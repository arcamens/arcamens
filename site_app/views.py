from paybills.submitters import ManualForm, SubscriptionForm
from core_app.models import Organization
from slock.views import LogoutView, LoginView
from slock.forms import SetPasswordForm
from django.shortcuts import render, redirect
from site_app.models import PasswordTicket, RegisterProcess
from django.core.mail import send_mail
from django.views.generic import View
from django.http import HttpResponse
from slock.forms import LoginForm
from django.urls import reverse
from django.conf import settings
from core_app.models import User
from core_app.views import AuthenticatedView
import paybills.views
from . import forms
import group_app
import datetime
import time
import random

class Index(LoginView):
    def get(self, request):
        return render(request, 'site_app/index.html', 
        {'form':LoginForm()})

class LoggedOut(View):
    def get(self, request):
        return render(request, 'site_app/logged-out.html', {'settings': settings})

class Help(View):
    def get(self, request):
        return render(request, 'site_app/help.html')

class Login(LoginView):
    """
    """

    def get(self, request):
        return render(request, 'site_app/index.html', 
        {'form':LoginForm()})

    def post(self, request):
        form = LoginForm(request.session, request.POST)

        if not form.is_valid():
            return render(request, 'site_app/index.html',
                        {'form': form})

        return redirect('core_app:index')

class Logout(LogoutView):
    """
    """

class SignUp(LoginView):
    """
    """

    def get(self, request):
        form = forms.SignupForm()
        return render(request, 'site_app/signup.html', 
        {'form': form, 'settings': settings})

    def post(self, request):
        """
        This is called after the user has filled the user fields
        and picked up a plan. The plan can be created on the fly
        or just be fixed(in case we decide futurely change how we
        charge on opus). 
        """
        form = forms.SignupForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, 'site_app/signup.html', 
                {'form': form, 'settings': settings}, status=400)

        record = form.save()
        process = RegisterProcess.objects.create(user=record)

        # Authenticates the user afterwards so
        # he can resend email confirmation etc.
        request.session['user_id'] = record.id

        return render(request, 
            'site_app/confirm-email.html', {'user': record})

class EnableAccount(View):
    def get(self, request, user_id, token):
        process = RegisterProcess.objects.get(user__id=user_id, token=token)
        process.user.enabled = True
        process.user.save()
        process.delete()
    
        # Create the free period record.
        period = Period.objects.create(paid=False, total=0, user=self.me)

        request.session['user_id'] = user_id
        return redirect('core_app:index')

class RecoverAccount(LoginView):
    def get(self, request):
        form = forms.RecoverAccountForm()
        return render(request, 'site_app/recover-account.html', 
        {'form': form})

    def post(self, request):
        form = forms.RecoverAccountForm(request.POST)

        if not form.is_valid():
            return render(request, 'site_app/recover-account.html',
                        {'form': form})

        email = form.cleaned_data['email']
        user = group_app.models.User.objects.get(email = email)

        token = 'invite%s%s' % (random.randint(1000, 10000), time.time())

        ticket = PasswordTicket.objects.create(token=token, user=user)

        url = reverse('site_app:redefine-password', kwargs={
        'user_id': user.id, 'token': token})

        url = '%s%s' % (settings.LOCAL_ADDR, url)

        send_mail('Account recover %s' % user.name,
        '%s' % url, 'noreply@arcamens.com', [email],
        fail_silently=False)

        return render(request, 'site_app/recover-mail-sent.html', 
        {'form': form})

class RedefinePassword(LoginView):
    def get(self, request, user_id, token):
        user = group_app.models.User.objects.get(id = user_id)
        form = SetPasswordForm()

        return render(request, 'site_app/redefine-password.html', 
        {'user': user, 'form': form, 'token': token})

    def post(self, request, user_id, token):
        # First attempt to grab the ticket
        # if it doesnt then it just throws an inter server error.
        user   = group_app.models.User.objects.get(id = user_id)
        ticket = PasswordTicket.objects.filter(user=user)
        form   = SetPasswordForm(request.POST, instance=user)

        # The logic to check if password matches should be handled
        # in the RedefinePasswordForm.
        if not form.is_valid():
            return render(request, 'site_app/redefine-password.html',
                 {'form': form, 'user': user, 'token': token})

        # Delete all password redefinition tickets.
        ticket.delete()

        form.save()
        # Redefine the password.
        # user.password = form.cleaned_data['password']
        # user.save()

        # Log the user.
        request.session['user_id'] = user.id

        # Redirect to the application.
        return redirect('core_app:index')





