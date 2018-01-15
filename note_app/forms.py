from django import forms
from . import models

class NoteForm(forms.ModelForm):
    class Meta:
        model  = models.Note
        exclude = ('card', 'owner')

class NoteFileWrapperForm(forms.ModelForm):
    class Meta:
        model  = models.NoteFileWrapper
        exclude = ('note', )



