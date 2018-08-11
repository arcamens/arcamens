from django.core.management import BaseCommand
from site_app.models import RegisterProcess
from datetime import timedelta
from django.conf import settings
from django.db.models import Q, F

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        delta = timedelta(days=settings.SIGNUP_EXP)
        query = Q(created__gte=F('created') + delta)
        RegisterProcess.objects.filter(query).delete()
        self.stdout.write('Released emails!')
    
