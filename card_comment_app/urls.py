from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^list-comments/(?P<card_id>.+)/', views.ListCardComments.as_view(), name='list-comments'),
    url(r'^e-create-comment/(?P<event_id>.+)/', views.ECreateCardComment.as_view(), name='e-create-comment'),
    url(r'^create-comment/(?P<card_id>.+)/', views.CreateCardComment.as_view(), name='create-comment'),
]






















