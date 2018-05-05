from paybills.submitters import ManualForm, SubscriptionForm
from core_app.models import Organization
from slock.views import AuthenticatedView, LogoutView, LoginView
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
        return render(request, 
        'site_app/logged-out.html', {})

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
        {'form': form,})

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
                {'form': form}, status=400)

        # Save the user record. The Service model
        # has a field named enabled, it is False for default
        # unless it is a free plan whose record is created by us.
        record         = form.save(commit=False)
        # record.enabled = True

        record.save()
        organization   = Organization.objects.create(name='Main', owner=record)
        record.default = organization
        record.organizations.add(organization)
        record.save()

        process = RegisterProcess.objects.create(user=record)

        return render(request, 
            'site_app/confirm-email.html', {'user': record})

class EnableAccount(View):
    def get(self, request, user_id, token):
        process = RegisterProcess.objects.get(user__id=user_id, token=token)
        process.user.enabled = True
        process.user.save()
        process.delete()

        request.session['user_id'] = user_id
        return redirect('core_app:index')

class CustomPayment(AuthenticatedView):
    """
    """

    def get(self, request):
        return render(request, 'site_app/custom-payment.html', {})

class Upgrade(AuthenticatedView):
    def get(self, request):
        me    = User.objects.get(id=self.user_id)
        items = me.items.all().order_by('-created')

        return render(request, 'site_app/upgrade.html', 
        {'items': items, 'me': me, 'CURRENCY_CODE': settings.CURRENCY_CODE})

class ConfirmDowngradeFree(AuthenticatedView):
    def get(self, request):
        me      = User.objects.get(id=self.user_id)
        n_users = me.n_acc_users()

        # if not me.paid:
            # return HttpResponse('Your plan is already free!', status=403)

        return render(request, 'site_app/confirm-downgrade-free.html', 
        {'n_users':n_users, 'me': me, 'settings': settings})

class DowngradeFree(AuthenticatedView):
    def get(self, request):
        me      = User.objects.get(id=self.user_id)
        n_users = me.n_acc_users()

        if n_users > settings.FREE_MAX_USERS:
            return render(request, 'site_app/downgrade-free-max-users-error.html', 
                {'me': me, 'n_users':n_users}, status=403)

        if me.expiration > datetime.date.today():
            return render(request, 'site_app/downgrade-free-expiration-error.html', 
                {'me': me, 'n_users':n_users}, status=403)

        period        = Period.objects.create(paid=False, total=0, user=me)
        me.max_users  = period.max_users
        me.expiration = period.expiration
        me.paid       = period.paid
        me.save()

        return render(request, 'site_app/downgrade-free-success.html', {})

class CalculatePeriodCost(AuthenticatedView):
    def post(self, request):
        me   = User.objects.get(id=self.user_id)
        form = forms.PeriodForm(request.POST, 
            max_users=me.max_users, expiration=me.expiration)

        if not form.is_valid():
            return render(request, 
                'site_app/paypal-manual-payment.html', {'form':form, 
                    'me': me, 'USER_COST':settings.USER_COST, 'CURRENCY_CODE': settings.CURRENCY_CODE}, status=400)

        now  = datetime.date.today()
        init = me.expiration if me.expiration and me.expiration > now else now
        d0   = init - now
        rate = settings.USER_COST/30.0
        cash = rate * d0.days * me.max_users 
        d1   = form.cleaned_data['expiration'] - now
        cost = form.cleaned_data['max_users'] * rate * d1.days - cash
        cost = round(cost, 3)

        return render(request, 'site_app/paypal-manual-payment.html', 
        {'form':form, 'me': me, 'cost': cost, 'USER_COST':settings.USER_COST, 'CURRENCY_CODE': settings.CURRENCY_CODE})

