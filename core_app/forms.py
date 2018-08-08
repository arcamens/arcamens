from django.utils.translation import ugettext_lazy as _
from group_app.forms import ConfirmGroupDeletionForm
from slock.forms import SetPasswordForm
from core_app.models import User
from sqlike.forms import SqLikeForm
from card_app.models import Card
from django.conf import settings
from django import forms
from . import models
import site_app.forms
import datetime

class OrganizationForm(forms.Form):
    name = forms.CharField(help_text='Example: Your business name.')

class ConfirmOrganizationDeletionForm(ConfirmGroupDeletionForm):
    name = forms.CharField(required=True,
    help_text='Type the organization name to confirm!')

class RemoveUserForm(forms.Form):
    reason = forms.CharField(required=False, help_text='You are fired!')

class UserSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, help_text='tag:developer')

class TagSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, help_text='Example: developer')

class OrganizationInviteForm(forms.Form):
    email = forms.EmailField(help_text="Insert user E-mail.")

class ShoutForm(forms.Form):
    msg = forms.CharField(required=False)

class UserForm(forms.ModelForm):
    class Meta:
        model  = models.User
        fields = ('name', 'avatar', 'email', 'description')

class UserFilterForm(SqLikeForm, forms.ModelForm):
    class Meta:
        model  = models.UserFilter
        exclude = ('user', 'organization')

class TagForm(forms.ModelForm):
    class Meta:
        model  = models.Tag
        exclude = ('organization', )

class UpdateOrganizationForm(forms.ModelForm):
    class Meta:
        model = models.Organization
        fields = ( 'name', )

class SignupForm(SetPasswordForm):
    class Meta:
        model   = models.User
        exclude = ('organizations', 'default', 
        'enabled', 'tags', 'c_storage', 'c_download',
        'expiration', 'max_users', 'paid')

class NodeFilterForm(forms.ModelForm):
    class Meta:
        model  = models.NodeFilter
        exclude = ('user', 'organization')

class EventFilterForm(forms.ModelForm):
    class Meta:
        model  = models.EventFilter
        exclude = ('user', 'organization')
        widgets = {
            'start': forms.SelectDateWidget(),
            'end': forms.SelectDateWidget()
        }

    def clean(self):
        super(EventFilterForm, self).clean()
        start = self.cleaned_data.get('start')
        end   = self.cleaned_data.get('end')
    
        if start > end:
            raise forms.ValidationError(("Invalid date!"
                "Start has to be lesser than end").format())

class FileAttachment:
    """
    We have to set different file size upload limits.
    One for free plans one for paid plans eventually.
    """
    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super(FileAttachment, self).__init__(*args, **kwargs)

    def clean(self):
        super(FileAttachment, self).clean()
        file        = self.cleaned_data.get('file')
        max_storage = settings.PAID_STORAGE_LIMIT\
        if self.user.default.owner.paid else settings.FREE_STORAGE_LIMIT

        # The max storage value is calculated based on the number of users
        # that the user default organization account has.
        max_storage = max_storage * self.user.default.owner.max_users
        max_file    = settings.PAID_MAX_FILE_SIZE\
        if self.user.default.owner.paid else settings.FREE_MAX_FILE_SIZE 

        if file.size > max_file:
            raise forms.ValidationError("File too big! \
                Check your upload limits")
        elif file.size + self.user.default.owner.c_storage > max_storage:
            raise forms.ValidationError("It overrides your \
                max montly storage. Check your upload limits ")
        
    def save(self, *args, **kwargs):
        file = self.cleaned_data.get('file')
        c_storage = self.user.default.owner.c_storage + file.size
        self.user.default.owner.c_storage = c_storage
        self.user.default.owner.save()
        return super(FileAttachment, self).save(*args, **kwargs)




