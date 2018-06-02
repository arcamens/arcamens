##############################################################################
# Activate virtualenv.
cd ~/.virtualenvs/
source arcamens/bin/activate
cd ~/projects/arcamens-code

tee >(stdbuf -o 0 python -i)
tee >(python manage.py shell --settings=arcamens.settings)

quit()
##############################################################################
# connect to victor vps and activate virtualenv.
tee >(stdbuf -o 0 ssh arcamens@staging.arcamens.com 'bash -i')

cd ~/.virtualenv/
source opus/bin/activate
cd ~/projects/arcamens-code
tee >(python manage.py shell --settings=arcamens.settings)

##############################################################################

from django import forms
f = forms.CharField()
f.clean('foo')

f = forms.EmailField()
f.clean('foo@oo.com')
help(f.clean)

from django import forms
help(forms.Form.clean)
##############################################################################
from core_app.models import User
import datetime

me = User.objects.get(name__startswith='iury')
me.expiration
(me.expiration - datetime.date.today()).days
##############################################################################
import os
os.rmdir('oaisduoi')
help(os.rmdir)

import shutil
shutil.rmtree('oiausoidu', ignore_errors=True)
shutil.rmtree('oiausoidu')
##############################################################################

from django.apps import apps
apps.get_app_config('admin').verbose_name
mod = apps.get_app_config('admin')
mod.module
mod.path

globals()[mod]
getattr(, function_name)

##############################################################################

from django.core.paginator import Paginator, EmptyPage
help(Paginator)


from django.template.loader import get_template
from django.template import Context

##############################################################################

from core_app.models import *
from card_app.models import *
from board_app.models import *
from list_app.models import *
from post_app.models import *
from timeline_app.models import *
from site_app.models import *
from note_app.models import *
from snippet_app.models import *
from comment_app.models import *

events = Event.objects.all()

def normalize_events(events):
    for ind in events:
        ind.create_html_cache()

events = ECreateCard.objects.all()
normalize_events(events)
events = EUpdateCard.objects.all()
normalize_events(events)
events = EUpdateNote.objects.all()
normalize_events(events)
##############################################################################
# testing https://staging.arcamens.com/card_app/card-link/350/
# bug with queryset.union when the latter queryset type is Model.objects.none().

from card_app.models import Card
from post_app.models import Post

cards = Card.objects.all()
post = Post.objects.none()

all = cards.union(post)
all
##############################################################################
from django.db.models import Q
from re import split
from functools import reduce
import operator

class SqLike:
    def __init__(self, fields, default):
        self.fields         = fields
        self.default = default

    def build(self, data):
        tokens = split(' *\+ *', data)
        sql    = []
        for ind in tokens:
            sql.append(self.fmt(ind))
        return sql

    def fmt(self, pair):
        pair = pair.split(':')
        q = self.fields.get(pair[0], self.default)
        sql = q(pair[-1])
        return sql

    def join(self, sql):
        return chks, tags

fields = {
    'o': lambda ind: Q(owner__name__icontains=ind),
    'w': lambda ind: Q(workers__name__icontains=ind),
    'c': lambda ind: Q(created__icontains=ind),
    'l': lambda ind: Q(label__icontains=ind),
    'd': lambda ind: Q(data__icontains=ind),
    's': lambda ind: Q(snippets_label__icontains=ind),
    'n': lambda ind: Q(note__data__icontains=ind),
    't': lambda ind: Q(tags__name__icontains=ind),

}

default = lambda ind: Q(label__icontains=ind) | Q(data__icontains=ind) 

sqlike = SqLike(fields, default)
stmt = sqlike.build('l:this + d:cool')
stmt

stmt = sqlike.build('test')
stmt

x = 'foo:bar'
x.split(':')

y = 'foo'
y.split(':')
##############################################################################
from django.db.models import Q
from re import split
from functools import reduce
import operator

class SqLike:
    def __init__(self, fields, default):
        self.fields         = fields
        self.default = default
        self.sql    = {
        'default':[]
        }
    def build(self, data):
        tokens = split(' *\+ *', data)
        tokens = map(lambda ind: ind.split(':', 2), tokens)
        for ind in tokens:
            self.fmt(ind)
        return self.sql
    def fmt(self, ind):
        seq, q = (self.sql.setdefault(ind[0], []), self.fields[ind[0]])\
        if len(ind) > 1 else (sql['default'], self.default)
        seq.append(q(ind[-1]))


fields = {
    'o': lambda ind: Q(owner__name__icontains=ind),
    'w': lambda ind: Q(workers__name__icontains=ind),
    'c': lambda ind: Q(created__icontains=ind),
    'l': lambda ind: Q(label__icontains=ind),
    'd': lambda ind: Q(data__icontains=ind),
    's': lambda ind: Q(snippets_label__icontains=ind),
    'n': lambda ind: Q(note__data__icontains=ind),
    't': lambda ind: Q(tags__name__icontains=ind),

}

default = lambda ind: Q(label__icontains=ind) | Q(data__icontains=ind) 

sqlike = SqLike(fields, default)
stmt = sqlike.build('l:this + d:cool')
print(stmt)
##############################################################################
from django.db.models import Q
from re import split
from functools import reduce
from operator import and_, or_

