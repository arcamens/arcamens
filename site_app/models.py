from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

class PasswordTicket(models.Model):
    token = models.CharField(null=True,
    blank=False, max_length=256)

    user = models.ForeignKey('core_app.User', null=True, 
    related_name='password_tickets', blank=True)

    # expiration = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now=True, null=True)

