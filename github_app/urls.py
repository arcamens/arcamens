from django.conf.urls import re_path
from . import views

app_name = 'github_app'
urlpatterns = [
    re_path('github-handle/', views.GithubHandle.as_view(), name='github-handle'),
    re_path('create-github-hook/', views.CreateGithubHook.as_view(), name='create-github-hook'),
    re_path('list-github-hooks/', views.ListGithubHooks.as_view(), name='list-github-hooks'),
    re_path('delete-github-hook/(?P<hook_id>.+)/', views.DeleteGithubHook.as_view(), name='delete-github-hook'),

]













