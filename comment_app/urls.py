from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^list-comments/(?P<event_id>.+)/', views.ListComments.as_view(), name='list-comments'),
    url(r'^e-create-comment/(?P<event_id>.+)/', views.ECreateComment.as_view(), name='e-create-comment'),
    url(r'^create-comment/(?P<event_id>.+)/', views.CreateComment.as_view(), name='create-comment'),
]






















