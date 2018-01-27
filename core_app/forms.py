from django.utils.translation import ugettext_lazy as _
from django import forms
from . import models
import site_app.forms

class OrganizationForm(forms.Form):
    name = forms.CharField()

class UpdateOrganizationForm(forms.ModelForm):
    class Meta:
        model = models.Organization
        fields = ('owner', 'name')

class UserSearchForm(forms.Form):
    pattern = forms.CharField(required=False)

class EventSearchForm(forms.Form):
    pattern = forms.CharField()
    seen = forms.BooleanField(required=False)

class TagForm(forms.ModelForm):
    class Meta:
        model  = models.Tag
        exclude = ('organization', )

class BindTagForm(forms.Form):
    name = forms.CharField()

class TagSearchForm(forms.Form):
    name = forms.CharField(required=False)

# site_app should inherit from here.
class UserForm(site_app.forms.UserForm):
    class Meta:
        model   = models.User
        fields = ('name', 'avatar', 'email', 
        'password', 'description')

class BindUsersForm(forms.Form):
    email = forms.EmailField()
    admin = forms.BooleanField(required=False)

class TaskSearchForm(forms.Form):
    pattern = forms.CharField(required=False)
    done = forms.BooleanField(required=False)


class GlobalFilterForm(forms.ModelForm):
    class Meta:
        model  = models.GlobalFilter
        exclude = ('user', 'organization')


