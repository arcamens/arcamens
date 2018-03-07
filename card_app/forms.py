from django import forms
from . import models

class CardFilterForm(forms.ModelForm):
    class Meta:
        model  = models.CardFilter
        exclude = ('user', 'organization', 
        'board', 'list')

class CardForm(forms.ModelForm):
    class Meta:
        model  = models.Card
        fields = ('label', 'data')

class ImageWrapperForm(forms.ModelForm):
    class Meta:
        model  = models.ImageWrapper
        exclude = ('card', )

class FileWrapperForm(forms.ModelForm):
    class Meta:
        model  = models.FileWrapper
        exclude = ('card', )

class UserSearchForm(forms.Form):
    pattern = forms.CharField(required=False,
    help_text='Example: victor + #arcamens \
    + #suggestion ...')

class CardSearchForm(forms.Form):
    done = forms.BooleanField(required=False)

    pattern = forms.CharField(required=False, 
    help_text='Example: iury + #arcamens + \
    websocket disconencts + #bug ...')

class TagSearchForm(forms.Form):
    name = forms.CharField(required=False)

class ListSearchform(forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='board or description : list or description')

class CardAttentionForm(forms.Form):
    message = forms.CharField(
    required=False, widget=forms.Textarea,
    help_text='(Optional) Hey, do you remember \
    you have a job?')

class AlertCardWorkersForm(forms.Form):
    message = forms.CharField(
    required=False, widget=forms.Textarea,
    help_text='I need this task done a!')





