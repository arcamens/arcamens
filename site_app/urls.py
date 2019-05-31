from django.conf.urls import re_path, include
from . import views

app_name = 'site_app'
urlpatterns = [
    re_path('index/', views.Index.as_view(), name='index'),
    re_path('logged-out/', views.LoggedOut.as_view(), name='logged-out'),
    re_path('help/', views.Help.as_view(), name='help'),
    re_path('login/', views.Login.as_view(), name='login'),
    re_path('logout/', views.Logout.as_view(), name='logout'),
    re_path('signup/', views.SignUp.as_view(), name='signup'),
    re_path('recover-account/', views.RecoverAccount.as_view(), name='recover-account'),
    re_path('redefine-password/(?P<user_id>.+)/(?P<token>.+)/', views.RedefinePassword.as_view(), name='redefine-password'),
    re_path('enable-account/(?P<user_id>.+)/(?P<token>.+)/', views.EnableAccount.as_view(), name='enable-account'),

]




