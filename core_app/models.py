from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import FileSystemStorage
from slock.models import BasicUser
from django.db import models
from datetime import datetime
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from sqlike.parser import SqLike, SqNode
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from onesignal.models import Device, GroupSignal
from storages.backends.s3boto3 import S3Boto3Storage
from urllib.parse import urlparse
import random
import hmac

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
        sqlike = SqLike(cls, SqNode(None, default),
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

    def __str__(self):
        return self.name

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
        devices = devices.values_list('id', flat=True)
    
        # Attempt to send message just if there is
        # any user related to the event.
        if devices.count() > 0:
            self.send_onesignal(devices)

    def send_onesignal(self, devices):
        """ 
        Could be overriden to customize messages.
        """

        msg = ('Activity from {user}!').format(user=self.user.name)

        data = {'heading': {'en': 'Arcamens'},
        "contents": {"en": msg}}

        self.push(data, devices)

    def seen(self, user):
        """
        """

        self.users.remove(user)
        self.signers.add(user)
        self.save(hcache=False)

class EShoutMixin(models.Model):
    class Meta:
        abstract = True

    def send_onesignal(self, devices):
        msg = ('{user} shouts: {msg}!').format(
        user=self.user.name, msg=self.msg)

        data = {'heading': {'en': 'Arcamens'},
        "contents": {"en": msg}}

        self.push(data, devices)

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
        self.invite_url), 'noreply@arcamens.com', [self.user.email], 
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

        sqlike = SqLike(cls, SqNode(None, default))
        return sqlike

class Node(models.Model):
    """    
    """

    indexer = models.AutoField(primary_key=True)

class Membership(models.Model):
    """    
    """
    user = models.ForeignKey('User', 
    null=True, related_name='user_membership')

    organization = models.ForeignKey('Organization', null=True)

    inviter = models.ForeignKey('core_app.User', 
    null=True, related_name='admin_membership')

    admin   = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, null=True)

class Organization(OrganizationMixin):
    name = models.CharField(null=False,
    blank=False, verbose_name=_("Name"),  max_length=100)

    expiration = models.DateTimeField(blank=True, null=True)

    owner = models.ForeignKey('User', null=True, 
    related_name='owned_organizations', blank=True)

    created = models.DateTimeField(auto_now_add=True, null=True)

class Invite(InviteMixin):
    # email = models.EmailField(max_length=70, 
    # null=True, blank=False)
    user = models.ForeignKey('core_app.User', 
    null=False, related_name='invites')

    peer = models.ForeignKey('core_app.User', null=False, 
    related_name='sent_invites')

    # should have a count to avoid mail spam.
    token = models.CharField(null=False, blank=False, max_length=256)
    invite_url = models.CharField(null=False, blank=False, max_length=256)

    organization = models.ForeignKey('Organization', 
    null=False, related_name='invites')

    created = models.DateTimeField(auto_now_add=True, null=False)

class UserTagship(models.Model):
    """    
    """
    user = models.ForeignKey('core_app.User', null=True, 
    related_name='user_tagship', blank=True)

    tag = models.ForeignKey('core_app.Tag', null=True, blank=True)

    tagger = models.ForeignKey('core_app.User', null=True, 
    related_name='user_taggership', blank=True)

    created  = models.DateTimeField(auto_now_add=True, null=True)

class User(UserMixin, BasicUser):
    organizations = models.ManyToManyField('Organization', 
    related_name='users', through=Membership, symmetrical=False,
    through_fields=('user', 'organization'))

    tags = models.ManyToManyField('Tag', through=UserTagship,
    through_fields=('user', 'tag'), related_name='users', symmetrical=False)

    default = models.ForeignKey('Organization',
    null=True, on_delete=models.SET_NULL)

    description = models.CharField(null=True,
    blank=False, verbose_name=_("Bio"), 
    help_text='Example: Software Enginer, Rainbow hunter.', 
    max_length=256)

    avatar = models.ImageField(null=True,
    verbose_name='Your avatar.', help_text='', blank=True)

    enabled = models.BooleanField(default=False)

    c_storage   = models.IntegerField(null=False, default=0)
    c_download = models.IntegerField(null=False, default=0)

    # default for expiration...
    # default=datetime.date.today() + datetime.timedelta(0)
    max_users  = models.IntegerField(null=False, default=3)
    paid       = models.BooleanField(null=False, default=False)
    expiration = models.DateField(null=True)

class Event(EventMixin):
    users = models.ManyToManyField('core_app.User',   
    related_name='events', symmetrical=False)

    organization = models.ForeignKey('Organization', 
    related_name='events', null=True)

    # created = models.DateTimeField(auto_now=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=False)
    user    = models.ForeignKey('core_app.User', null=True)

    signers = models.ManyToManyField('core_app.User', 
    related_name='seen_events', symmetrical=False)

    html = models.TextField(null=True, blank=False)
    html_template = None

    def __str__(self):
        return 'Event'