class SqNode:
    def __init__(self, tokens, rule, op=and_):
        self.rule = rule
        self.tokens = tokens
        self.op = op
        self.seq = [Q()]

    def add(self, value):
        self.seq.append(self.rule(value))

    def build(self):
        return reduce(self.op, self.seq)

class SqLike:
    def __init__(self, node, *args, op=and_):
        self.args  = args
        self.node = node
        self.op = op

        self.sql = {
        }

        self.default = []

        for indi in args:
            for indj in indi.tokens:
                self.sql[indj] = indi

    def build(self):
        sql = []
        for ind in self.sql.values():
            sql.append(ind.build())
        return reduce(self.op, sql)

    def feed(self, data):
        tokens = split(' *\+ *', data)
        tokens = map(lambda ind: ind.split(':', 2), tokens)

        for ind in tokens:
            if len(ind) > 1:
                self.sql[ind[0]].add(ind[1])
            else:
                self.node.add(ind[0])
        return self.build()

owner   = lambda ind: Q(owner__name__icontains=ind) | Q(
owner__email__icontains=ind)

worker  = lambda ind: Q(workers__name__icontains=ind) | Q(    
workers__email__icontains=ind)

created = lambda ind: Q(created__icontains=ind)
label   = lambda ind: Q(label__icontains=ind)
data    = lambda ind: Q(data__icontains=ind)

snippet = lambda ind: Q(snippets_label__icontains=ind) | Q(
snippets_data__icontains=ind)

note  = lambda ind: Q(note__data__icontains=ind)
tag   = lambda ind: Q(tags__name__icontains=ind)
list  = lambda ind: Q(ancestor__name__icontains=ind)
board = lambda ind: Q(ancestor__ancestor__name__icontains=ind)
default = lambda ind: Q(label__icontains=ind) | Q(data__icontains=ind) 

sqlike = SqLike(SqNode(None, default),
SqNode(('o', 'owner'), owner),
SqNode(('l', 'label'), label),
SqNode(('d', 'data'), data),
SqNode(('w', 'worker'), worker, or_), 
SqNode(('c', 'created'), created))


stmt = sqlike.feed('l:this + d:cool + d:nice + shit + w:iury + w:victor')
print(stmt)
##############################################################################
# create users on victor vps.

tee >(stdbuf -o 0 ssh arcamens@staging.arcamens.com 'bash -i')
cd ~/.virtualenv/
source opus/bin/activate
cd ~/projects/arcamens
tee >(python manage.py shell --settings=arcamens.settings)

from core_app.models import User, Organization
organization = Organization.objects.get(name='Arcamens')
organization

# create the users.
for ind in range(200):
    test = User.objects.create(name='TestUser-%s' % ind, 
        email='usermail-%s@bar.com' % ind, default=arcamens)
    test.organizations.add(arcamens)


from board_app.models import Board
board = Board.objects.get(name='Arcamens', organization=organization)
board.members.add(*organization.users.all())
##############################################################################
# assign all boards to me.

tee >(stdbuf -o 0 ssh arcamens@staging.arcamens.com 'bash -i')
cd ~/.virtualenv/
source opus/bin/activate
cd ~/projects/arcamens
tee >(python manage.py shell --settings=arcamens.settings)

from core_app.models import User, Organization
from board_app.models import Board
user = User.objects.get(name__istartswith='iury')
boards = Board.objects.filter(organization__name__istartswith='arcamens')

for ind in boards:
    ind.members.add(user)

##############################################################################
# move suggestion list cards to arcamens/backlog.

from core_app.models import User, Organization
from board_app.models import Board
from list_app.models import List
from timeline_app.models import Timeline
from post_app.models import Post

lst = List.objects.get(name__startswith='Suggestion', 
ancestor__organization__name='Arcamens', 
ancestor__name__startswith='Arcamens')

timeline = Timeline.objects.get(name__icontains='Arcamens/backlog',
organization__name='Arcamens')

for ind in lst.cards.all():
    Post.objects.create(label=ind.label, 
        ancestor=timeline, data=ind.data,user=ind.owner)    

from board_app.models import Board
board = Board.objects.get(name='Arcamens', organization=organization)
board.members.add(*organization.users.all())
##############################################################################
from re import findall

REGX  ='card_app/card-link/([0-9]+)'
cards = findall(REGX, 'this is a test ee https://staging.arcamens.com/card_app/card-link/500358/ letssee good https://staging.arcamens.com/card_app/card-link/500358/')
cards
##############################################################################
# Get database db name, password and username.
# Execute raw sql in the database.

from django.db import connection
db_name = connection.settings_dict['NAME']
db_name
connection.settings_dict
cursor = connection.cursor()
SQL = 'drop table django_migrations;'
cursor.execute(SQL)
connection.vendor
from django.db.utils import OperationalError
with cursor:
    cursor.execute(SQL)

help(connection)
help(connection.cursor)

from django.db import connections
dir(connections)
help(connections)
print(connections)

##############################################################################

from card_app.models import Card
card = Card.objects.create(label='aks')
card.id

