from django.utils.translation import ugettext_lazy as _
from django.db import models
import json

class BitbucketHooker(models.Model):
    username = models.CharField(null=True, blank=False, 
    max_length=626)

    uuid = models.CharField(null=True, blank=False, 
    max_length=626)



