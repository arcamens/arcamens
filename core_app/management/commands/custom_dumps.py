import json

from django.core.management.base import BaseCommand
from core_app.models import User, Organization
from board_app.models import Board
from group_app.models import Group


class Command(BaseCommand):
    help = 'Custom dumps for boards/groups.'

    def add_arguments(self, parser):
        parser.add_argument('organization', type=str)
        parser.add_argument('file', type=str)

    def handle(self, *args, **kwargs):
        organization = Organization.objects.get(name=kwargs['organization'])
        data = {'name': organization.name,
        'elems': {'boards': self.dump_boards(organization),
        'groups': self.dump_groups(organization)}}

        fd = open(kwargs['file'], 'w')
        json.dump(data, fd)
        fd.close()

    def dump_boards(self, organization):
        boards = []
        for ind in organization.boards.all():
            boards.append({'name': ind.name,
                'description': ind.description,
                    'lists': self.dump_lists(ind)})
        return boards

    def dump_lists(self, board):
        lists = []
        for ind in board.lists.all():
            lists.append({'name': ind.name,
                'cards': self.dump_cards(ind)})
        return lists

    def dump_cards(self, list):
        cards = []
        for ind in list.cards.all():
            cards.append({'label': ind.label, 'data': ind.data,
                'priority': ind.priority, 'done': ind.done})
        return cards

    def dump_groups(self, organization):
        groups = []
        for ind in organization.groups.all():
            groups.append({'name': ind.name, 
                'description': ind.name,  
                    'posts': self.dump_posts(ind)})
        return groups

    def dump_posts(self, group):
        posts = []
        for ind in group.posts.all():
            posts.append({'priority': ind.priority,
                'label': ind.label, 'data': ind.data, 
                    'done': ind.done})
        return posts
