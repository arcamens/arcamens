from paybills.submitters import ManualForm, SubscriptionForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import render
from django.views.generic import View
from core_app.models import Organization, OrganizationService
from core_app.views import AuthenticatedView
from core_app.models import User
import paybills.views
from . import forms
import timeline_app
import datetime

class Index(View):
    def get(self, request):
        return render(request, 'site_app/index.html', {'login_form': forms.LoginForm(),
        'signup_form': forms.SignupForm()})

class Home(View):
    def get(self, request):
        return render(request, 'site_app/home.html')

class Help(View):
    def get(self, request):
        return render(request, 'site_app/help.html')

class Login(View):
    """
    """

    def get(self, request):
        return render(request, 'site_app/index.html', 
        {'login_form':forms.LoginForm()})

    def post(self, request):
        form = forms.LoginForm(request.session, request.POST)

        if not form.is_valid():
            return render(request, 'site_app/index.html',
                        {'login_form': form})

        # email        = form.cleaned_data['email']
        # password     = form.cleaned_data['password']
        # user         = timeline_app.models.User.objects.get(email = email, 
        # password=password)
        # request.session['user_id'] = user.id
        return redirect('core_app:index')

class Logout(View):
    """
    """

    def get(self, request):
        del request.session['user_id']
        return redirect('site_app:index')

class SignUp(View):
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
        form = forms.UserForm(request.POST)

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









