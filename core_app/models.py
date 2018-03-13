from django.utils.translation import ugettext_lazy as _
from core_app.model_mixins import *
from slock.models import BasicUser
from paybills.models import Service
from django.db import models
from datetime import datetime

class Organization(models.Model):
    name     = models.CharField(null=True,
    blank=False, verbose_name=_("Name"),  max_length=256)
    expiration = models.DateTimeField(blank=True, null=True)

    owner = models.ForeignKey('User', null=True, 
    related_name='owned_organizations', blank=True)
    created = models.DateTimeField(auto_now=True, null=True)

class OrganizationService(Service):
    """
    Fill here with basic  info 
    about the product that has to be sent
    to paypal.
    """

    max_organizations = models.IntegerField(
    null=True, default=15)

    max_users = models.IntegerField(
    null=True, default=15)

    name = models.CharField(null=True, default='Paid BasicService',
    blank=False, max_length=256)

    paid = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.name

class Invite(models.Model):
    # email = models.EmailField(max_length=70, 
    # null=True, blank=False)

    user = models.ForeignKey('core_app.User', null=True, blank=True)

    # should have a count to avoid mail spam.
    token = models.CharField(null=True,
    blank=False, max_length=256)

    organization = models.ForeignKey('Organization', 
    null=True, blank=True)

class User(UserMixin, BasicUser):
    recover_email = models.EmailField(max_length=70, 
    null=True, blank=False, unique=True)

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

    # This field will be checked when user attempts to create
    # organization/add members to the organization.
    service = models.ForeignKey(
    'paybills.Service', null=True, blank=True)

    description = models.TextField(null=True,
    blank=False, verbose_name=_("Description"), 
    help_text='Position, Skills, Goals, ..', 
    max_length=256)

    avatar = models.ImageField(default='user.png',
    verbose_name='Your avatar.', help_text='', blank=False)

    enabled = models.BooleanField(blank=True, default=False)

    # default for expiration...
    # default=datetime.date.today() + datetime.timedelta(0)
    expiration = models.DateField(null=True)

    def __str__(self):
        return self.name

class Event(EventMixin, models.Model):
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

class Tag(models.Model):
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

class GlobalFilter(GlobalFilterMixin, models.Model):
    CHOICES = (
        ('P', 'Posts'),
        ('C', 'Cards'),
    )

    pattern  = models.CharField(max_length=255, blank=True, 
    default='', help_text='client socket  + #apollo + engine + #bug ...')

    organization = models.ForeignKey('core_app.Organization', 
    blank=True, null=True)

    user = models.ForeignKey('core_app.User', null=True, 
    blank=True)

    done = models.BooleanField(blank=True, 
    default=False, help_text='Done cards/posts?.')

    class Meta:
        unique_together = ('user', 'organization', )

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

class GlobalTaskFilter(models.Model):
    pattern  = models.CharField(max_length=255, blank=True, 
    default='', help_text='Example: ignition mechanism  \
    + #issue + #car ...')

    organization = models.ForeignKey('core_app.Organization', 
    blank=True, null=True)

    user = models.ForeignKey('core_app.User', null=True, 
    blank=True)

    done = models.BooleanField(blank=True, 
    default=False, help_text='Done cards/posts?.')

    class Meta:
        unique_together = ('user', 'organization', )

class Clipboard(GlobalFilterMixin, models.Model):
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



