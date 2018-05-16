from django.views.generic import View
from django.shortcuts import render
from django.http import HttpResponse
from onesignal.models import SignalToken

# Create your views here.
class UpdateUuid(View):
    def get(self, request, token, uuid):
        token = SignalToken.objects.get(token=token)
        token.device.uuid = uuid
        token.device.save()

        return HttpResponse(statu=200)
