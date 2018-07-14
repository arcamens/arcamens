from django.utils.translation import ugettext_lazy as _
from group_app.forms import ConfirmGroupDeletionForm
from slock.forms import SetPasswordForm
from sqlike.forms import SqLikeForm
from card_app.models import Card
from django import forms
from . import models
import site_app.forms
import datetime

class OrganizationForm(forms.Form):
    name = forms.CharField(help_text='Example: Your business name.')

class RemoveUserForm(forms.Form):
    reason = forms.CharField(required=False, help_text='You are fired!')

class TagSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, help_text='Example: developer')

class OrganizationInviteForm(forms.Form):
    email = forms.EmailField(help_text="Insert user E-mail.")

class ShoutForm(forms.Form):
    msg = forms.CharField(required=False)

class ConfirmOrganizationDeletionForm(ConfirmGroupDeletionForm):
    name = forms.CharField(required=True,
    help_text='Type the organization name to confirm!')

class UserForm(forms.ModelForm):
    class Meta:
        model  = models.User
        fields = ('name', 'avatar', 'email', 'description')

class UserFilterForm(SqLikeForm, forms.ModelForm):
    class Meta:
        model  = models.UserFilter
        exclude = ('user', 'organization')

class TagForm(forms.ModelForm):
    class Meta:
        model  = models.Tag
        exclude = ('organization', )

class UpdateOrganizationForm(forms.ModelForm):
    class Meta:
        model = models.Organization
        fields = ( 'name', )

class UserSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False,
    help_text='tag:developer + tag:python')


class SignupForm(SetPasswordForm):
    class Meta:
        model   = models.User
        exclude = ('organizations', 'default', 'service', 
        'expiration', 'max_users', 'paid')

class NodeFilterForm(forms.ModelForm):
    class Meta:
        model  = models.NodeFilter
        exclude = ('user', 'organization')

class EventFilterForm(forms.ModelForm):
    class Meta:
        model  = models.EventFilter
        exclude = ('user', 'organization')
        widgets = {
            'start': forms.SelectDateWidget(),
            'end': forms.SelectDateWidget()
        }

class FileAttachment:
    """
    We have to set different file size upload limits.
    One for free plans one for paid plans eventually.
    """
    def __init__(self, *args, max_file=1, storage=0, 
        max_storage=100, **kwargs):

        self.max_file      = max_file * 1024 * 1024
        self.storage       = storage * 1024 * 1024
        self.max_storage   = max_storage * 1024 * 1024
        super(FileAttachment, self).__init__(*args, **kwargs)

    def clean(self):
        super(FileAttachment, self).clean()
        file = self.cleaned_data.get('file')

        if file.size > self.max_file:
            raise forms.ValidationError("File too big!\
                Check your upload limits ")
        elif file.size + self.storage > self.max_storage:
            raise forms.ValidationError("It overrides your \
                max montly storage. Check your upload limits ")
        


