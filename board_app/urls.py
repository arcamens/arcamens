from django.views.generic.base import RedirectView
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^list-boards/', views.ListBoards.as_view(), name='list-boards'),
    url(r'^create-board/', views.CreateBoard.as_view(), name='create-board'),
    url(r'^pin-board/(?P<board_id>.+)/', views.PinBoard.as_view(), name='pin-board'),

    url(r'^update-board/(?P<board_id>.+)/', views.UpdateBoard.as_view(), name='update-board'),
    url(r'^paste-lists/(?P<board_id>.+)/', views.PasteLists.as_view(), name='paste-lists'),
    url(r'^delete-board/(?P<board_id>.+)/', views.DeleteBoard.as_view(), name='delete-board'),
    url(r'^setup-board-filter/(?P<organization_id>.+)', views.SetupBoardFilter.as_view(), name='setup-board-filter'),
    url(r'^login/', RedirectView.as_view(pattern_name='site_app:login'), name='login'),
    url(r'^logout/', RedirectView.as_view(pattern_name='site_app:logout'), name='logout'),
    url(r'^manage-user-boards/(?P<user_id>.+)/', views.ManageUserBoards.as_view(), name='manage-user-boards'),
    url(r'^manage-board-users/(?P<board_id>.+)', views.ManageBoardUsers.as_view(), name='manage-board-users'),
    url(r'^list-pins/', views.ListPins.as_view(), name='list-pins'),
    url(r'^unpin/(?P<pin_id>.+)/', views.Unpin.as_view(), name='unpin'),
    url(r'^bind-board-user/(?P<board_id>.+)/(?P<user_id>.+)/', views.BindBoardUser.as_view(), name='bind-board-user'),
    url(r'^unbind-board-user/(?P<board_id>.+)/(?P<user_id>.+)/', views.UnbindBoardUser.as_view(), name='unbind-board-user'),

]


















