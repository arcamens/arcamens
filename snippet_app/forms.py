from django import forms
from . import models

class SnippetForm(forms.ModelForm):
    class Meta:
        model  = models.Snippet
        exclude = ('card', 'owner')

class SnippetFileWrapperForm(forms.ModelForm):
    class Meta:
        model  = models.SnippetFileWrapper
        exclude = ('snippet', )




