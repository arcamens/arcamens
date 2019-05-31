from core_app.forms import FileAttachment
from sqlike.forms import SqLikeForm
from django import forms
from . import models

class CommentForm(forms.ModelForm):
    data = forms.CharField(strip=False, 
    required=False, widget=forms.Textarea)

    class Meta:
        model  = models.Comment
        exclude = ('post', 'owner')

class CommentFileWrapperForm(FileAttachment, forms.ModelForm):
    class Meta:
        model  = models.CommentFileWrapper
        fields = ('file', )

class CommentSearchForm(SqLikeForm, forms.ModelForm):
    class Meta:
        model  = models.CommentSearch
        exclude = ('user', 'organization')


