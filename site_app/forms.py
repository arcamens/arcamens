from slock.forms import SetPasswordForm
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

class SignupForm(SetPasswordForm):
    class Meta:
        model   = core_app.models.User
        exclude = ('organizations', 'default', 
        'service', 'expiration')

class ServiceForm(forms.Form):
    max_users = forms.IntegerField()
    # paid = forms.BooleanField(required=False)

