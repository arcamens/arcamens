from django.views.generic.base import RedirectView
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^index/$', views.Index.as_view(), name='index'),
    url(r'^disabled-account/(?P<user_id>.+)/', views.DisabledAccount.as_view(), name='disabled-account'),
    url(r'^switch-organization/(?P<organization_id>.+)/', views.SwitchOrganization.as_view(), name='switch-organization'),
    url(r'^update-user-information/', views.UpdateUserInformation.as_view(), name='update-user-information'),
    url(r'^create-organization/(?P<user_id>.+)/', views.CreateOrganization.as_view(), name='create-organization'),
    url(r'^seen-event/(?P<event_id>.+)/', views.SeenEvent.as_view(), name='seen-event'),

    url(r'^join-organization/(?P<organization_id>.+)/(?P<token>.+)/', views.JoinOrganization.as_view(), name='join-organization'),
    url(r'^signup-from-invite/(?P<organization_id>.+)/(?P<token>.+)/', views.SignupFromInvite.as_view(), name='signup-from-invite'),
    url(r'^update-organization/(?P<organization_id>.+)/', views.UpdateOrganization.as_view(), name='update-organization'),
    url(r'^delete-organization/(?P<organization_id>.+)/', views.DeleteOrganization.as_view(), name='delete-organization'),
    url(r'^list-users/(?P<organization_id>.+)', views.ListUsers.as_view(), name='list-users'),
    url(r'^manage-user-tags/(?P<user_id>.+)', views.ManageUserTags.as_view(), name='manage-user-tags'),
    url(r'^list-events/', views.ListEvents.as_view(), name='list-events'),
    url(r'^shout/', views.Shout.as_view(), name='shout'),
    url(r'^list-logs/', views.ListLogs.as_view(), name='list-logs'),
    url(r'^all-seen/', views.AllSeen.as_view(), name='all-seen'),

    url(r'^list-tags/', views.ListTags.as_view(), name='list-tags'),
    url(r'^bind-user-tag/(?P<user_id>.+)/(?P<tag_id>.+)/', views.BindUserTag.as_view(), name='bind-user-tag'),
    url(r'^unbind-user-tag/(?P<user_id>.+)/(?P<tag_id>.+)/', views.UnbindUserTag.as_view(), name='unbind-user-tag'),
    url(r'^create-tag/', views.CreateTag.as_view(), name='create-tag'),
    url(r'^delete-tag/(?P<tag_id>.+)/', views.DeleteTag.as_view(), name='delete-tag'),
    url(r'^invite-organization-user/(?P<organization_id>.+)/', views.InviteOrganizationUser.as_view(), name='invite-organization-user'),
    url(r'^list-clipboard/', views.ListClipboard.as_view(), name='list-clipboard'),
    url(r'^delete-all-clipboard/', views.DeleteAllClipboard.as_view(), name='delete-all-clipboard'),
    url(r'^confirm-clipboard-deletion/', views.ConfirmClipboardDeletion.as_view(), name='confirm-clipboard-deletion'),
    url(r'^update-password/', views.UpdatePassword.as_view(), name='update-password'),

    url(r'^export/', views.Export.as_view(), name='export'),
    url(r'^import/', views.Import.as_view(), name='import'),
    url(r'^disabled-account/$', views.DisabledAccount.as_view(), name='disabled-account'),
    url(r'^fix-account-debits/$', views.FixAccountDebits.as_view(), name='fix-account-debits'),
    url(r'^remove-organization-user(?P<user_id>.+)', views.RemoveOrganizationUser.as_view(), name='remove-organization-user'),
    url(r'^cancel-invite/(?P<invite_id>.+)', views.CancelInvite.as_view(), name='cancel-invite'),
    url(r'^list-invites/', views.ListInvites.as_view(), name='list-invites'),
    url(r'^manage-organization-admins/', views.ManageOrganizationAdmins.as_view(), name='manage-organization-admins'),
    url(r'^bind-organization-admin/(?P<organization_id>.+)/(?P<user_id>.+)/', views.BindOrganizationAdmin.as_view(), name='bind-organization-admin'),
    url(r'^unbind-organization-admin/(?P<organization_id>.+)/(?P<user_id>.+)/', views.UnbindOrganizationAdmin.as_view(), name='unbind-organization-admin'),

]


