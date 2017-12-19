from django import forms
from . import models

class CardCommentForm(forms.ModelForm):
    class Meta:
        model  = models.CardComment
        exclude = ('post', 'user')








