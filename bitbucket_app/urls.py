from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^bitbucket-hooker/', views.BitbucketHooker.as_view(), name='bitbucket-hooker'),
]









