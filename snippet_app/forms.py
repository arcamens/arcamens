from core_app.forms import FileAttachment
from django import forms
from . import models

class SnippetForm(forms.ModelForm):
    data = forms.CharField(strip=False, 
    required=False, widget=forms.Textarea)

    class Meta:
        model  = models.Snippet
        exclude = ('post', 'owner')

class SnippetFileWrapperForm(FileAttachment, forms.ModelForm):
    class Meta:
        model  = models.SnippetFileWrapper
        exclude = ('snippet', )







