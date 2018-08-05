from django.core.management import BaseCommand
from core_app.models import User, Organization
from board_app.models import Board, Boardship
from group_app.models import Group, Groupship

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

        boards     = Board.objects.filter(organization=organization)
        boardships = (Boardship(member=user, board=ind, 
        binder=user) for ind in boards)

        Boardship.objects.bulk_create(boardships)

        groups     = Group.objects.filter(organization=organization)
        groupships = (Groupship(user=user, group=ind, 
        binder=user) for ind in groups)
        Groupship.objects.bulk_create(groupships)

        self.stdout.write('User binded to all boards/groups!')
    
    




