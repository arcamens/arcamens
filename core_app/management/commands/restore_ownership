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

        boards = Board.objects.filter(organization=organization)
        for ind in boards:
           ind.members.add(user)
        
        timelines = Timeline.objects.filter(organization=organization)
        for ind in timelines:
           ind.users.add(user)
        
        self.stdout.write('User binded to all boards/timelines!')
    
    


