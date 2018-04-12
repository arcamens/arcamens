from django.utils.translation import ugettext_lazy as _
from slock.models import BasicUser
from core_app.models import Event
from wsbells.models import UserWS, QueueWS
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

    organization = models.ForeignKey('core_app.Organization', null=True, blank=True,
    related_name='bitbucket_hooks')

    address = models.CharField(null=True, 
    help_text='Example: https://bitbucket.org/team/project/',
    blank=False, default='', max_length=626)

class EBitbucketCommit(UserWS, Event):
    # Not sure if i should have abitbuckethooker 
    # foreignkey here. The user actor will
    # be the bitbucket addon.
    # We need to add commit_id too, for updating
    # in case the commit is deleted(not sure yet though).
    hook = models.ForeignKey('BitbucketHook', null=True, blank=True)

    url = models.CharField(null=True, blank=False, 
    max_length=626)

    note = models.OneToOneField('note_app.Note', null=True, blank=True,
    related_name='commit')

    html_template = 'bitbucket_app/e-bitbucket-commit.html'






