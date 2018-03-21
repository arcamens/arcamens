from django.utils.translation import ugettext_lazy as _
from timeline_app.forms import ConfirmTimelineDeletionForm
from django import forms
from . import models
import site_app.forms
import datetime

class OrganizationForm(forms.Form):
    name = forms.CharField()

class EventSearchForm(forms.Form):
    pattern = forms.CharField()
    seen = forms.BooleanField(required=False)

class EventFilterForm(forms.Form):
    val0  = datetime.date.today()-datetime.timedelta(days=3)
    start = forms.DateTimeField(initial = val0)

    val1 = datetime.date.today()+datetime.timedelta(days=1)
    end  = forms.DateTimeField(initial = val1)

class TagSearchForm(forms.Form):
    name = forms.CharField(required=False)

class OrganizationInviteForm(forms.Form):
    email = forms.EmailField(help_text="Insert user E-mail.")

class UserForm(forms.ModelForm):
    class Meta:
        model  = models.User
        fields = ('name', 'avatar', 'email', 'description')

class PasswordForm(forms.Form):
    retype = forms.CharField(required=True, widget=forms.PasswordInput())
    password = forms.CharField(required=True, widget=forms.PasswordInput())
    old = forms.CharField(required=True, widget=forms.PasswordInput())

    def __init__(self, *args, confirm_token='', **kwargs):
        self.confirm_token = confirm_token
        super(PasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(PasswordForm, self).clean()
        retype   = self.cleaned_data.get('retype')
        password = self.cleaned_data.get('password')
        old = self.cleaned_data.get('old')

        if old != self.confirm_token:
            raise forms.ValidationError(
                     "Wrong existing password!")

        if retype != password :
            raise forms.ValidationError(
                "    Password doesn't match!")

class GlobalFilterForm(forms.ModelForm):
    class Meta:
        model  = models.GlobalFilter
        exclude = ('user', 'organization')

class GlobalTaskFilterForm(forms.ModelForm):
    class Meta:
        model  = models.GlobalTaskFilter
        exclude = ('user', 'organization')

class UserFilterForm(forms.ModelForm):
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

class ShoutForm(forms.Form):
    msg = forms.CharField(required=False)

class ConfirmOrganizationDeletionForm(ConfirmTimelineDeletionForm):
    name = forms.CharField(required=True,
    help_text='Type the organization name to confirm!')


