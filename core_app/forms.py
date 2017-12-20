from django.utils.translation import ugettext_lazy as _
from django import forms
from . import models

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





