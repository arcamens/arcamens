from django.utils.translation import ugettext_lazy as _
from sqlike.forms import SqLikeForm
from django import forms
from . import models

class GroupForm(forms.ModelForm):
    class Meta:
        model  = models.Group
        exclude = ('owner', 'organization', 'users', 'node')

class UpdateGroupForm(forms.ModelForm):
    class Meta:
        model  = models.Group
        exclude = ('owner', 'organization', 'users', 'node', 'open')

class GroupSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False)

class UserSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False)

class ConfirmGroupDeletionForm(forms.Form):
    name = forms.CharField(required=True,
    help_text='Type the group name to confirm!')

    def __init__(self, *args, confirm_token='', **kwargs):
        self.confirm_token = confirm_token

        super(ConfirmGroupDeletionForm, 
            self).__init__(*args, **kwargs)

    def clean(self):
        super(ConfirmGroupDeletionForm, self).clean()
        name   = self.cleaned_data.get('name')
        if name != self.confirm_token:
            raise forms.ValidationError("The name doesn't match!")






