from django import forms
import core_app.models

class SignupForm(forms.Form):
    name         = forms.CharField()
    email        = forms.EmailField()

    password     = forms.CharField()
    organization = forms.CharField()

class RecoverAccountForm(forms.Form):
    email = forms.EmailField()

    def clean(self):
        super(RecoverAccountForm, self).clean()
        email = self.cleaned_data.get('email')

        try:
            user = core_app.models.User.objects.get(
                email = email)
        except Exception as e:
            raise forms.ValidationError(
                "This user doesn't exist!")

class UserForm(forms.ModelForm):
    retype = forms.CharField(label='Retype password', 
    widget=forms.PasswordInput)

    class Meta:
        model   = core_app.models.User
        exclude = ('organizations', 'default', 
        'service', 'expiration')

        widgets = {
        'password': forms.PasswordInput()}

    def clean(self):
        super(UserForm, self).clean()
        retype   = self.cleaned_data.get('retype')
        password = self.cleaned_data.get('password')

        if retype != password:
            raise forms.ValidationError(
                'Passwords dont match!')

class ServiceForm(forms.Form):
    max_users = forms.IntegerField()
    # paid = forms.BooleanField(required=False)


class RedefinePasswordForm(forms.Form):
    password = forms.CharField()
    retype   = forms.CharField()














