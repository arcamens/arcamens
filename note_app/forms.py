from core_app.forms import FileAttachment
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
        exclude = ('note', )







