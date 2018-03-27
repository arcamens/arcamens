from django import forms
from core_app.forms import SqlikeForm
from . import models

class PostForm(forms.ModelForm):
    class Meta:
        model  = models.Post
        exclude = ('user', 'ancestor', 
            'html', 'parent')

class PostFileWrapperForm(forms.ModelForm):
    class Meta:
        model  = models.PostFileWrapper
        exclude = ('post', )

class PostFilterForm(SqlikeForm, forms.ModelForm):
    class Meta:
        model  = models.PostFilter
        exclude = ('user', 'timeline')

class AssignmentFilterForm(SqlikeForm, forms.ModelForm):
    class Meta:
        model  = models.AssignmentFilter
        exclude = ('user', 'organization')

class GlobalPostFilterForm(SqlikeForm, forms.ModelForm):
    class Meta:
        model  = models.GlobalPostFilter
        exclude = ('user', 'organization')

class UserSearchForm(forms.Form):
    pattern = forms.CharField(required=False,
    help_text='Example: victor + #arcamens + #suggestion ...')

class TagSearchForm(forms.Form):
    name = forms.CharField(required=False)

class AssignPostForm(forms.Form):
    email = forms.EmailField()

class PostAttentionForm(forms.Form):
    message = forms.CharField(
    required=False, widget=forms.Textarea,
    help_text='(Optional) Be in the meeting 20 min earlier.')

class AlertPostWorkersForm(forms.Form):
    message = forms.CharField(
    required=False, widget=forms.Textarea,
    help_text='Please, take a look at this asap!')







