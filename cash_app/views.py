from paybills.submitters import ManualForm
from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import HttpResponse
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

# Create your views here.
class CustomPayment(AuthenticatedView):
    """
    """

    def get(self, request):
        return render(request, 'cash_app/custom-payment.html', {})

class Upgrade(AuthenticatedView):
    def get(self, request):
        items = self.me.items.all().order_by('-created')

        return render(request, 'cash_app/upgrade.html', 
        {'items': items, 'me': self.me, 'CURRENCY_CODE': settings.CURRENCY_CODE})

class ConfirmDowngradeFree(AuthenticatedView):
    def get(self, request):
        users   = User.objects.filter(organizations__owner__id=self.me.id)
        users   = users.distinct()
        n_users = users.count()

        # if not me.paid:
            # return HttpResponse('Your plan is already free!', status=403)

        return render(request, 'cash_app/confirm-downgrade-free.html', 
        {'n_users':n_users, 'me': self.me, 'settings': settings})

class DowngradeFree(AuthenticatedView):
    def get(self, request):
        users   = User.objects.filter(organizations__owner__id=self.me.id)
        users   = users.distinct()
        n_users = users.count()

        if n_users > settings.FREE_MAX_USERS:
            return render(request, 'cash_app/downgrade-free-max-users-error.html', 
                {'me': self.me, 'n_users':n_users}, status=403)

        if self.me.expiration > datetime.date.today():
            return render(request, 'cash_app/downgrade-free-expiration-error.html', 
                {'me': self.me, 'n_users':n_users}, status=403)

        period = Period.objects.create(paid=False, total=0, user=self.me)
        self.me.max_users  = period.max_users
        self.me.expiration = period.expiration
        self.me.paid       = period.paid
        self.me.save()

        return render(request, 'cash_app/downgrade-free-success.html', {})

class CalculatePeriodCost(AuthenticatedView):
    def post(self, request):
        form = forms.PeriodForm(request.POST, 
            max_users=self.me.max_users, expiration=self.me.expiration)

        if not form.is_valid():
            return render(request, 
                'cash_app/paypal-manual-payment.html', {'form':form, 
                    'me': self.me, 'settings':settings}, status=400)

        now  = datetime.date.today()
        init = self.me.expiration if self.me.expiration and self.me.expiration > now else now
        d0   = init - now
        rate = settings.USER_COST/30.0
        cash = rate * d0.days * self.me.max_users 
        d1   = form.cleaned_data['expiration'] - now
        cost = form.cleaned_data['max_users'] * rate * d1.days - cash
        cost = round(cost, 3)

        return render(request, 'cash_app/paypal-manual-payment.html', 
        {'form':form, 'me': self.me, 'cost': cost, 'settings':settings, })

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
        form = forms.PeriodForm(initial={'max_users': self.me.max_users,
        'expiration': self.me.expiration})

        return render(request, 'cash_app/paypal-manual-payment.html', 
        {'form':form, 'me': self.me, 'settings':settings})

    def post(self, request):
        form = forms.PeriodForm(request.POST, 
            max_users=self.me.max_users, expiration=self.me.expiration)

        # I need to check if the user has decreased the max_users
        # value to a smaller value than its total account users.
        # If so then he has to remove users for decreasing its max_users
        # value.
        if not form.is_valid():
            return render(request, 
                'cash_app/paypal-manual-payment.html', {'form':form, 
                    'me': self.me, 'settings':settings, }, status=400)

        record      = form.save(commit=False)
        record.paid = True
        record.user = self.me

        now  = datetime.date.today()
        init = self.me.expiration if self.me.expiration and self.me.expiration > now else now
        d0   = init - now
        rate = settings.USER_COST/30.0 
        cash = rate * d0.days * self.me.max_users 
        d1   = form.cleaned_data['expiration'] - now
        cost = form.cleaned_data['max_users'] * rate * d1.days - cash
        cost = round(cost, 3)

        record.total = cost
        record.save()

        # Fields that are related to generating the
        # html form. 
        payload = {
        'item_name': "Arcamens Period",
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
        manual = ManualForm(self.me, record, payload)
        return HttpResponse(manual)

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


