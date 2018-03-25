##############################################################################
# activate, virtualenv, opus.
cd ~/.virtualenvs/
source arcamens/bin/activate
cd ~/projects/arcamens-code

tee >(stdbuf -o 0 python -i)
tee >(python manage.py shell --settings=arcamens.settings)

quit()
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


