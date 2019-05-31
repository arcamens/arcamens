from django import forms
from . import models

class ECreateFeedbackForm(forms.ModelForm):
    class Meta:
        model  = models.ECreateFeedback
        fields = ('data', )










