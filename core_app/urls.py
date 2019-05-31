from django.views.generic.base import RedirectView
from django.conf.urls import re_path
from . import views

app_name = 'core_app'
urlpatterns = [
    re_path('index/', views.Index.as_view(), name='index'),
    re_path('set-timezone/', views.SetTimezone.as_view(), name='set-timezone'),
    re_path('disabled-account/(?P<user_id>.+)/', views.DisabledAccount.as_view(), name='disabled-account'),
    re_path('switch-organization/(?P<organization_id>.+)/', views.SwitchOrganization.as_view(), name='switch-organization'),
    re_path('update-user-information/', views.UpdateUserInformation.as_view(), name='update-user-information'),
    re_path('create-organization/', views.CreateOrganization.as_view(), name='create-organization'),
    re_path('select-organization/', views.SelectOrganization.as_view(), name='select-organization'),
    re_path('no-organization/', views.NoOrganization.as_view(), name='no-organization'),
    re_path('no-default/', views.NoDefault.as_view(), name='no-default'),

    re_path('seen-event/(?P<event_id>.+)/', views.SeenEvent.as_view(), name='seen-event'),
    re_path('setup-node-filter/', views.SetupNodeFilter.as_view(), name='setup-node-filter'),
    re_path('join-organization/(?P<organization_id>.+)/(?P<token>.+)/', views.JoinOrganization.as_view(), name='join-organization'),
    re_path('signup-from-invite/(?P<organization_id>.+)/(?P<token>.+)/', views.SignupFromInvite.as_view(), name='signup-from-invite'),
    re_path('update-organization/', views.UpdateOrganization.as_view(), name='update-organization'),
    re_path('delete-organization/', views.DeleteOrganization.as_view(), name='delete-organization'),
    re_path('list-users/', views.ListUsers.as_view(), name='list-users'),
    re_path('list-events/', views.ListEvents.as_view(), name='list-events'),
    re_path('shout/', views.Shout.as_view(), name='shout'),
    re_path('list-logs/', views.ListLogs.as_view(), name='list-logs'),
    re_path('all-seen/', views.AllSeen.as_view(), name='all-seen'),

    re_path('list-tags/', views.ListTags.as_view(), name='list-tags'),
    re_path('create-tag/', views.CreateTag.as_view(), name='create-tag'),
    re_path('delete-tag/(?P<tag_id>.+)/', views.DeleteTag.as_view(), name='delete-tag'),
    re_path('invite-organization-user/', views.InviteOrganizationUser.as_view(), name='invite-organization-user'),
    re_path('list-clipboard/', views.ListClipboard.as_view(), name='list-clipboard'),
    re_path('delete-all-clipboard/', views.DeleteAllClipboard.as_view(), name='delete-all-clipboard'),
    re_path('confirm-clipboard-deletion/', views.ConfirmClipboardDeletion.as_view(), name='confirm-clipboard-deletion'),
    re_path('update-password/', views.UpdatePassword.as_view(), name='update-password'),
    re_path('set-membership/(?P<organization_id>.+)/(?P<user_id>.+)/', views.SetMembership.as_view(), name='set-membership'),

    re_path('disabled-account/', views.DisabledAccount.as_view(), name='disabled-account'),
    re_path('remove-organization-user/(?P<user_id>.+)', views.RemoveOrganizationUser.as_view(), name='remove-organization-user'),
    re_path('cancel-invite/(?P<invite_id>.+)', views.CancelInvite.as_view(), name='cancel-invite'),
    re_path('list-invites/', views.ListInvites.as_view(), name='list-invites'),
    re_path('resend-invite/(?P<invite_id>.+)', views.ResendInvite.as_view(), name='resend-invite'),
    re_path('list-nodes/', views.ListNodes.as_view(), name='list-nodes'),
    re_path('list-public-organizations/', views.ListPublicOrganizations.as_view(), name='list-public-organizations'),
    re_path('resend-email-confirmation/', views.ResendEmailConfirmation.as_view(), name='resend-email-confirmation'),
    re_path('join-public-organization/(?P<organization_id>.+)/', views.JoinPublicOrganization.as_view(), name='join-public-organization'),
    re_path('not-public-organization/(?P<organization_id>.+)/', views.NotPublicOrganization.as_view(), name='not-public-organization'),
    re_path('join-from-link/(?P<organization_id>.+)/', views.JoinFromLink.as_view(), name='join-from-link'),

    re_path('unbind-user-tags/(?P<user_id>.+)/', views.UnbindUserTags.as_view(), name='unbind-user-tags'),
    re_path('bind-user-tags/(?P<user_id>.+)/', views.BindUserTags.as_view(), name='bind-user-tags'),
    re_path('create-user-tagship/(?P<user_id>.+)/(?P<tag_id>.+)/', views.CreateUserTagship.as_view(), name='create-user-tagship'),
    re_path('delete-user-tagship/(?P<user_id>.+)/(?P<tag_id>.+)/', views.DeleteUserTagship.as_view(), name='delete-user-tagship'),

]




