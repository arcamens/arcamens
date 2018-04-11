from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^bitbucket-handle/', views.BitbucketHandle.as_view(), name='bitbucket-handle'),
]