class Tag(TagMixin):
    name = models.CharField(null=False, blank=False, max_length=100)

    description = models.CharField(null=True, blank=False, 
    default='...', max_length=256)

    # When the organization is deleted all its tags
    # are deleted too.
    organization = models.ForeignKey('core_app.Organization',
    related_name='tags', null=False)

    class Meta:
        unique_together = ('name', 'organization')

class EInviteUser(Event):
    peer = models.ForeignKey('User', null=False, 
    related_name='e_invite_user0')
    html_template = 'core_app/e-invite-user.html'

class EShout(EShoutMixin, Event):
    msg = models.CharField(null=False,
    blank=False, verbose_name=_("Msg"),  max_length=256,
    help_text="No pain no gain!")
    html_template = 'core_app/e-shout.html'

class EJoinOrganization(Event):
    peer = models.ForeignKey('User', null=False, 
    related_name='e_join_organization0')
    html_template = 'core_app/e-join-organization.html'

class EBindUserTag(Event):
    peer = models.ForeignKey('User', null=False, 
    related_name='e_bind_user_tag0')

    tag = models.ForeignKey('Tag', null=False)
    html_template = 'core_app/e-bind-user-tag.html'

class ECreateTag(Event):
    tag = models.ForeignKey('Tag', null=False, 
    related_name='e_create_tag1')
    html_template = 'core_app/e-create-tag.html'

class EDeleteTag(Event):
    tag_name = models.CharField(null=False, max_length=256)
    html_template = 'core_app/e-delete-tag.html'

class EUnbindUserTag(Event):
    peer = models.ForeignKey('User', null=False, 
    related_name='e_unbind_user_tag0')

    tag = models.ForeignKey('Tag', null=False)
    html_template = 'core_app/e-unbind-user-tag.html'

class UserFilter(models.Model):
    organization = models.ForeignKey('core_app.Organization', 
    blank=True, default='')

    pattern  = models.CharField(max_length=255, blank=True, default='',
    help_text='Example: oliveira@arcamens.com')

    user = models.ForeignKey('core_app.User', null=False)

    # It warrants there will exist only one user and organization
    # filter. If we decide to permit more filters..
    class Meta:
        unique_together = ('user', 'organization',)

class Clipboard(models.Model):
    organization = models.ForeignKey('core_app.Organization', null=False)

    user  = models.ForeignKey('core_app.User', null=False)
    posts = models.ManyToManyField('post_app.Post', 
    related_name='post_clipboard_users', symmetrical=False)

    cards = models.ManyToManyField('card_app.Card', 
    related_name='card_clipboard_users', symmetrical=False)

    lists = models.ManyToManyField('list_app.List', 
    related_name='list_clipboard_users', symmetrical=False)

    class Meta:
        unique_together = ('user', 'organization')

class EUpdateOrganization(Event):
    html_template = 'core_app/e-update-organization.html'

class ERemoveOrganizationUser(Event):
    peer = models.ForeignKey('User', null=False, 
    related_name='e_remove_organization_user0')

    reason = models.CharField(null=False, default='',
    blank=True, max_length=256)

    html_template = 'core_app/e-remove-organization-user.html'

class NodeFilter(models.Model):
    pattern = models.CharField(max_length=255, blank=True, 
    default='', help_text='/projectname/', )

    user = models.ForeignKey('core_app.User', null=False)

    organization = models.ForeignKey('core_app.Organization', null=False)
    status = models.BooleanField(blank=True, default=False, 
    help_text='Filter On/Off.')

    # It warrants there will exist only one user and organization
    # filter. If we decide to permit more filters..
    class Meta:
        unique_together = ('user', 'organization',)

class EventFilter(models.Model):
    start = models.DateField(null=True, default=datetime.now, blank=False)
    end   = models.DateField(null=True, default=datetime.now, blank=False)

    user = models.ForeignKey('core_app.User', null=False)

    organization = models.ForeignKey('core_app.Organization', null=False)

    # It warrants there will exist only one user and organization
    # filter. If we decide to permit more filters..
    class Meta:
        unique_together = ('user', 'organization',)

class EDisabledAccount(Event):
    reason = models.CharField(max_length=255, 
    blank=True, default = '')

    html_template = 'core_app/e-disabled-account.html'


class StorageMixin:
   def generate_filename(self, filename):
       v = 'storage ' + str(datetime.now().timestamp())+'/'+str(random.SystemRandom())
       dir = hmac.new(settings.SECRET_KEY.encode(), v.encode()).hexdigest()
       return '%s/%s-%s' % (dir, timezone.now(), filename)

class AmazonStorage(StorageMixin, S3Boto3Storage):
    pass

class LocalStorage(StorageMixin, FileSystemStorage):
    pass







