from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^bitbucket-handle/', views.BitbucketHandle.as_view(), name='bitbucket-handle'),
    url(r'^create-bitbucket-hook/', views.CreateBitbucketHook.as_view(), name='create-bitbucket-hook'),
    url(r'^list-bitbucket-hooks/', views.ListBitbucketHooks.as_view(), name='list-bitbucket-hooks'),
    url(r'^delete-bitbucket-hook/(?P<hook_id>.+)/', views.DeleteBitbucketHook.as_view(), name='delete-bitbucket-hook'),

]












