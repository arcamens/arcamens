from django.core.management import BaseCommand
from core_app.models import User, Organization
from board_app.models import Board
from timeline_app.models import Timeline

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('owner-email', type=str)
        parser.add_argument('organization-name', type=str)
        parser.add_argument('user-email', type=str)

    def handle(self, *args, **kwargs):
        organization = Organization.objects.get(
            owner__email__istartswith=kwargs['owner-email'], 
                name__istartswith=kwargs['organization-name'])

        user = User.objects.get(email__istartswith=kwargs['user-email'])
        user.organizations.add(organization)

        for ind in Board.objects.filter(organization=organization):
           ind.set_ownership(user)
        
        for ind in Timeline.objects.filter(organization=organization):
           ind.set_ownership(user)
        
        self.stdout.write('User binded to all boards/timelines!')
    
    



