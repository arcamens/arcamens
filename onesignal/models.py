from django.db import models
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
import requests
import random
import json

# Create your models here.
class GroupSignal(models.Model):
    class Meta:
        abstract = True


    def push(self, data, devices):
        devices = list(devices)
        SIZE    = 99

        groups  = [devices[ind * SIZE:(ind + 1) * SIZE] 
            for ind in range(0, len(devices)//SIZE + 1)]

        auth    = "Basic %s" % settings.ONE_SIGNAL_API_KEY

        headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": auth}

        for ind in groups:
            self.post(data, ind, headers)

    def post(self, data, devices, headers):
        url = 'https://onesignal.com/api/v1/notifications'
        targets = []

        # targets = [{"field": "tag", "key": "device_id", 
        # "relation": "=", 'value':'device-%s' % ind } for ind in devices]

        for ind in range(0, len(devices) - 1):
            targets.extend(({"field": "tag", "relation": "=", 'key': 'device_id', 
                'value':'device-%s' % devices[ind] }, {'operator':'OR'}))

        targets.append({"field": "tag", "relation": "=", 'key': 'device_id',
                'value':'device-%s' % devices[-1]})

        payload = {
        'app_id': settings.ONE_SIGNAL_APPID, 
        "filters": targets}

        payload.update(data)
        req = requests.post(url, data=json.dumps(payload), headers=headers)

class Device(models.Model):
    class Meta:
        abstract = True

    def init_onesignal(self):
        context = {
        'ONE_SIGNAL_APPID': settings.ONE_SIGNAL_APPID, 
        'device_id':  self.id}

        tmp     = get_template('onesignal/init_onesignal.html')
        html    = tmp.render(context)
        return html




