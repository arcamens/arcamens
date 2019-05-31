from django import forms
from . import models

class ListForm(forms.ModelForm):
    class Meta:
        model   = models.List
        exclude = ('ancestor',  'owner')

class BindMemberForm(forms.Form):
    email = forms.EmailField()

class ListFilterForm(forms.ModelForm):
    class Meta:
        model  = models.ListFilter
        exclude = ('user', 'organization', 'board')



