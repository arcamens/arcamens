from django.views.generic.base import RedirectView
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^update-uuid/', views.UpdateUuid.as_view(),  name='update-uuid'),

]






