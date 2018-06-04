from django.core.management import BaseCommand
from core_app.models import Event

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        children = Event.__subclasses__()
        for ind in children:
            for ind in ind.objects.all():
                ind.create_html_cache()
        self.stdout.write('Events updated!')
    
    
