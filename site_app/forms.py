from django import forms
import core_app.models

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(LoginForm, self).clean()
        email    = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        try:
            user = core_app.models.User.objects.get(
                email = email, password=password)
        except Exception as e:
            raise forms.ValidationError(
                'User or password is wrong!')
        else:
            self.session['user_id'] = user.id

# class LoginForm(forms.Form):
    # email    = forms.EmailField()
    # password = forms.CharField()

class SignupForm(forms.Form):
    name         = forms.CharField()
    email        = forms.EmailField()
    password     = forms.CharField()
    organization = forms.CharField()

# class UserForm(forms.ModelForm):
    # class Meta:
        # model   = core_app.models.User
        # exclude = ('organizations', 'default', 'service', 'expiration')

class ServiceForm(forms.Form):
    max_users = forms.IntegerField()
    # paid = forms.BooleanField(required=False)





