from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from slock.models import BasicUser
from paybills.models import Service
from core_app.utils import search_tokens
from functools import reduce
import operator

import datetime

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


class UserMixin(object):
    def get_user_url(self):
        return reverse('core_app:user', 
        kwargs={'user_id': self.id})

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

    post_clipboard = models.ManyToManyField(
    'post_app.Post', null=True, blank=True, 
    related_name='post_clipboard_users', symmetrical=False)

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

    avatar = models.ImageField( null=True,
    default='user.png',verbose_name='Your avatar.', help_text='', blank=True)

    enabled = models.BooleanField(blank=True, default=False)

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
    organization = models.ForeignKey('core_app.Organization',
    related_name='tags', null=True, blank=True)


class EInviteUser(Event):
    peer = models.ForeignKey('User', null=True, 
    related_name='e_invite_user0', blank=True)

    def get_absolute_url(self):
        return reverse('core_app:e-invite-user', 
        kwargs={'event_id': self.id})

class EJoinOrganization(Event):
    peer = models.ForeignKey('User', null=True, 
    related_name='e_join_organization0', blank=True)

    def get_absolute_url(self):
        return reverse('core_app:e-join-organization', 
        kwargs={'event_id': self.id})

class EBindUserTag(Event):
    peer = models.ForeignKey('User', null=True, 
    related_name='e_bind_user_tag0', blank=True)
    tag = models.ForeignKey('Tag', null=True, blank=True)

    def get_absolute_url(self):
        return reverse('core_app:e-bind-user-tag', 
        kwargs={'event_id': self.id})

class EUnbindUserTag(Event):
    peer = models.ForeignKey('User', null=True, 
    related_name='e_unbind_user_tag0', blank=True)
    tag = models.ForeignKey('Tag', null=True, blank=True)

    def get_absolute_url(self):
        return reverse('core_app:e-unbind-user-tag', 
        kwargs={'event_id': self.id})


class GlobalFilterMixin:
    def collect_cards(self, cards, filter):
        cards = cards.filter(done=filter.done)

        chks, tags = search_tokens(filter.pattern)

        for ind in tags:
            cards = cards.filter(Q(tags__name__startswith=ind))

        cards = cards.filter(reduce(operator.and_, 
        (Q(label__contains=ind) | Q(owner__name__contains=ind) 
        for ind in chks))) if chks else cards

        return cards

    def collect_posts(self, posts, filter):
        chks, tags = search_tokens(filter.pattern)

        for ind in tags:
            posts = posts.filter(Q(tags__name__startswith=ind))

        # I should make post have owner instead of user.
        posts = posts.filter(reduce(operator.and_, 
        (Q(label__contains=ind) | Q(user__name__contains=ind) 
        for ind in chks))) if chks else posts

        posts = posts.filter(Q(done=filter.done))
        return posts

class GlobalFilter(GlobalFilterMixin, models.Model):
    pattern      = models.CharField(max_length=255, blank=True, default='', null=True)
    user         = models.ForeignKey('core_app.User', null=True, blank=True)
    organization = models.ForeignKey('core_app.Organization', blank=True,
    null=True)

    user = models.ForeignKey('core_app.User', 
    null=True, blank=True)
    organization = models.ForeignKey('core_app.Organization', 
    null=True, blank=True)

    done = models.BooleanField(blank=True, 
    default=False, help_text='Done cards?.')

    class Meta:
        unique_together = ('user', 'organization', )











