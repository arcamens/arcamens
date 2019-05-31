from django.views.generic.base import RedirectView
from django.conf.urls import re_path
from . import views

app_name = 'board_app'
urlpatterns = [
    # re_path('list-boards/', views.ListBoards.as_view(), name='list-boards'),
    re_path('create-board/', views.CreateBoard.as_view(), name='create-board'),
    re_path('pin-board/(?P<board_id>.+)/', views.PinBoard.as_view(), name='pin-board'),

    re_path('update-board/(?P<board_id>.+)/', views.UpdateBoard.as_view(), name='update-board'),
    re_path('paste-list/(?P<board_id>.+)/(?P<list_id>.+)/', views.PasteList.as_view(), name='paste-list'),
    re_path('paste-all-lists/(?P<board_id>.+)/', views.PasteAllLists.as_view(), name='paste-all-lists'),
    re_path('select-destin-board/(?P<board_id>.+)/', views.SelectDestinBoard.as_view(), name='select-destin-board'),

    re_path('delete-board/(?P<board_id>.+)/', views.DeleteBoard.as_view(), name='delete-board'),
    re_path('login/', RedirectView.as_view(pattern_name='site_app:login'), name='login'),
    re_path('logout/', RedirectView.as_view(pattern_name='site_app:logout'), name='logout'),
    re_path('list-pins/', views.ListPins.as_view(), name='list-pins'),
    re_path('unpin/(?P<pin_id>.+)/', views.Unpin.as_view(), name='unpin'),

    re_path('unbind-member-boards/(?P<member_id>.+)/', views.UnbindMemberBoards.as_view(), name='unbind-member-boards'),
    re_path('bind-member-boards/(?P<member_id>.+)/', views.BindMemberBoards.as_view(), name='bind-member-boards'),
    re_path('unbind-board-members/(?P<board_id>.+)/', views.UnbindBoardMembers.as_view(), name='unbind-board-members'),
    re_path('bind-board-members/(?P<board_id>.+)/', views.BindBoardMembers.as_view(), name='bind-board-members'),
    re_path('create-boardship-member/(?P<board_id>.+)/(?P<member_id>.+)/', views.CreateBoardshipMember.as_view(), name='create-boardship-member'),
    re_path('create-member-boardship/(?P<board_id>.+)/(?P<member_id>.+)/', views.CreateMemberBoardship.as_view(), name='create-member-boardship'),

    re_path('set-member-boardship/(?P<board_id>.+)/(?P<member_id>.+)/', views.SetMemberBoardship.as_view(), name='set-member-boardship'),
    re_path('set-boardship-member/(?P<board_id>.+)/(?P<member_id>.+)/', views.SetBoardshipMember.as_view(), name='set-boardship-member'),
    re_path('delete-boardship-member/(?P<board_id>.+)/(?P<member_id>.+)/', views.DeleteBoardshipMember.as_view(), name='delete-boardship-member'),
    re_path('delete-member-boardship/(?P<board_id>.+)/(?P<member_id>.+)/', views.DeleteMemberBoardship.as_view(), name='delete-member-boardship'),

    re_path('board-link/(?P<board_id>.+)/', views.BoardLink.as_view(), name='board-link'),
    re_path('join-public-board/(?P<board_id>.+)/', views.JoinPublicBoard.as_view(), name='join-public-board'),
    re_path('leave-board/(?P<board_id>.+)/', views.LeaveBoard.as_view(), name='leave-board'),

]



