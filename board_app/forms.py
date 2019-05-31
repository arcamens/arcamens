from group_app.forms import ConfirmDeletionForm
from core_app.models import User, Membership
from sqlike.forms import SqLikeForm
from django import forms
from . import models
import card_app.models

class BoardForm(forms.ModelForm):
    class Meta:
        model  = models.Board
        exclude = ('owner', 'main', 'admins',
        'members', 'organization', 'node')

    def __init__(self, *args, me=None, **kwargs):
        self.me = me
        super(BoardForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(BoardForm, self).clean()
        if not self.me.paid and not self.cleaned_data['public']:
            raise forms.ValidationError('Free accounts can have\
                just public boards.')

class BindUsersForm(forms.Form):
    email = forms.EmailField()
    admin = forms.BooleanField(required=False)

class BoardSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False)

class UserSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False)

class ConfirmBoardDeletionForm(ConfirmDeletionForm):
    name = forms.CharField(required=True,
    help_text='Type the board name to confirm!')

class BoardshipForm(forms.ModelForm):
    class Meta:
        model  = models.Boardship
        fields = ('status',)







