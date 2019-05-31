from django.conf.urls import re_path
from django.views.generic.base import RedirectView
from . import views

app_name = 'group_app'
urlpatterns = [
    # re_path('group/(?P<group_id>.+)/', views.Group.as_view(), name='group'),
    re_path('list-posts/(?P<group_id>.+)/', views.ListPosts.as_view(), name='list-posts'),
    re_path('create-group/(?P<organization_id>.+)', views.CreateGroup.as_view(), name='create-group'),
    re_path('update-group/(?P<group_id>.+)/', views.UpdateGroup.as_view(), name='update-group'),
    re_path('delete-group/(?P<group_id>.+)/', views.DeleteGroup.as_view(), name='delete-group'),
    re_path('unbind-user-groups/(?P<user_id>.+)/', views.UnbindUserGroups.as_view(), name='unbind-user-groups'),
    re_path('bind-user-groups/(?P<user_id>.+)/', views.BindUserGroups.as_view(), name='bind-user-groups'),

    re_path('unbind-group-users/(?P<group_id>.+)/', views.UnbindGroupUsers.as_view(), name='unbind-group-users'),
    re_path('bind-group-users/(?P<group_id>.+)/', views.BindGroupUsers.as_view(), name='bind-group-users'),
    re_path('create-groupship-user/(?P<group_id>.+)/(?P<user_id>.+)/', views.CreateGroupshipUser.as_view(), name='create-groupship-user'),
    re_path('create-user-groupship/(?P<group_id>.+)/(?P<user_id>.+)/', views.CreateUserGroupship.as_view(), name='create-user-groupship'),

    re_path('set-user-groupship/(?P<group_id>.+)/(?P<user_id>.+)/', views.SetUserGroupship.as_view(), name='set-user-groupship'),
    re_path('set-groupship-user/(?P<group_id>.+)/(?P<user_id>.+)/', views.SetGroupshipUser.as_view(), name='set-groupship-user'),

    re_path('group-link/(?P<group_id>.+)/', views.GroupLink.as_view(), name='group-link'),
    re_path('pin-group/(?P<group_id>.+)/', views.PinGroup.as_view(), name='pin-group'),
    re_path('unpin/(?P<pin_id>.+)/', views.Unpin.as_view(), name='unpin'),
    re_path('select-destin-group/(?P<group_id>.+)/', views.SelectDestinGroup.as_view(), name='select-destin-group'),
    re_path('paste-post/(?P<group_id>.+)/(?P<post_id>.+)/', views.PastePost.as_view(), name='paste-post'),
    re_path('paste-all-posts/(?P<group_id>.+)/', views.PasteAllPosts.as_view(), name='paste-all-posts'),
    re_path('delete-groupship-user/(?P<group_id>.+)/(?P<user_id>.+)/', views.DeleteGroupshipUser.as_view(), name='delete-groupship-user'),
    re_path('delete-user-groupship/(?P<group_id>.+)/(?P<user_id>.+)/', views.DeleteUserGroupship.as_view(), name='delete-user-groupship'),
    re_path('join-public-group/(?P<group_id>.+)/', views.JoinPublicGroup.as_view(), name='join-public-group'),
    re_path('leave-group/(?P<group_id>.+)/', views.LeaveGroup.as_view(), name='leave-group'),

]

