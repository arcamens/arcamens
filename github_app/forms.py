from group_app.forms import ConfirmGroupDeletionForm
from sqlike.forms import SqLikeForm
from django import forms
from . import models
import card_app.models

class GithubHookForm(forms.ModelForm):
    class Meta:
        model  = models.GithubHook
        fields = ('full_name', )













