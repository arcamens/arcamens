import json

from django.core.management.base import BaseCommand
from core_app.models import User, Organization, Membership, Node
from board_app.models import Board, Boardship, ECreateBoard
from group_app.models import Group, Groupship
from list_app.models import List, ECreateList
from card_app.models import Card, ECreateCard
from post_app.models import Post, ECreatePost


class Command(BaseCommand):
    help = 'Custom import for boards/groups.'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)
        parser.add_argument('user-email', type=str)

    def handle(self, *args, **kwargs):
        fd   = open(kwargs['file'], 'r')
        data = json.load(fd)
        fd.close()

        user = User.objects.get(email=kwargs['user-email'])
        organization = Organization.objects.get(name=data['name'])

        # Membership.objects.create(user=user, status='0',
        # organization=organization, inviter=user)

        self.load_boards(organization, user, data['elems']['boards'])
        self.load_groups(organization, user, data['elems']['groups'])

    def load_boards(self, organization, user, boards):
        # Could use bulkcreate.
        for ind in boards:
            board = Board.objects.create(
            owner=user,  name=ind['name'], description=ind['description'], 
            organization=organization, node=Node.objects.create())
            boardship = Boardship.objects.create(member=user, 
            board=board, binder=user, status='0')
            event = ECreateBoard.objects.create(organization=organization,
            board=board, user=user)
            event.dispatch(user)
            event.save()
    
            self.load_lists(organization, user, board, ind['lists'])

    def load_lists(self, organization, user, board, lists):
        for ind in lists:
            list = List.objects.create(owner=user, 
                name=ind['name'], ancestor=board)
            event = ECreateList.objects.create(organization=organization,
            ancestor=board, child=list, user=user)
            event.dispatch(user)
            self.load_cards(organization, user, board, list, ind['cards'])

    def load_cards(self, organization, user, board, list, cards):
        for ind in cards:
            card = Card.objects.create(owner=user, ancestor=list,
                label=ind['label'], data=ind['data'])
            event = ECreateCard.objects.create(organization=organization,
            ancestor=list, board=board, card=card, user=user)
            event.dispatch(user)
    
    def load_groups(self, organization, user, groups):
        for ind in groups:
            group = Group.objects.create(owner=user, 
                organization=organization, name=ind['name'], 
                    description=ind['description'], node=Node.objects.create())
            groupship = Groupship.objects.create(user=user, 
            group=group, binder=user, status='0')
            self.load_posts(organization, user, group, ind['posts'])

    def load_posts(self, organization, user, group, posts):
        for ind in posts:
            post = Post.objects.create(owner=user, ancestor=group,
                label=ind['label'], data=ind['data'])
            event = ECreatePost.objects.create(organization=organization,
            group=group, post=post, user=user)
            event.dispatch(user)



