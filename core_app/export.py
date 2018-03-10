import json

# import django

from board_app.models import Board
from card_app.models import Card
from list_app.models import List
from post_app.models import Post
from timeline_app.models import Timeline


def export_timelines(user):
    data = []
    for timeline in Timeline.objects.filter(organization=user.default):
        posts = []
        for post in Post.objects.filter(ancestor=timeline):
            # posts.append({'label': post.label, 'html': post.html, 'done': post.done})
            posts.append({'label': post.label, 'done': post.done})
        timeline_desc = {'label': timeline.name, 'desc': timeline.description, 'posts': posts}
        data.append(timeline_desc)
    return json.dumps(data)


def export_boards(user):
    data = []
    for board in Board.objects.filter(organization=user.default):
        lists = []
        for list in List.objects.filter(ancestor=board):
            cards = []
            for card in Card.objects.filter(ancestor=list):
                cards.append({'label': card.label, 'data': card.data, 'done': card.done})
            lists.append({'name': list.name, 'desc': list.description, 'cards': cards})
        board_desc = {'name': board.name, 'desc': board.description, 'lists': lists}
        data.append(board_desc)
    return json.dumps(data)


def import_timelines(user, json_str):
    data = json.loads(json_str)
    for timeline_desc in data:
        timeline = Timeline.objects.create(name=timeline_desc['label'], description=timeline_desc['desc'],
                                           owner=user, organization=user.default)
        timeline.users.add(user)
        for post_desc in timeline_desc['posts']:
            Post.objects.create(ancestor=timeline, label=post_desc['label'], done=post_desc['done'],
                                user=user)


def import_boards(user, json_str):
    data = json.loads(json_str)
    for board_desc in data:
        board = Board.objects.create(name=board_desc['name'], description=board_desc['desc'],
                                     owner=user, organization=user.default)
        board.members.add(user)
        for list_desc in board_desc['lists']:
            list = List.objects.create(ancestor=board, name=list_desc['name'], description=list_desc['desc'],
                                       owner=user)
            for card_desc in list_desc['cards']:
                Card.objects.create(ancestor=list, label=card_desc['label'], data=card_desc['data'], done=card_desc['done'],
                                    owner=user)
