from django.utils.translation import ugettext_lazy as _
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

class UserForm(site_app.forms.UserForm):
    class Meta:
        model  = models.User
        fields = ('name', 'avatar', 
        'email', 'password', 'description', 
        'recover_email')

        widgets = {
        'password': forms.PasswordInput()}

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






