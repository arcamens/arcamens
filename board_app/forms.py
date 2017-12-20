from django import forms
from . import models

class BoardForm(forms.ModelForm):
    class Meta:
        model  = models.Board
        exclude = ('owner', 'main', 'admins',
        'members', 'organization')

class BoardFilterForm(forms.ModelForm):
    class Meta:
        model  = models.BoardFilter
        exclude = ('user', 'organization')

class BindUsersForm(forms.Form):
    email = forms.EmailField()
    admin = forms.BooleanField(required=False)

class FindEventForm(forms.Form):
    pattern = forms.CharField()
    seen = forms.BooleanField(required=False)

class BoardSearchForm(forms.Form):
    name = forms.CharField(required=False)

class UserSearchForm(forms.Form):
    name = forms.CharField(required=False)





