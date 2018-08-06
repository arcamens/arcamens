from django.conf.urls import url
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    # url(r'^group/(?P<group_id>.+)/', views.Group.as_view(), name='group'),
    url(r'^list-posts/(?P<group_id>.+)/', views.ListPosts.as_view(), name='list-posts'),
    url(r'^create-group/(?P<organization_id>.+)', views.CreateGroup.as_view(), name='create-group'),
    url(r'^update-group/(?P<group_id>.+)/', views.UpdateGroup.as_view(), name='update-group'),
    url(r'^delete-group/(?P<group_id>.+)/', views.DeleteGroup.as_view(), name='delete-group'),
    url(r'^manage-user-groups/(?P<user_id>.+)/', views.ManageUserGroups.as_view(), name='manage-user-groups'),
    url(r'^manage-group-users/(?P<group_id>.+)/', views.ManageGroupUsers.as_view(), name='manage-group-users'),
    url(r'^bind-group-user/(?P<group_id>.+)/(?P<user_id>.+)/', views.BindGroupUser.as_view(), name='bind-group-user'),
    url(r'^unbind-group-user/(?P<group_id>.+)/(?P<user_id>.+)/', views.UnbindGroupUser.as_view(), name='unbind-group-user'),
    url(r'^bind-user-group/(?P<group_id>.+)/(?P<user_id>.+)/', views.BindUserGroup.as_view(), name='bind-user-group'),
    url(r'^unbind-user-group/(?P<group_id>.+)/(?P<user_id>.+)/', views.UnbindUserGroup.as_view(), name='unbind-user-group'),

    url(r'^group-link/(?P<group_id>.+)/', views.GroupLink.as_view(), name='group-link'),
    url(r'^pin-group/(?P<group_id>.+)/', views.PinGroup.as_view(), name='pin-group'),
    url(r'^unpin/(?P<pin_id>.+)/', views.Unpin.as_view(), name='unpin'),
    url(r'^select-destin-group/(?P<group_id>.+)/', views.SelectDestinGroup.as_view(), name='select-destin-group'),
    url(r'^paste-post/(?P<group_id>.+)/(?P<post_id>.+)/', views.PastePost.as_view(), name='paste-post'),
    url(r'^paste-all-posts/(?P<group_id>.+)/', views.PasteAllPosts.as_view(), name='paste-all-posts'),

]




