import pytz

from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render, redirect

class FixTimezone(MiddlewareMixin):
    def process_request(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        # timezone.deactivate()

