from django.utils.translation import ugettext_lazy as _
from slock.models import BasicUser
from paybills.models import BasicItem
from django.db import models
from datetime import datetime
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from sqlike.parser import SqLike, SqNode
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from onesignal.models import Device, GroupSignal
from os.path import join
import random

class UserMixin(Device):
    class Meta:
        abstract = True

    def get_user_url(self):
        return reverse('core_app:user', 
        kwargs={'user_id': self.id})

    @classmethod
    def from_sqlike(cls):
        email = lambda ind: Q(email__icontains=ind)
        name  = lambda ind: Q(name__icontains=ind)
        desc  = lambda ind: Q(description__icontains=ind)
        tag   = lambda ind: Q(tags__name__icontains=ind)
        default = lambda ind: Q(email__icontains=ind) | Q(name__icontains=ind)
        sqlike = SqLike(SqNode(None, default),
        SqNode(('m', 'email'), email),
        SqNode(('n', 'name'), name), 
        SqNode(('t', 'tag'), tag, chain=True), 
        SqNode(('d', 'description'), desc),)
        return sqlike

    @classmethod
    def collect_users(cls, users, pattern):
        sqlike = cls.from_sqlike()
        sqlike.feed(pattern)
        users = sqlike.run(users)
        return users

    def n_acc_users(self):
        orgs    = self.owned_organizations.all()
        users   = self.__class__.objects.filter(organizations=orgs)
        n_users = users.count()
        return n_users

    def is_max_users(self):
        """
        Tells if owner account has achieved its limit of users
        in the account.
        """

        u_orgs       = self.owned_organizations.all()
        n_users      = User.objects.filter(organizations__in=u_orgs).distinct().count()
        n_invites    = Invite.objects.filter(organization__in=u_orgs).count()
        count        = n_users + n_invites
        return count >= self.max_users

    def __str__(self):
        return '%s %s' % (self.name, self.email)

class EventMixin(GroupSignal):
    class Meta:
        abstract = True

    def save(self, *args, hcache=True, **kwargs):
        super().save(*args, **kwargs)

        if hcache and self.html_template:
            self.create_html_cache()

    def create_html_cache(self):
        tmp       = get_template(self.html_template)
        self.html = tmp.render({'event': self})
        super().save()

    def dispatch(self, *args):
        # Assumes the action owner has
        # seen the event.

        self.users.add(*args)
        
        # The user has seen the event since he
        # has provoked it.
        self.signers.add(self.user)
        self.users.remove(self.user)

        devices = self.users.filter(default=self.organization)
        devices = devices.values_list('onesignal_id', flat=True)
        devices = list(devices)

        self.push('Arcamens Notification', 'An event occurred', devices)

    def seen(self, user):
        """
        """

        self.users.remove(user)
        self.signers.add(user)
        self.save(hcache=False)

class OrganizationMixin(models.Model):
    class Meta:
        abstract = True

    def __str__(self):
        return self.name

