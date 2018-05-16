from django.views.generic.base import RedirectView
from django.conf.urls import url
from . import models

urlpatterns = [
    url(r'^update-uuid/', models.Device.update_uuid,  name='update-uuid'),

]






