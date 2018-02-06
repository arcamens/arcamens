from django.utils.translation import ugettext_lazy as _
from django import forms
from . import models
import site_app.forms
import datetime

class OrganizationForm(forms.Form):
    name = forms.CharField()

class UserSearchForm(forms.Form):
    pattern = forms.CharField(required=False)

class EventSearchForm(forms.Form):
    pattern = forms.CharField()
    seen = forms.BooleanField(required=False)

class BindTagForm(forms.Form):
    name = forms.CharField()

class TagSearchForm(forms.Form):
    name = forms.CharField(required=False)

class BindUsersForm(forms.Form):
    email = forms.EmailField()
    admin = forms.BooleanField(required=False)

class TaskSearchForm(forms.Form):
    pattern = forms.CharField(required=False)
    done = forms.BooleanField(required=False)

class UserForm(site_app.forms.UserForm):
    class Meta:
        model   = models.User
        fields = ('name', 'avatar', 
        'email', 'password', 'description', 
        'recover_email')

class GlobalFilterForm(forms.ModelForm):
    class Meta:
        model  = models.GlobalFilter
        exclude = ('user', 'organization')

class TagForm(forms.ModelForm):
    class Meta:
        model  = models.Tag
        exclude = ('organization', )

class UpdateOrganizationForm(forms.ModelForm):
    class Meta:
        model = models.Organization
        fields = ('owner', 'name')

class EventFilterForm(forms.Form):
    start = forms.DateField(initial=datetime.date.today)
    end = forms.DateField(initial=datetime.date.today)


