from django.utils.translation import ugettext_lazy as _
from django import forms
from . import models

class TimelineForm(forms.ModelForm):
    class Meta:
        model  = models.Timeline
        exclude = ('owner', 'organization', 'users')

class BindUsersForm(forms.Form):
    email = forms.EmailField()
    admin = forms.BooleanField(required=False)

class FilterForm(forms.Form):
    pattern = forms.CharField()

class FindUserForm(forms.Form):
    pattern = forms.CharField()

class TimelineFilterForm(forms.ModelForm):
    class Meta:
        model  = models.TimelineFilter
        exclude = ('user', 'organization')

class BindTimelinesForm(forms.Form):
    name = forms.CharField(required=False)

# class ListUsersSearchForm(forms.Form):
    # pattern = forms.CharField(required=False)

class FindEventForm(forms.Form):
    pattern = forms.CharField()
    seen = forms.BooleanField(required=False)

class FindTagForm(forms.Form):
    pattern = forms.CharField()

class BindTagForm(forms.Form):
    name = forms.CharField()

class TagForm(forms.ModelForm):
    class Meta:
        model  = models.Tag
        exclude = ('organization', )

class UserSearchForm(forms.Form):
    name = forms.CharField(required=False)





