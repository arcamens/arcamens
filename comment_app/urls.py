from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^list-comments/(?P<post_id>.+)/', views.ListPostComments.as_view(), name='list-comments'),
    url(r'^e-create-comment/(?P<event_id>.+)/', views.ECreatePostComment.as_view(), name='e-create-comment'),
    url(r'^create-comment/(?P<post_id>.+)/', views.CreatePostComment.as_view(), name='create-comment'),
]





















