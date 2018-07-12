from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^upgrade/', views.Upgrade.as_view(), name='upgrade'),
    url(r'^paypal-manual-payment/', views.PaypalManualPayment.as_view(), name='paypal-manual-payment'),
    url(r'^custom-payment/', views.CustomPayment.as_view(), name='custom-payment'),
    url(r'^paypal-ipn/', views.PayPalIPN.as_view(), name='paypal-ipn'),
    url(r'^custom-payment/', views.CustomPayment.as_view(), name='custom-payment'),
    url(r'^confirm-downgrade-free/', views.ConfirmDowngradeFree.as_view(), name='confirm-downgrade-free'),
    url(r'^downgrade-free/', views.DowngradeFree.as_view(), name='downgrade-free'),
    url(r'^calculate-period-cost/', views.CalculatePeriodCost.as_view(), name='calculate-period-cost'),
]




