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

