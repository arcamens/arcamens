from django import forms
from sqlike.forms import SqLikeForm
from . import models

class PostForm(forms.ModelForm):
    class Meta:
        model  = models.Post
        exclude = ('user', 'ancestor', 'html', 'parent', 'priority')

class PostFileWrapperForm(forms.ModelForm):
    class Meta:
        model  = models.PostFileWrapper
        exclude = ('post', )

class PostFilterForm(SqLikeForm, forms.ModelForm):
    class Meta:
        model  = models.PostFilter
        exclude = ('user', 'timeline')

class GlobalAssignmentFilterForm(SqLikeForm, forms.ModelForm):
    class Meta:
        model  = models.GlobalAssignmentFilter
        exclude = ('user', 'organization')

        widgets = {
            'options': forms.RadioSelect,
        }

class GlobalPostFilterForm(SqLikeForm, forms.ModelForm):
    class Meta:
        model  = models.GlobalPostFilter
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

class ListSearchform(forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Ex: arcamens + todo ...')

class PostPriorityForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Example: owner:oliveira + tag:bug')


