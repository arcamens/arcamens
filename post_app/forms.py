from django import forms
from . import models

class PostForm(forms.ModelForm):
    class Meta:
        model  = models.Post
        exclude = ('user', 'ancestor', 'html')

class PostFileWrapperForm(forms.ModelForm):
    class Meta:
        model  = models.PostFileWrapper
        exclude = ('post', )

class AssignPostForm(forms.Form):
    email = forms.EmailField()

class PostFilterForm(forms.ModelForm):
    class Meta:
        model  = models.PostFilter
        exclude = ('user', 'timeline')

class GlobalPostFilterForm(forms.ModelForm):
    class Meta:
        model  = models.GlobalPostFilter
        exclude = ('user', 'organization')

class UserSearchForm(forms.Form):
    name = forms.CharField(required=False)

class TagSearchForm(forms.Form):
    name = forms.CharField(required=False)





