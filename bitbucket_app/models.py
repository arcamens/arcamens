from django.utils.translation import ugettext_lazy as _
from core_app.models import User
from django.db import models
import json

class BitbucketHooker(models.Model):
    username = models.CharField(null=True, blank=False, 
    max_length=626)

    uuid = models.CharField(null=True, blank=False, 
    max_length=626)

class BitbucketCommit(models.Model):
    author = models.CharField(null=True, blank=False, 
    max_length=626)

    message = models.CharField(null=True, blank=False, 
    max_length=626)

    url = models.CharField(null=True, blank=False, 
    max_length=626)

    note = models.OneToOneField('mote_app.Note', null=True, 
    related_name='commit', blank=True)



