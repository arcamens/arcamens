from django.views.generic.base import RedirectView
from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^list-boards/', views.ListBoards.as_view(), name='list-boards'),
    url(r'^create-board/', views.CreateBoard.as_view(), name='create-board'),
    url(r'^pin-board/(?P<board_id>.+)/', views.PinBoard.as_view(), name='pin-board'),

    url(r'^update-board/(?P<board_id>.+)/', views.UpdateBoard.as_view(), name='update-board'),
    url(r'^paste-list/(?P<board_id>.+)/(?P<list_id>.+)/', views.PasteList.as_view(), name='paste-list'),
    url(r'^paste-all-lists/(?P<board_id>.+)/', views.PasteAllLists.as_view(), name='paste-all-lists'),
    url(r'^select-destin-board/(?P<board_id>.+)/', views.SelectDestinBoard.as_view(), name='select-destin-board'),

    url(r'^delete-board/(?P<board_id>.+)/', views.DeleteBoard.as_view(), name='delete-board'),
    url(r'^login/', RedirectView.as_view(pattern_name='site_app:login'), name='login'),
    url(r'^logout/', RedirectView.as_view(pattern_name='site_app:logout'), name='logout'),
    url(r'^manage-user-boards/(?P<user_id>.+)/', views.ManageUserBoards.as_view(), name='manage-user-boards'),
    url(r'^manage-board-members/(?P<board_id>.+)', views.ManageBoardMembers.as_view(), name='manage-board-members'),
    url(r'^manage-board-admins/(?P<board_id>.+)', views.ManageBoardAdmins.as_view(), name='manage-board-admins'),
    url(r'^list-pins/', views.ListPins.as_view(), name='list-pins'),
    url(r'^unpin/(?P<pin_id>.+)/', views.Unpin.as_view(), name='unpin'),
    url(r'^bind-board-user/(?P<board_id>.+)/(?P<user_id>.+)/', views.BindBoardUser.as_view(), name='bind-board-user'),
    url(r'^unbind-board-user/(?P<board_id>.+)/(?P<user_id>.+)/', views.UnbindBoardUser.as_view(), name='unbind-board-user'),
    url(r'^bind-board-admin/(?P<board_id>.+)/(?P<user_id>.+)/', views.BindBoardAdmin.as_view(), name='bind-board-admin'),
    url(r'^unbind-board-admin/(?P<board_id>.+)/(?P<user_id>.+)/', views.UnbindBoardAdmin.as_view(), name='unbind-board-admin'),

    url(r'^board-link/(?P<board_id>.+)/', views.BoardLink.as_view(), name='board-link'),

]








