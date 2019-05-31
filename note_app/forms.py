from core_app.forms import FileAttachment
from sqlike.forms import SqLikeForm
from django import forms
from . import models

class NoteForm(forms.ModelForm):
    data = forms.CharField(strip=False, widget=forms.Textarea)
    class Meta:
        model  = models.Note
        exclude = ('card', 'owner')

class NoteFileWrapperForm(FileAttachment, forms.ModelForm):
    class Meta:
        model  = models.NoteFileWrapper
        fields = ('file', )

class NoteSearchForm(SqLikeForm, forms.ModelForm):
    class Meta:
        model  = models.NoteSearch
        exclude = ('user', 'organization')








