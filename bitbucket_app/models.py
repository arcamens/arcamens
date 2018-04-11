from django.utils.translation import ugettext_lazy as _
from slock.models import BasicUser
from core_app.models import Event
from core_app.model_mixins import UserMixin
from django.db import models
import json

class BitbucketMixin(UserMixin):
    pass

class BitbucketHooker(BitbucketMixin, BasicUser):
    """
    Service interactions should be modeled using BasicUser class
    with concreate inheritance. 

    An addon that integrates with an extern service acts pretty 
    much like an user. 

    It generates events, create posts, cards etc. 
    It is pretty much like a robot.

    Note: I have to make it disabled for login.
    """

    # name = models.CharField(null=True, blank=False, 
    # default='Bitbucket Service', max_length=626)

    repo_url = models.CharField(null=True, blank=False, 
    max_length=626)

class EBitbucketCommit(models.Model):
    author = models.CharField(null=True, blank=False, 
    max_length=626)

    message = models.CharField(null=True, blank=False, 
    max_length=626)

    url = models.CharField(null=True, blank=False, 
    max_length=626)

    note = models.OneToOneField('note_app.Note', null=True, 
    related_name='commit', blank=True)
    html_template = 'bitbucket_app/e-bitbucket-commit.html'



