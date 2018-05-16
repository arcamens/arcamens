from django.db import models
from django.http import HttpResponse
from django.template.loader import get_template
from requests.exceptions import HTTPError
from onesignalclient.app_client import OneSignalAppClient
from onesignalclient.notification import Notification
from django.conf import settings
import random

# Create your models here.
class GroupSignal(models.Model):
    class Meta:
        abstract = True

    def push(self, title, message, devices=[]):
        client = OneSignalAppClient(app_id=settings.ONE_SIGNAL_APPID, 
        app_api_key=settings.ONE_SIGNAL_API_KEY)

        notification = Notification(settings.ONE_SIGNAL_APPID, 
        Notification.DEVICES_MODE)

        notification.include_player_ids = devices

        notification.contents = {'en': message }
        notification.headings = {'en': title}

        try:
            client.create_notification(notification)
        except HTTPError as excpt:
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


