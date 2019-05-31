from django.utils.translation import ugettext_lazy as _
from core_app.models import Organization, User, Invite
from group_app.forms import ConfirmDeletionForm
from slock.forms import SetPasswordForm
from core_app.models import User, Membership
from sqlike.forms import SqLikeForm
from card_app.models import Card
from django.conf import settings
from django import forms
from . import models
import site_app.forms
import datetime


class ConfirmOrganizationDeletionForm(ConfirmDeletionForm):
    name = forms.CharField(required=True,
    help_text='Type the organization name to confirm!')

class RemoveUserForm(forms.Form):
    reason = forms.CharField(required=False, help_text='You are fired!')

class UserSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, help_text='tag:developer')

class TagSearchForm(SqLikeForm, forms.Form):
    pattern = forms.CharField(required=False, 
    help_text='Example: feature')

class InviteForm(forms.ModelForm):
    class Meta:
        model  = models.Invite
        fields = ('email', 'status')

    def __init__(self, *args, me=None, **kwargs):
        self.me = me
        super(InviteForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(InviteForm, self).clean()

        # It is necessary otherwise the form doesn't display errors
        # when the email is not valid.
        if self.errors: return

        email = self.cleaned_data.get('email')
        status = self.cleaned_data.get('status')
        user, _ = User.objects.get_or_create(email=email)

        # If the user is already a member then notify with an error.
        if user.organizations.filter(id=self.me.default.id).exists():
            raise forms.ValidationError("The user is already a member!")

        # If there is already an invite just tell him it was sent.
        if user.invites.filter(organization=self.me.default).exists():
            raise forms.ValidationError("The user was already invited!")

        if self.me.paid and status != '2' and self.is_max_users():
            raise forms.ValidationError('Max users limit was arrived!\
                You need to upgrade your plan!')

        self.instance.organization = self.me.default
        self.instance.peer = self.me
        self.instance.user = user

    def is_max_users(self):
        max_users = self.me.default.owner.c_acc_peers()
        return self.me.default.owner.max_users <= max_users

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

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = models.Organization
        fields = ( 'name', 'public', 'description')

    def __init__(self, *args, me=None, **kwargs):
        self.me = me
        super(OrganizationForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(OrganizationForm, self).clean()
        if not self.me.paid and not self.cleaned_data['public']:
            raise forms.ValidationError('Free accounts can have\
                just public organizatoins')

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

class MembershipForm(forms.ModelForm):
    class Meta:
        model  = models.Membership
        fields = ('status',)

    def __init__(self, *args, me=None, **kwargs):
        self.me = me
        self.old_status = kwargs['instance'].status
        super(MembershipForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(MembershipForm, self).clean()
        # Means the user attempted to change from contributor to other status.
        cond = self.old_status == '2' and ('status' in self.changed_data)
        if self.me.default.owner.paid and cond and self.is_max_users():
            raise forms.ValidationError("Can't change user\
                    status, upgrade your plan!")
    
    def is_max_users(self):
        max_users = self.me.default.owner.c_acc_peers()
        return self.me.default.owner.max_users <= max_users

class UserTagshipForm(forms.ModelForm):
    class Meta:
        model  = models.UserTagship
        fields = ()




