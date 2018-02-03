from paybills.submitters import ManualForm, SubscriptionForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from core_app.models import Organization, OrganizationService
from django.core.mail import send_mail
from django.conf import settings
from core_app.models import User
from site_app.models import PasswordTicket
from slock.views import AuthenticatedView, LogoutView, LoginView
from slock.forms import LoginForm
import paybills.views
from . import forms
import timeline_app
import datetime
import time
import random

class Index(LoginView):
    def get(self, request):
        return render(request, 'site_app/index.html', 
        {'form':LoginForm()})

class LoggedOut(View):
    def get(self, request):
        return render(request, 'site_app/logged-out.html', 
        {})

class Home(LoginView):
    def get(self, request):
        return render(request, 'site_app/home.html')

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
        form = forms.UserForm()
        return render(request, 'site_app/signup.html', 
        {'form': form,})

    def post(self, request):
        """
        This is called after the user has filled the user fields
        and picked up a plan. The plan can be created on the fly
        or just be fixed(in case we decide futurely change how we
        charge on opus). 
        """
        form = forms.UserForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, 'site_app/signup.html', 
                {'form': form}, status=400)

        # Save the user record. The Service model
        # has a field named enabled, it is False for default
        # unless it is a free plan whose record is created by us.
        record         = form.save(commit=False)
        service        = OrganizationService.objects.get(paid=False)
        record.service = service
        record.enabled = True

        record.save()
        organization   = Organization.objects.create(name='Main', owner=record)
        record.default = organization
        record.organizations.add(organization)
        record.save()

        request.session['user_id'] = record.id

        return redirect('site_app:upgrade')

class Upgrade(AuthenticatedView):
    def get(self, request):
        form = forms.ServiceForm()
        return render(request, 'site_app/upgrade.html', 
        {'form':form})

class ManualPayment(AuthenticatedView):
    """
    Users just make use of submmiters to start
    the payment process. It allows a high level of
    flexibility on how to customize the offering of
    products.
    """

    def get(self, request):
        form = forms.ServiceForm()
        return render(request, 'site_app/manual-payment.html', 
        {'form':form})

    def post(self, request):
        form = forms.ServiceForm(request.POST)

        if not form.is_valid():
            return render(request, 
                'site_app/manual-payment.html', {
                     'form':form}, status=400)

        # Fields that are related to generating the
        # html form. 
        service, _ = OrganizationService.objects.get_or_create(
        max_users=form.cleaned_data['max_users'], paid=True)
        user = User.objects.get(id=self.user_id)

        payload = {
        'item_name': "Organization",
        'currency_code': 'EUR',
        'amount': service.max_users * 1,
        'quantity': 1,
        'shopping_url': 'http://opus.test.splittask.net:61001',
        'return': 'http://opus.test.splittask.net:61001',
        'cancel_return': 'http://opus.test.splittask.net:61001',
        'image_url': 'http://FIXME.gif',
        'no_shipping': '1'}

        manual = ManualForm(user, service, payload)
        return HttpResponse(manual)

class SubscriptionPayment(AuthenticatedView):
    def get(self, request):
        form = forms.ServiceForm()
        return render(request, 'site_app/subscription-payment.html', 
        {'form':form})

    def post(self, request):
        form = forms.ServiceForm(request.POST)

        if not form.is_valid():
            return render(request, 
                'site_app_app/subscription-payment.html', {
                     'form':form}, status=400)

        service, _ = OrganizationService.objects.get_or_create(
        max_users=form.cleaned_data['max_users'], paid=True)
        user = User.objects.get(id=self.user_id)

        # Ommited now for getting payments delivered 
        # instantenously.
        # delta = (datetime.date.today() - user.expiration)
        # delta = max(delta.days, 90)

        payload = {
       'item_name': "Organization",
       'src': 1,
       'currency_code': 'EUR',
       'shopping_url': 'http://opus.test.splittask.net:61001',
       'return': 'http://opus.test.splittask.net:61001',
       'cancel_return': 'http://opus.test.splittask.net:61001',
       'image_url': 'http://FIXME.gif',
       'no_shipping': '1',
       'a3': service.max_users * 1,
       'p3': 30,
       't3': 'D',
       # 't1': 'D',
       # 'a1':0,
       # 'p1': delta
        }
    
        subscription = SubscriptionForm(user, service, payload)
        return HttpResponse(subscription)

class PayPalIPN(paybills.views.PayPalIPN):
    """
    When a payment is made it calls on_success method
    regardless whether it is a subscription or manual.
    """

    def on_success(self, data, user, service):
        """
        Users should override this method to perform
        actions when payments are made.

        Services that should be enabled for a given
        period of time should increase its service timeout
        value here.

        The timeout procedure for a service should be implemented
        on its own, it shouldnt be implemented in register_app for
        avoiding loss of flexibility.
        """

        user.enabled = True

        # When the payment is made, we just upgrade
        # the user service from free to paid.
        user.service = service
        user.save()

    def on_manual_payment(self, data, user, service):
        """
        """
        print('Manual payment happened!')

    def on_subscription_signup(self, data, user, service):
        """
        """
        print('User subscribed!')

    def on_subscription_payment(self, data, user, service):
        print('User subscription payment!')


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
        user = timeline_app.models.User.objects.get(email = email)

        token = 'invite%s%s' % (random.randint(1000, 10000), time.time())

        ticket = PasswordTicket.objects.create(token=token, user=user)

        url = reverse('site_app:redefine-password', kwargs={
        'user_id': user.id, 'token': token})

        url = '%s%s' % (settings.LOCAL_ADDR, url)

        send_mail('Account recover %s' % user.name,
        '%s' % url, settings.EMAIL_HOST_USER, [email],
        fail_silently=False)

        return render(request, 'site_app/recover-mail-sent.html', 
        {'form': form})

class RedefinePassword(LoginView):
    def get(self, request, user_id, token):
        user = timeline_app.models.User.objects.get(id = user_id)
        form   = forms.RedefinePasswordForm()

        return render(request, 'site_app/redefine-password.html', 
        {'user': user, 'form': form, 'token': token})

    def post(self, request, user_id, token):
        # First attempt to grab the ticket
        # if it doesnt then it just throws an inter server error.
        user   = timeline_app.models.User.objects.get(id = user_id)
        ticket = PasswordTicket.objects.filter(user=user)
        form   = forms.RedefinePasswordForm(request.POST)

        # The logic to check if password matches should be handled
        # in the RedefinePasswordForm.
        if not form.is_valid():
            return render(request, 'site_app/redefine-password.html',
                 {'form': form, 'user': user, 'token': token})

        # Delete all password redefinition tickets.
        ticket.delete()

        # Redefine the password.
        user.password = form.cleaned_data['password']
        user.save()

        # Log the user.
        request.session['user_id'] = user.id

        # Redirect to the application.
        return redirect('core_app:index')






