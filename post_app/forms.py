from django import forms
from sqlike.forms import SqLikeForm
from core_app.forms import FileAttachment
from . import models

class PostForm(forms.ModelForm):
    class Meta:
        model  = models.Post
        fields = ('label', 'data')

class PostFileWrapperForm(FileAttachment, forms.ModelForm):
    class Meta:
        model  = models.PostFileWrapper
        fields = ('file', )

class PostFilterForm(SqLikeForm, forms.ModelForm):
    class Meta:
        model  = models.PostFilter
        exclude = ('user', 'group')

class PostSearchForm(SqLikeForm, forms.ModelForm):
    class Meta:
        model  = models.PostSearch
        exclude = ('user', 'organization')

class UserSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False,
    help_text='Example: oliveira + mens.com')

class TagSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Example: feature')

class PostAttentionForm(forms.Form):
    message = forms.CharField(
    required=False, widget=forms.Textarea,
    help_text='(Optional) Be in the meeting 20 min earlier.')

class AlertPostWorkersForm(forms.Form):
    message = forms.CharField(
    required=False, widget=forms.Textarea,
    help_text='Please, take a look at this asap!')

class ListSearchform(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Ex: arcamens + todo ...')

class PostPriorityForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Example: owner:oliveira + tag:bug')

# class PostTaskshipForm(forms.ModelForm):
    # class Meta:
        # model  = models.PostTaskship
        # fields = ('status',)

class PostTagshipForm(forms.ModelForm):
    class Meta:
        model  = models.PostTagship
        fields = ()







