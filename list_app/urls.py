from django.views.generic.base import RedirectView
from django.conf.urls import re_path
from . import views

app_name = 'list_app'
urlpatterns = [
    re_path('list-lists/(?P<board_id>.+)/', views.ListLists.as_view(), name='list-lists'),
    re_path('update-list/(?P<list_id>.+)/', views.UpdateList.as_view(), name='update-list'),
    re_path('create-list/(?P<board_id>.+)/', views.CreateList.as_view(), name='create-list'),
    re_path('delete-list/(?P<list_id>.+)/', views.DeleteList.as_view(), name='delete-list'),
    re_path('pin-list/(?P<list_id>.+)/', views.PinList.as_view(), name='pin-list'),
    re_path('paste-card/(?P<list_id>.+)/(?P<card_id>.+)/', views.PasteCard.as_view(), name='paste-card'),
    re_path('paste-card/(?P<list_id>.+)/', views.PasteCard.as_view(), name='paste-card'),
    re_path('paste-all-cards/(?P<list_id>.+)/', views.PasteAllCards.as_view(), name='paste-all-cards'),
    re_path('cut-list/(?P<list_id>.+)/', views.CutList.as_view(), name='cut-list'),
    re_path('copy-list/(?P<list_id>.+)/', views.CopyList.as_view(), name='copy-list'),
    re_path('setup-list-filter/(?P<board_id>.+)', views.SetupListFilter.as_view(), name='setup-list-filter'),
    re_path('undo-clipboard/(?P<list_id>.+)/', views.UndoClipboard.as_view(), name='undo-clipboard'),
    re_path('list-link/(?P<list_id>.+)/', views.ListLink.as_view(), name='list-link'),
    re_path('confirm-list-deletion/(?P<list_id>.+)/', views.ConfirmListDeletion.as_view(), name='confirm-list-deletion'),
    re_path('unpin/(?P<pin_id>.+)/', views.Unpin.as_view(), name='unpin'),

]






