from django.utils.translation import ugettext_lazy as _
from django import forms
from . import models
import site_app.forms

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()

    def __init__(self, request, *args, **kwargs):
        # important to "pop" added kwarg before call to parent's constructor
        self.request = request
        super(LoginForm, self).__init__(request, *args, **kwargs)

    def clean(self):
        super(LoginForm, self).clean()

        try:
            user = models.User.objects.get(email = email, 
                organization__name=organization, password=password)
        except Exception as e:
            raise forms.ValidationError(
                'User doesnt exist!')
        else:
            self.request.session['user_id'] = user.id

class OrganizationForm(forms.Form):
    name = forms.CharField()

class UpdateOrganizationForm(forms.ModelForm):
    class Meta:
        model = models.Organization
        fields = ('owner', 'name')

class UserSearchForm(forms.Form):
    pattern = forms.CharField(required=False)

class EventSearchForm(forms.Form):
    pattern = forms.CharField()
    seen = forms.BooleanField(required=False)

class TagForm(forms.ModelForm):
    class Meta:
        model  = models.Tag
        exclude = ('organization', )

class BindTagForm(forms.Form):
    name = forms.CharField()

class TagSearchForm(forms.Form):
    name = forms.CharField(required=False)

# site_app should inherit from here.
class UserForm(site_app.forms.UserForm):
    class Meta:
        model   = models.User
        fields = ('name', 'avatar', 'email')

class BindUsersForm(forms.Form):
    email = forms.EmailField()
    admin = forms.BooleanField(required=False)




