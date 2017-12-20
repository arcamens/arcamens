from django.conf.urls import url
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    url(r'^timeline/(?P<timeline_id>.+)/', views.Timeline.as_view(), name='timeline'),
    url(r'^list-posts/(?P<timeline_id>.+)/', views.ListPosts.as_view(), name='list-posts'),
    url(r'^list-all-posts/(?P<user_id>.+)', views.ListAllPosts.as_view(), name='list-all-posts'),
    url(r'^list-clipboard/(?P<user_id>.+)', views.ListClipboard.as_view(), name='list-clipboard'),
    url(r'^create-timeline/(?P<organization_id>.+)', views.CreateTimeline.as_view(), name='create-timeline'),
    url(r'^update-timeline/(?P<timeline_id>.+)/', views.UpdateTimeline.as_view(), name='update-timeline'),
    url(r'^delete-timeline/(?P<timeline_id>.+)/', views.DeleteTimeline.as_view(), name='delete-timeline'),
    url(r'^setup-timeline-filter/(?P<organization_id>.+)', views.SetupTimelineFilter.as_view(), name='setup-timeline-filter'),
    url(r'^e-update-timeline/(?P<event_id>.+)/', views.EUpdateTimeline.as_view(), name='e-update-timeline'),
    url(r'^e-bind-timeline-user/(?P<event_id>.+)/', views.EBindTimelineUser.as_view(), name='e-bind-timeline-user'),
    url(r'^e-unbind-timeline-user/(?P<event_id>.+)/', views.EUnbindTimelineUser.as_view(), name='e-unbind-timeline-user'),
    url(r'^e-delete-timeline/(?P<event_id>.+)/', views.EDeleteTimeline.as_view(), name='e-delete-timeline'),
    url(r'^paste-posts/(?P<timeline_id>.+)/', views.PastePosts.as_view(), name='paste-posts'),
    url(r'^logout/', RedirectView.as_view(pattern_name='site_app:logout'), name='logout'),
    url(r'^list-timelines/', views.ListTimelines.as_view(), name='list-timelines'),
    url(r'^invite-organization-user/(?P<organization_id>.+)/', views.InviteOrganizationUser.as_view(), name='invite-organization-user'),
    url(r'^check-event/(?P<user_id>.+)/', views.CheckEvent.as_view(), name='check-event'),
    url(r'^seen-event/(?P<event_id>.+)/', views.SeenEvent.as_view(), name='seen-event'),
    url(r'^manage-user-timelines/(?P<user_id>.+)/', views.ManageUserTimelines.as_view(), name='manage-user-timelines'),
    url(r'^manage-timeline-users/(?P<timeline_id>.+)/', views.ManageTimelineUsers.as_view(), name='manage-timeline-users'),
    url(r'^disabled-organization/(?P<user_id>.+)/', views.DisabledOrganization.as_view(), name='disabled-organization'),
    url(r'^bind-timeline-user/(?P<timeline_id>.+)/(?P<user_id>.+)/', views.BindTimelineUser.as_view(), name='bind-timeline-user'),
    url(r'^unbind-timeline-user/(?P<timeline_id>.+)/(?P<user_id>.+)/', views.UnbindTimelineUser.as_view(), name='unbind-timeline-user'),

]









