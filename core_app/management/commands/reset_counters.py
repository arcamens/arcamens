from django.core.management import BaseCommand
from core_app.models import User
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        users = User.objects.filter(enabled=True)
        users.update(c_storage=0, c_download=0)
        self.stdout.write('Counters were reseted!')
    

    








