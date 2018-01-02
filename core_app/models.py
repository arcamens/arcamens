from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from paybills.models import Service
import datetime

class Organization(models.Model):
    name     = models.CharField(null=True,
    blank=False, verbose_name=_("Name"),  max_length=256)
    expiration = models.DateTimeField(blank=True, null=True)

    owner = models.ForeignKey('User', null=True, 
    related_name='owned_organizations', blank=True)
    created = models.DateTimeField(auto_now=True, null=True)

class UserMixin(object):
    def get_user_url(self):
        return reverse('core_app:user', 
        kwargs={'user_id': self.id})

    def __str__(self):
        return self.name

class Invite(models.Model):
    email = models.EmailField(max_length=70, 
    null=True, blank=False)

    # should have a count to avoid mail spam.
    token = models.CharField(null=True,
    blank=False, max_length=256)

    organization = models.ForeignKey('Organization', 
    null=True, blank=True)

class User(UserMixin, models.Model):
    name = models.CharField(null=True,
    blank=False, verbose_name=_("Name"), 
    help_text='User Name', max_length=256)

    email = models.EmailField(max_length=70, 
    null=True, blank=False, unique=True)

    organizations = models.ManyToManyField(
    'Organization', related_name='users', 
    null=True, blank=True, symmetrical=False)

    tags = models.ManyToManyField(
    'Tag', related_name='users', 
    null=True, blank=True, symmetrical=False)

    clipboard = models.ManyToManyField(
    'timeline_app.Clipboard', null=True, blank=True, symmetrical=False)

    # contacts  = models.ManyToManyField('self', 
    # related_name='users', null=True, blank=True, symmetrical=False)
    default = models.ForeignKey('Organization', 
    null=True, blank=True)

    # This field will be checked when user attempts to create
    # organization/add members to the organization.
    service = models.ForeignKey(
    'paybills.Service', null=True, blank=True)

    password = models.CharField(null=True,
    blank=False, verbose_name=_("Password"), 
    help_text='Password', max_length=256)

    description = models.TextField(null=True,
    blank=False, verbose_name=_("Description"), 
    help_text='Position, Skills, Goals, ..', 
    max_length=256)

    avatar = models.ImageField(upload_to='media/', null=True,
    default='user.png',verbose_name='', help_text='', blank=True)

    enabled = models.BooleanField(blank=True, default=True)

    # default for expiration...
    # default=datetime.date.today() + datetime.timedelta(0)
    expiration = models.DateField(null=True, blank=False)

    card_clipboard = models.ManyToManyField(
    'card_app.Card', related_name='card_clipboard_users', 
    null=True, blank=True, symmetrical=False)

    list_clipboard = models.ManyToManyField(
    'list_app.List', related_name='list_clipboard_users', 
    null=True, blank=True, symmetrical=False)

    def __str__(self):
        return self.name

class Event(models.Model):
    users = models.ManyToManyField('core_app.User', null=True,  
    related_name='events', blank=True, symmetrical=False)

    organization = models.ForeignKey('Organization', 
    related_name='events', null=True, blank=True)

    created = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey('core_app.User', null=True, blank=True)

    def __str__(self):
        return 'Event'

class Tag(models.Model):
    name = models.CharField(null=True,
    blank=False, max_length=256)

    description = models.CharField(null=True,
    blank=False, max_length=256)

    # When the organization is deleted all its tags
    # are deleted too.
    organization = models.ForeignKey(
    'core_app.Organization', related_name='tags',
    null=True, blank=True)


class EInviteUser(Event):
    peer = models.ForeignKey('User', null=True, 
    related_name='e_invite_user0', blank=True)

    def get_absolute_url(self):
        return reverse('core_app:e-invite-user', 
        kwargs={'event_id': self.id})



