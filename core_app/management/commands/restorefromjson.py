import json
import argparse

from django.core.management import BaseCommand

import core_app
from board_app.models import Board
from card_app.models import Card
from list_app.models import List
from note_app.models import Note
from post_app.models import Post
from snippet_app.models import Snippet
from group_app.models import Group


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("json", type=argparse.FileType('r'))
        parser.add_argument("user", type=str)

    def handle(self, *args, **kwargs):
        user = core_app.models.User.objects.get(name__startswith=kwargs['user'])

        data = json.load(kwargs['json'])
        models = {'group_app.group', 'post_app.post',
                  'board_app.board', 'list_app.list', 'card_app.card', 'snippet_app.snippet', 'note_app.note'}
        hash = {m: [] for m in models}
        for row in data:
            if not row['model'] in models:
                continue
            hash[row['model']].append(row['fields'])

        for group_data in hash['group_app.group']:
            group = Group.objects.create(name=group_data['name'], description=group_data['description'],
                                               owner=user, organization=user.default)
            group.users.add(user)

        for post_data in hash['post_app.post']:
            Post.objects.create(ancestor_id=post_data['ancestor'], label=post_data['label'], done=post_data['done'],
                                user=user)

        for board_data in hash['board_app.board']:
            board = Board.objects.create(name=board_data['name'], description=board_data['description'],
                                         owner=user, organization=user.default)
            board.members.add(user)

        for list_data in hash['list_app.list']:
            List.objects.create(ancestor_id=list_data['ancestor'], name=list_data['name'], description=list_data['description'],
                                owner=user)

        for card_data in hash['card_app.card']:
            Card.objects.create(ancestor_id=card_data['ancestor'], label=card_data['label'], data=card_data['data'], done=card_data['done'],
                                owner=user)

        for snippet_data in hash['snippet_app.snippet']:
            Snippet.objects.create(post_id=snippet_data['post'], title=snippet_data['title'], data=snippet_data['data'],
                                   owner=user)

        for note_data in hash['note_app.note']:
            Note.objects.create(card_id=note_data['card'], data=note_data['data'],
                                owner=user)
