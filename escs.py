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




