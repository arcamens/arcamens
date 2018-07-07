from django import forms
from core_app.forms import FileAttachment
from sqlike.forms import SqLikeForm
from . import models

class UserSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False,
    help_text='Example: tag:arcamens + tag:bug-hunter')

class CardSearchForm(SqLikeForm, forms.Form):
    done = forms.BooleanField(required=False)

    pattern = forms.CharField(required=False, 
    help_text='Example: owner:oliveira + tag:bug')

class CardPriorityForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Example: owner:oliveira + tag:bug')

class ConnectCardForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Example: owner:oliveira + tag:bug')

class ConnectPostForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Example: owner:oliveira + tag:bug')

class TagSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Example: fake-bug')

class ListSearchform(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Ex: arcamens + todo ...')

class GroupSearchform(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Ex: arcamens + backlog ...')

class CardAttentionForm(forms.Form):
    message = forms.CharField(
    required=False, widget=forms.Textarea,
    help_text='(Optional) Hey, do you remember \
    you have a job?')

class AlertCardWorkersForm(forms.Form):
    message = forms.CharField(
    required=False, widget=forms.Textarea,
    help_text='I need this task done a!')

class GlobalCardFilterForm(SqLikeForm, forms.ModelForm):
    class Meta:
        model  = models.GlobalCardFilter
        exclude = ('user', 'organization')

class CardFilterForm(SqLikeForm, forms.ModelForm):
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

class CardFileWrapperForm(FileAttachment, forms.ModelForm):
    class Meta:
        model  = models.CardFileWrapper
        exclude = ('card', )





