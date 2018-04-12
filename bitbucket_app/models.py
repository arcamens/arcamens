from django.utils.translation import ugettext_lazy as _
from slock.models import BasicUser
from core_app.models import Event
from core_app.model_mixins import UserMixin
from django.db import models
import json

class BitbucketHook(models.Model):
    """
    Service interactions should be modeled using user class
    with concreate inheritance. 

    An addon that integrates with an extern service acts pretty 
    much like an user. 

    It generates events, create posts, cards etc. 
    It is pretty much like a robot.

    Note: I have to make it disabled for login.
    """

    # name = models.CharField(null=True, blank=False, 
    # default='Bitbucket Service', max_length=626)
    addon = models.ForeignKey('core_app.User', null=True, blank=True,
    related_name='bitbucket_hooks')

    address = models.CharField(null=True, 
    help_text='Example: https://bitbucket.org/team/project/',
    blank=False, default='', max_length=626)

class EBitbucketCommit(Event):
    # Not sure if i should have abitbuckethooker 
    # foreignkey here. The user actor will
    # be the bitbucket addon.
    # We need to add commit_id too, for updating
    # in case the commit is deleted(not sure yet though).

    author = models.CharField(null=True, blank=False, 
    max_length=626)

    message = models.CharField(null=True, blank=False, 
    max_length=626)

    url = models.CharField(null=True, blank=False, 
    max_length=626)

    # card = models.ForeignKey('card_app.Card', null=True, blank=True,
    # related_name='bitbucket_commits')

    note = models.OneToOneField('note_app.Note', null=True, blank=True,
    related_name='commit')

    html_template = 'bitbucket_app/e-bitbucket-commit.html'





