from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^index/', views.Index.as_view(), name='index'),
    url(r'^home/', views.Home.as_view(), name='home'),
    url(r'^help/', views.Help.as_view(), name='help'),
    url(r'^login/', views.Login.as_view(), name='login'),
    url(r'^logout/', views.Logout.as_view(), name='logout'),
    url(r'^signup/', views.SignUp.as_view(), name='signup'),
    url(r'^upgrade/', views.Upgrade.as_view(), name='upgrade'),
    url(r'^manual-payment/', views.ManualPayment.as_view(), name='manual-payment'),
    url(r'^subscription-payment/', views.SubscriptionPayment.as_view(), name='subscription-payment'),
    url(r'^paypal-ipn/', views.PayPalIPN.as_view(), name='paypal-ipn'),

]