class PaypalManualPayment(AuthenticatedView):
    """
    Users just make use of submmiters to start
    the payment process. It allows a high level of
    flexibility on how to customize the offering of
    products.
    """

    def get(self, request):
        # We should check if user has some payment process going on
        # so we avoid receiving twice.
        me   = User.objects.get(id=self.user_id)
        form = forms.PeriodForm(initial={'max_users': me.max_users,
        'expiration': me.expiration})

        return render(request, 'site_app/paypal-manual-payment.html', 
        {'form':form, 'me': me, 'USER_COST':settings.USER_COST, 'CURRENCY_CODE': settings.CURRENCY_CODE})

    def post(self, request):
        me   = User.objects.get(id=self.user_id)
        form = forms.PeriodForm(request.POST, 
            max_users=me.max_users, expiration=me.expiration)

        # I need to check if the user has decreased the max_users
        # value to a smaller value than its total account users.
        # If so then he has to remove users for decreasing its max_users
        # value.
        if not form.is_valid():
            return render(request, 
                'site_app/paypal-manual-payment.html', {'form':form, 
                    'me': me, 'USER_COST':settings.USER_COST, 'CURRENCY_CODE': settings.CURRENCY_CODE}, status=400)

        record      = form.save(commit=False)
        record.paid = True
        record.user = me

        now  = datetime.date.today()
        init = me.expiration if me.expiration and me.expiration > now else now
        d0   = init - now
        rate = settings.USER_COST/30.0 
        cash = rate * d0.days * me.max_users 
        d1   = form.cleaned_data['expiration'] - now
        cost = form.cleaned_data['max_users'] * rate * d1.days - cash
        cost = round(cost, 3)

        record.total = cost
        record.save()

        # Fields that are related to generating the
        # html form. 
        payload = {
        'item_name': "Splittask Period",
        'currency_code': settings.CURRENCY_CODE,
        'amount': cost,
        'quantity': 1,
        'shopping_url': 'https://staging.arcamens.com',
        'return': 'https://staging.arcamens.com',
        'cancel_return': 'https://staging.arcamens.com',
        # 'image_url': 'http://FIXME.gif',
        'no_shipping': '1'}

        # The product that is being sold is cached.
        # When the manual payment happens then it retrieves
        # the product it was bought and update the user account
        # attributes. These are expiration, max_users.
        manual = ManualForm(me, record, payload)
        return HttpResponse(manual)

# class SubscriptionPayment(AuthenticatedView):
    # def get(self, request):
        # form = forms.ServiceForm()
        # return render(request, 'site_app/subscription-payment.html', 
        # {'form':form})
# 
    # def post(self, request):
        # form = forms.ServiceForm(request.POST)
# 
        # if not form.is_valid():
            # return render(request, 
                # 'site_app_app/subscription-payment.html', {
                     # 'form':form}, status=400)
# 
        # service, _ = OrganizationService.objects.get_or_create(
        # max_users=form.cleaned_data['max_users'], paid=True)
        # user = User.objects.get(id=self.user_id)
# 
        # # Ommited now for getting payments delivered 
        # # instantenously.
        # # delta = (datetime.date.today() - user.expiration)
        # # delta = max(delta.days, 90)
# 
        # payload = {
       # 'item_name': "Organization",
       # 'src': 1,
       # 'currency_code': 'EUR',
       # 'shopping_url': 'http://opus.test.splittask.net:61001',
       # 'return': 'http://opus.test.splittask.net:61001',
       # 'cancel_return': 'http://opus.test.splittask.net:61001',
       # 'image_url': 'http://FIXME.gif',
       # 'no_shipping': '1',
       # 'a3': service.max_users * 1,
       # 'p3': 30,
       # 't3': 'D',
       # # 't1': 'D',
       # # 'a1':0,
       # # 'p1': delta
        # }
    # 
        # subscription = SubscriptionForm(user, service, payload)
        # return HttpResponse(subscription)

class PayPalIPN(paybills.views.PayPalIPN):
    """
    When a payment is made it calls on_success method
    regardless whether it is a subscription or manual.
    """

    def on_success(self, data, user, item):
        """
        Users should override this method to perform
        actions when payments are made.

        Periods that should be enabled for a given
        period of time should increase its service timeout
        value here.

        The timeout procedure for a service should be implemented
        on its own, it shouldnt be implemented in register_app for
        avoiding loss of flexibility.
        """
    
        # If the payment in fact happens then the user
        # acquired the product so we update the user account
        # attributes regarding the product.
        user.enabled    = True
        user.max_users  = item.period.max_users
        user.expiration = item.period.expiration
        user.paid       = item.period.paid

        print('Setting user attributes on PaypalIPN')
        print('User:', user.name)
        print('Max users:', user.max_users)
        print('Expiration:', user.expiration)
        print('Paid:', user.paid)

        user.save()

    def on_manual_payment(self, data, user, item):
        """
        """
        print('Manual payment happened!')

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
        '%s' % url, 'noreply@arcamens.com', [email],
        fail_silently=False)

        return render(request, 'site_app/recover-mail-sent.html', 
        {'form': form})

class RedefinePassword(LoginView):
    def get(self, request, user_id, token):
        user = timeline_app.models.User.objects.get(id = user_id)
        form = SetPasswordForm()

        return render(request, 'site_app/redefine-password.html', 
        {'user': user, 'form': form, 'token': token})

    def post(self, request, user_id, token):
        # First attempt to grab the ticket
        # if it doesnt then it just throws an inter server error.
        user   = timeline_app.models.User.objects.get(id = user_id)
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








