from django.conf.urls import re_path
from . import views

app_name = 'feedback_app'
urlpatterns = [
    re_path('create-feedback/(?P<event_id>.+)/', views.CreateFeedback.as_view(), name='create-feedback'),
]