class InviteMixin(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.token  = 'invite%s' % random.randint(1000, 10000)

        invite_url = reverse('core_app:join-organization', kwargs={
        'organization_id': self.organization.id, 'token': self.token})

        self.invite_url = '%s%s' % (settings.LOCAL_ADDR, invite_url)
        super().save(*args, **kwargs)

    def send_email(self):
        msg = 'You were invited to %s by %s.' % (
        self.organization.name, self.peer.name)

        send_mail(msg, '%s %s' % (self.organization.name, 
        self.invite_url), 'noreply@splittask.net', [self.user.email], 
        fail_silently=False)

    def __str__(self):
        return '%s %s %s' % (self.user.name, 
            self.token, self.organization.name)

class TagMixin(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def from_sqlike(cls):
        default  = lambda ind: Q(name__icontains=ind) | Q(
        description__icontains=ind)

        sqlike = SqLike(SqNode(None, default))
        return sqlike

class Node(models.Model):
    """    
    """

    indexer = models.AutoField(primary_key=True)

class Organization(OrganizationMixin):
    name     = models.CharField(null=True,
    blank=False, verbose_name=_("Name"),  max_length=256)
    expiration = models.DateTimeField(blank=True, null=True)

    owner = models.ForeignKey('User', null=True, 
    related_name='owned_organizations', blank=True)
    created = models.DateTimeField(auto_now=True, null=True)

    admins = models.ManyToManyField(
    'User', related_name='managed_organizations', 
    null=True, blank=True, symmetrical=False)

class Period(BasicItem):
    """
    This is the product thats being purchased.
    """

    # The price should be calculated taking into account
    # User.expiration and current User.max_users attrs.
    price = models.IntegerField(null=True, default=0)

    # This is the max number of users that our customer
    # will purchase for a period of time. There is a difference
    # between current number of users and max_users. If the customer
    # attempt to add more users to his account than the max then he is
    # asked to upgrade his limits. This way i think we may be able
    # to implement subscription.
    max_users = models.IntegerField(null=True, default=3,
    help_text="Max users until the expiration.")

    expiration = models.DateField(null=True, 
    blank=False, help_text="Example: year-month-day")

    total = models.FloatField(null=True, default=0)
    paid  = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return ('Paid: {paid}' 
        'Price: {price}' 
        'Expiration: {expiration}' 
        'Max Users: {max_users}').format(paid=self.paid, 
            price=self.price, expiration=self.expiration, 
                max_users=self.max_users)

class Invite(InviteMixin):
    # email = models.EmailField(max_length=70, 
    # null=True, blank=False)
    user = models.ForeignKey('core_app.User', null=True, 
    blank=True, related_name='invites')

    peer = models.ForeignKey('core_app.User', null=True, 
    blank=True, related_name='sent_invites')

    # should have a count to avoid mail spam.
    token = models.CharField(null=True,
    blank=False, max_length=256)

    invite_url = models.CharField(null=True,
    blank=False, max_length=256)

    organization = models.ForeignKey('Organization', 
    null=True, blank=True, related_name='invites')
    created = models.DateTimeField(auto_now=True, null=True)

class User(UserMixin, BasicUser):
    organizations = models.ManyToManyField(
    'Organization', related_name='users', 
    null=True, blank=True, symmetrical=False)

    tags = models.ManyToManyField(
    'Tag', related_name='users', 
    null=True, blank=True, symmetrical=False)

    # post_clipboard = models.ManyToManyField(
    # 'post_app.Post', null=True, blank=True, 
    # related_name='post_clipboard_users', symmetrical=False)

    # contacts  = models.ManyToManyField('self', 
    # related_name='users', null=True, blank=True, symmetrical=False)
    default = models.ForeignKey('Organization', 
    null=True, blank=True)

    description = models.TextField(null=True,
    blank=False, verbose_name=_("Description"), 
    help_text='Position, Skills, Goals, ..', 
    max_length=256)

    avatar = models.ImageField(null=True,
    verbose_name='Your avatar.', help_text='', blank=False)

    enabled = models.BooleanField(blank=True, default=False)

    # default for expiration...
    # default=datetime.date.today() + datetime.timedelta(0)
    max_users  = models.IntegerField(null=True, default=3)
    paid       = models.BooleanField(blank=True, default=False)
    expiration = models.DateField(null=True)

class Event(EventMixin):
    users = models.ManyToManyField('core_app.User', null=True,  
    related_name='events', blank=True, symmetrical=False)

    organization = models.ForeignKey('Organization', 
    related_name='events', null=True, blank=True)

    # created = models.DateTimeField(auto_now=True, null=True)
    created = models.DateTimeField(auto_now=True, null=True)

    user = models.ForeignKey('core_app.User', null=True, blank=True)

    signers = models.ManyToManyField('core_app.User', null=True,  
    related_name='seen_events', blank=True, symmetrical=False)

    html = models.TextField(null=True, blank=False)
    html_template = None

    def __str__(self):
        return 'Event'

class Tag(TagMixin):
    name = models.CharField(null=True,
    blank=False, max_length=256)

    description = models.CharField(null=True,
    blank=False, max_length=256)

    # When the organization is deleted all its tags
    # are deleted too.
    organization = models.ForeignKey('core_app.Organization',
    related_name='tags', null=True, blank=True)

class EInviteUser(Event):
    peer = models.ForeignKey('User', null=True, 
    related_name='e_invite_user0', blank=True)
    html_template = 'core_app/e-invite-user.html'

class EShout(Event):
    msg = models.CharField(null=True,
    blank=False, verbose_name=_("Msg"),  max_length=256,
    help_text="No pain no gain!")
    html_template = 'core_app/e-shout.html'

class EJoinOrganization(Event):
    peer = models.ForeignKey('User', null=True, 
    related_name='e_join_organization0', blank=True)
    html_template = 'core_app/e-join-organization.html'

class EBindUserTag(Event):
    peer = models.ForeignKey('User', null=True, 
    related_name='e_bind_user_tag0', blank=True)
    tag = models.ForeignKey('Tag', null=True, blank=True)
    html_template = 'core_app/e-bind-user-tag.html'

class ECreateTag(Event):
    tag = models.ForeignKey('Tag', null=True, 
    related_name='e_create_tag1', blank=True)
    html_template = 'core_app/e-create-tag.html'

class EDeleteTag(Event):
    tag_name = models.CharField(null=True,
    blank=False, max_length=256)
    html_template = 'core_app/e-delete-tag.html'

class EUnbindUserTag(Event):
    peer = models.ForeignKey('User', null=True, 
    related_name='e_unbind_user_tag0', blank=True)
    tag = models.ForeignKey('Tag', null=True, blank=True)
    html_template = 'core_app/e-unbind-user-tag.html'


class UserFilter(models.Model):
    organization = models.ForeignKey('core_app.Organization', 
    blank=True, default='')

    pattern  = models.CharField(max_length=255, blank=True, default='',
    help_text='Example: victor + #arcamens + #suggestion ...')

    user = models.ForeignKey('core_app.User', 
    null=True, blank=True)

    # It warrants there will exist only one user and organization
    # filter. If we decide to permit more filters..
    class Meta:
        unique_together = ('user', 'organization',)

class Clipboard(models.Model):
    organization = models.ForeignKey(
    'core_app.Organization', blank=True)

    user = models.ForeignKey('core_app.User', blank=True)

    posts = models.ManyToManyField(
    'post_app.Post', null=True, blank=True, 
    related_name='post_clipboard_users', symmetrical=False)

    cards= models.ManyToManyField(
    'card_app.Card', related_name='card_clipboard_users', 
    null=True, blank=True, symmetrical=False)

    lists = models.ManyToManyField(
    'list_app.List', related_name='list_clipboard_users', 
    null=True, blank=True, symmetrical=False)

    class Meta:
        unique_together = ('user', 'organization')

class EUpdateOrganization(Event):
    html_template = 'core_app/e-update-organization.html'

class ERemoveOrganizationUser(Event):
    peer = models.ForeignKey('User', null=True, 
    related_name='e_remove_organization_user0', blank=True)

    reason = models.CharField(null=True, default='',
    blank=True, max_length=256)

    html_template = 'core_app/e-remove-organization-user.html'

class NodeFilter(models.Model):
    pattern = models.CharField(max_length=255, blank=True, 
    default='')

    user         = models.ForeignKey('core_app.User', null=True, blank=True)
    organization = models.ForeignKey('core_app.Organization', 
    blank=True, null=True)

    status = models.BooleanField(blank=True, default=False, 
    help_text='Filter On/Off.')

    # It warrants there will exist only one user and organization
    # filter. If we decide to permit more filters..
    class Meta:
        unique_together = ('user', 'organization',)

class EDisabledAccount(Event):
    reason = models.CharField(max_length=255, 
    blank=True, default = '')

    html_template = 'core_app/e-disabled-account.html'






