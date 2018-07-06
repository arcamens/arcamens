from group_app.forms import ConfirmGroupDeletionForm
from sqlike.forms import SqLikeForm
from django import forms
from . import models
import card_app.models

class BoardForm(forms.ModelForm):
    class Meta:
        model  = models.Board
        exclude = ('owner', 'main', 'admins',
        'members', 'organization', 'node')

class UpdateBoardForm(forms.ModelForm):
    class Meta:
        model  = models.Board
        exclude = ('owner', 'main', 'admins',
        'members', 'organization', 'node', 'open')

class BindUsersForm(forms.Form):
    email = forms.EmailField()
    admin = forms.BooleanField(required=False)

class BoardSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False)

class UserSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False)

class ConfirmBoardDeletionForm(ConfirmGroupDeletionForm):
    name = forms.CharField(required=True,
    help_text='Type the board name to confirm!')









