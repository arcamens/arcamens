from django import forms
import core_app.models

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

class SetPasswordForm(forms.ModelForm):
    retype = forms.CharField(required=True, widget=forms.PasswordInput())
    password = forms.CharField(required=True, widget=forms.PasswordInput())

    def clean(self):
        super(SetPasswordForm, self).clean()
        retype   = self.cleaned_data.get('retype')
        password = self.cleaned_data.get('password')

        if retype != password:
            raise forms.ValidationError(
                'Passwords dont match!')

class SignupForm(SetPasswordForm):
    class Meta:
        model   = core_app.models.User
        exclude = ('organizations', 'default', 
        'service', 'expiration')

        # widgets = {
        # 'password': forms.PasswordInput()}

class ServiceForm(forms.Form):
    max_users = forms.IntegerField()
    # paid = forms.BooleanField(required=False)


class RedefinePasswordForm(SetPasswordForm):
    class Meta:
        model  = core_app.models.User
        fields = ('password', )

