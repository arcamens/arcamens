from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^github-handle/', views.GithubHandle.as_view(), name='github-handle'),
    url(r'^create-github-hook/', views.CreateGithubHook.as_view(), name='create-github-hook'),
    url(r'^list-github-hooks/', views.ListGithubHooks.as_view(), name='list-github-hooks'),
    url(r'^delete-github-hook/(?P<hook_id>.+)/', views.DeleteGithubHook.as_view(), name='delete-github-hook'),

]













