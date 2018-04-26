from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^index/', views.Index.as_view(), name='index'),
    url(r'^logged-out/', views.LoggedOut.as_view(), name='logged-out'),
    url(r'^help/', views.Help.as_view(), name='help'),
    url(r'^login/', views.Login.as_view(), name='login'),
    url(r'^logout/', views.Logout.as_view(), name='logout'),
    url(r'^signup/', views.SignUp.as_view(), name='signup'),
    url(r'^upgrade/', views.Upgrade.as_view(), name='upgrade'),
    url(r'^paypal-manual-payment/', views.PaypalManualPayment.as_view(), name='paypal-manual-payment'),
    url(r'^custom-payment/', views.CustomPayment.as_view(), name='custom-payment'),
    url(r'^paypal-ipn/', views.PayPalIPN.as_view(), name='paypal-ipn'),
    url(r'^recover-account/', views.RecoverAccount.as_view(), name='recover-account'),
    url(r'^redefine-password/(?P<user_id>.+)/(?P<token>.+)/', views.RedefinePassword.as_view(), name='redefine-password'),
    url(r'^enable-account/(?P<user_id>.+)/(?P<token>.+)/', views.EnableAccount.as_view(), name='enable-account'),

]