cards = Card.objects.filter(id__in=[str(card.id)])
cards.all()

x = Card.objects.get(id='51')
x
##############################################################################
# Bug with django m2m field. When joining two querysets 
# from the manytomany it doubles the results.
from core_app.models import Event
event = Event.objects.all().first()
event.html

event.users.all() | event.signers.all()

# <QuerySet [<User: Iury de oliveira>, <User: Iury de oliveira>, <User: Iury de oliveira>, <User: Iury de oliveira>, <User: Iury de oliveira>, <User: Iury de oliveira>, <User: Iury de oliveira>, <User: Iury de oliveira>, <User: Iury de oliveira>]>
>>> 

event.users.all()
# >>> event.users.all()
# <QuerySet []>
# >>> 

event.signers.all()
# >>> event.signers.all()
# <QuerySet [<User: Iury de oliveira>]>
# >>> 

# It should return just one User instance.
event.users.all() | event.signers.all()

event.users.values_list('onesignal_id')
list(Event.objects.all().values_list('users__onesignal_id', flat=True))
##############################################################################

from requests.exceptions import HTTPError
from onesignalclient.app_client import OneSignalAppClient
from onesignalclient.notification import Notification
from django.conf import settings

client = OneSignalAppClient(app_id=settings.ONE_SIGNAL_APPID, 
app_api_key=settings.ONE_SIGNAL_API_KEY)

notification = Notification(settings.ONE_SIGNAL_APPID, 
Notification.DEVICES_MODE)
notification.include_player_ids = ['d09804ed-e996-43b7-a7f4-578738c57cc1']
notification
dir(notification)
notification.get_payload_for_request()
client.create_notification(notification)


notification = Notification(settings.ONE_SIGNAL_APPID, 
Notification.DEVICES_MODE)
notification.include_player_ids = ['ioliveira@id.uff.br']
notification
client.create_notification(notification)

client.get_headers()
##############################################################################
# Example that describes how to send a notification through onesignal.

import requests
import json

url = 'https://onesignal.com/api/v1/notifications'

headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Basic YjQ5NDc3MWItYzNjNS00MmZhLWEyNTYtZTk5YjJkYjkwZTY4'}

payload = {'app_id': 'e4387e31-b5c1-493a-8a28-f56bfed98c27', 'contents': {'en': 'Default message.'}, 'content_available': False, 'include_player_ids': ['d09804ed-e996-43b7-a7f4-578738c57cc1']}

req = requests.post(url, data=json.dumps(payload), headers=headers)
req
req.text

payload = {
    'app_id': settings.ONE_SIGNAL_APPID, 
    'contents': {'en': 'Default message.'}, 
    'content_available': False, 
    'include_player_ids': ['d09804ed-e996-43b7-a7f4-578738c57cc1']
}

payload

auth = "Basic %s" % settings.ONE_SIGNAL_API_KEY

headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": auth
}

req = requests.post(url, data=json.dumps(payload), headers=headers)
req
req.text
##############################################################################
import requests
import json
from django.conf import settings
url = 'https://onesignal.com/api/v1/notifications'

payload = {'app_id': 'e4387e31-b5c1-493a-8a28-f56bfed98c27', 
'filters': [{'field': 'tag',  'relation': 'exists', 'key': 'device_id',
'value': 'device-3'}],
'contents': {'en': 'Activity from Bitbucket Service!'}}


auth = "Basic %s" % settings.ONE_SIGNAL_API_KEY

headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": auth
}

req = requests.post(url, data=json.dumps(payload), headers=headers)
req
req.text
##############################################################################
from itertools import *
import itertools

lst0 = ['a', 'b', 'c', 'd', 'e']
itertools.izip(['|'], lst0)
dir(itertools)
lst0.extend((1, 2))
lst0
##############################################################################
lst = [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13]
rst = []

rst = [lst[ind * 3:(ind + 1) * 3] 
for ind in range(0, len(lst)//3 + 1)]
rst
##############################################################################
# Do lookups of cards that have an organization that has a BitbucketHook.
# bitbucket_app debugging.

from card_app.models import Card
from bitbucket_app.models import BitbucketHook
from django.db.models import Q

cards = Card.objects.filter(
ancestor__ancestor__organization__bitbucket_hooks__full_name='arcamens/django-github')

cards.count()

hooks = BitbucketHook.objects.filter(full_name='arcamens/django-github')
orgs = hooks.values_list('organization')
is_ok = Q(ancestor__ancestor__organization=orgs)
cards = Card.objects.filter(is_ok)
cards.count()

for ind in []:
    pass
else:
    print('hi')
##############################################################################
import html2text
h = html2text.HTML2Text()
h.ignore_links = True
h.handle("<p>Hello, <a href='http://earth.google.com/'>world</a>!")
help(h.handle)
dir(h)
##############################################################################
from ehp import *

html = Html()

data = '''
<body> <em> foo </em> </body>
'''

dom = html.feed(data)
dom.text()

##############################################################################
# delete user eventfilter on victor server.
from core_app.models import User
import datetime

me = User.objects.get(name__startswith='Iury')
me.eventfilter_set.all().delete()

##############################################################################


