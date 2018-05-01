from django.conf.urls import url
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    # url(r'^timeline/(?P<timeline_id>.+)/', views.Timeline.as_view(), name='timeline'),
    url(r'^list-posts/(?P<timeline_id>.+)/', views.ListPosts.as_view(), name='list-posts'),
    url(r'^create-timeline/(?P<organization_id>.+)', views.CreateTimeline.as_view(), name='create-timeline'),
    url(r'^update-timeline/(?P<timeline_id>.+)/', views.UpdateTimeline.as_view(), name='update-timeline'),
    url(r'^delete-timeline/(?P<timeline_id>.+)/', views.DeleteTimeline.as_view(), name='delete-timeline'),
    url(r'^paste-posts/(?P<timeline_id>.+)/', views.PastePosts.as_view(), name='paste-posts'),
    url(r'^manage-user-timelines/(?P<user_id>.+)/', views.ManageUserTimelines.as_view(), name='manage-user-timelines'),
    url(r'^manage-timeline-users/(?P<timeline_id>.+)/', views.ManageTimelineUsers.as_view(), name='manage-timeline-users'),
    url(r'^bind-timeline-user/(?P<timeline_id>.+)/(?P<user_id>.+)/', views.BindTimelineUser.as_view(), name='bind-timeline-user'),
    url(r'^unbind-timeline-user/(?P<timeline_id>.+)/(?P<user_id>.+)/', views.UnbindTimelineUser.as_view(), name='unbind-timeline-user'),
    url(r'^timeline-link/(?P<timeline_id>.+)/', views.TimelineLink.as_view(), name='timeline-link'),

]


