from timeline_app.forms import ConfirmTimelineDeletionForm
from sqlike.forms import SqLikeForm
from django import forms
from . import models
import card_app.models

class BitbucketHookForm(forms.ModelForm):
    class Meta:
        model  = models.BitbucketHook
        fields = ('address', )










