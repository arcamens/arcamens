from django.conf.urls import re_path, include
from . import views

app_name = 'cash_app'
urlpatterns = [
    re_path('upgrade/', views.Upgrade.as_view(), name='upgrade'),
    re_path('paypal-manual-payment/', views.PaypalManualPayment.as_view(), name='paypal-manual-payment'),
    re_path('custom-payment/', views.CustomPayment.as_view(), name='custom-payment'),
    re_path('paypal-ipn/', views.PayPalIPN.as_view(), name='paypal-ipn'),
    re_path('custom-payment/', views.CustomPayment.as_view(), name='custom-payment'),
    re_path('confirm-downgrade-free/', views.ConfirmDowngradeFree.as_view(), name='confirm-downgrade-free'),
    re_path('downgrade-free/', views.DowngradeFree.as_view(), name='downgrade-free'),
    re_path('calculate-period-cost/', views.CalculatePeriodCost.as_view(), name='calculate-period-cost'),
]




