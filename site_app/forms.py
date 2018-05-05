from slock.forms import SetPasswordForm
from captcha.fields import ReCaptchaField
from django import forms
import core_app.models
from django.conf import settings

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
    captcha = ReCaptchaField()

    class Meta:
        model   = core_app.models.User
        exclude = ('organizations', 'default', 
        'expiration', 'max_users', 'paid')

class ServiceForm(forms.Form):
    max_users = forms.IntegerField()
    expiration = forms.DateField()

    # paid = forms.BooleanField(required=False)

class PeriodForm(forms.ModelForm):
    expiration = forms.DateField(widget=forms.SelectDateWidget())

    def __init__(self, *args, max_users=None, expiration=None, **kwargs):
        self.max_users  = max_users
        self.expiration = expiration
        super(PeriodForm, self).__init__(*args, **kwargs)

    class Meta:
        model   = core_app.models.Period
        exclude = ('user', 'price', 'total', 'paid')

    def clean(self):
        super().clean()

        if self.errors:
            return

        max_users = self.cleaned_data.get('max_users')
        if max_users <= settings.FREE_MAX_USERS:
            raise forms.ValidationError("That is a free plan.")
        elif max_users < self.max_users:
            raise forms.ValidationError("Max users can't be \
                smaller than your account members number!")

        expiration = self.cleaned_data.get('expiration')
        if expiration <= datetime.date.today():
            raise forms.ValidationError("That is not a valid date.")
        elif self.expiration and expiration < self.expiration:
            raise forms.ValidationError("Expiration can't be \
                smaller than your current expiration!")
        elif self.expiration and expiration == self.expiration and max_users == self.max_users:
            raise forms.ValidationError("Either increase the number of users \
                or increase expiration date!")


