from django.utils.translation import ugettext_lazy as _
from sqlike.forms import SqLikeForm
from django import forms
from . import models

class TimelineForm(forms.ModelForm):
    class Meta:
        model  = models.Timeline
        exclude = ('owner', 'organization', 'users')

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

class UserSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False)

class ConfirmTimelineDeletionForm(forms.Form):
    name = forms.CharField(required=True,
    help_text='Type the timeline name to confirm!')

    def __init__(self, *args, confirm_token='', **kwargs):
        self.confirm_token = confirm_token

        super(ConfirmTimelineDeletionForm, 
            self).__init__(*args, **kwargs)

    def clean(self):
        super(ConfirmTimelineDeletionForm, self).clean()
        name   = self.cleaned_data.get('name')

        if name != self.confirm_token:
            raise forms.ValidationError(
                "The name doesn't match!")


