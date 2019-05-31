from django.conf.urls import re_path
from . import views

app_name = 'bitbucket_app'
urlpatterns = [
    re_path('bitbucket-handle/', views.BitbucketHandle.as_view(), name='bitbucket-handle'),
    re_path('create-bitbucket-hook/', views.CreateBitbucketHook.as_view(), name='create-bitbucket-hook'),
    re_path('list-bitbucket-hooks/', views.ListBitbucketHooks.as_view(), name='list-bitbucket-hooks'),
    re_path('delete-bitbucket-hook/(?P<hook_id>.+)/', views.DeleteBitbucketHook.as_view(), name='delete-bitbucket-hook'),

]












