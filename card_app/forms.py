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

class ForkForm(forms.ModelForm):
    class Meta:
        model  = models.Fork
        fields = ('label', 'data')

class UserSearchForm(forms.Form):
    pattern = forms.CharField(required=False)

class CardSearchForm(forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Ex: Label + Owner + #tag0 + #tag1..')
    done = forms.BooleanField(required=False)

class TagSearchForm(forms.Form):
    name = forms.CharField(required=False)

class GlobalCardFilterForm(forms.ModelForm):
    class Meta:
        model  = models.GlobalCardFilter
        exclude = ('user', 'organization')








