from django.utils.translation import ugettext_lazy as _
from timeline_app.forms import ConfirmTimelineDeletionForm
from sqlike.forms import SqLikeForm
from card_app.models import Card
from django import forms
from . import models
import site_app.forms
import datetime

class OrganizationForm(forms.Form):
    name = forms.CharField()

class RemoveUserForm(forms.Form):
    reason = forms.CharField(required=False, help_text='You are fired!')

class EventFilterForm(forms.Form):
    val0  = datetime.date.today()-datetime.timedelta(days=3)
    start = forms.DateField(initial = val0, widget=forms.SelectDateWidget())

    val1 = datetime.date.today()+datetime.timedelta(days=1)
    end  = forms.DateField(initial = val1, widget=forms.SelectDateWidget())

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




