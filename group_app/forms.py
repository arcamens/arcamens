from django.utils.translation import ugettext_lazy as _
from core_app.models import User, Membership
from sqlike.forms import SqLikeForm
from django import forms
from . import models

class GroupForm(forms.ModelForm):
    class Meta:
        model  = models.Group
        exclude = ('owner', 'organization', 'users', 'node')

    def __init__(self, *args, me=None, **kwargs):
        self.me = me
        super(GroupForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(GroupForm, self).clean()
        if not self.me.paid and not self.cleaned_data['public']:
            raise forms.ValidationError('Free accounts can have\
                just public groups.')

class GroupshipForm(forms.ModelForm):
    class Meta:
        model  = models.Groupship
        fields = ('status',)

class GroupSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False)

class UserSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False)

class ConfirmDeletionForm(forms.Form):
    name = forms.CharField(required=True)

    def __init__(self, *args, confirm_token='', **kwargs):
        self.confirm_token = confirm_token

        super(ConfirmDeletionForm, 
            self).__init__(*args, **kwargs)

    def clean(self):
        super(ConfirmDeletionForm, self).clean()
        name = self.cleaned_data.get('name')

        if name != self.confirm_token:
            raise forms.ValidationError("The name doesn't match!")

class ConfirmGroupDeletionForm(ConfirmDeletionForm):
    name = forms.CharField(required=True,
    help_text='Type the group name to confirm!')







