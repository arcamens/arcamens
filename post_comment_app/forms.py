from django import forms
from . import models

class PostCommentForm(forms.ModelForm):
    class Meta:
        model  = models.PostComment
        exclude = ('post', 'user')








