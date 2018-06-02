from django.utils.translation import ugettext_lazy as _
from timeline_app.forms import ConfirmTimelineDeletionForm
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

class ConfirmOrganizationDeletionForm(ConfirmTimelineDeletionForm):
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


