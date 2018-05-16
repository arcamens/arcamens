from django.db import models
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
import random

# Create your models here.
class GroupSignal(models.Model):
    class Meta:
        abstract = True

    def dispatch(self, notification, exclude=[]):
        message = notification.fmt_message()

    def push(self, devices=[]):
        pass

class Notification:
    def fmt_message(self):
        pass

class Device(models.Model):
    onesignal_id = models.CharField(null=True, blank=True, max_length=256)

    class Meta:
        abstract = True

    def init_onesignal(self):
        context = {
        'ONE_SIGNAL_APPID': settings.ONE_SIGNAL_APPID, 
        'device_id':  self.id}

        tmp     = get_template('onesignal/init_onesignal.html')
        html    = tmp.render(context)
        return html

