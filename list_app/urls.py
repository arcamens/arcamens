from django.views.generic.base import RedirectView
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^list-lists/(?P<board_id>.+)/', views.ListLists.as_view(), name='list-lists'),
    url(r'^done/(?P<list_id>.+)/', views.Done.as_view(), name='done'),
    url(r'^update-list/(?P<list_id>.+)/', views.UpdateList.as_view(), name='update-list'),
    url(r'^create-list/(?P<board_id>.+)/', views.CreateList.as_view(), name='create-list'),
    url(r'^delete-list/(?P<list_id>.+)/', views.DeleteList.as_view(), name='delete-list'),
    url(r'^list/(?P<list_id>.+)/', views.List.as_view(), name='list'),
    url(r'^pin-list/(?P<list_id>.+)/', views.PinList.as_view(), name='pin-list'),
    url(r'^e-create-list/(?P<event_id>.+)/', views.ECreateList.as_view(), name='e-create-list'),
    url(r'^e-update-list/(?P<event_id>.+)/', views.EUpdateList.as_view(), name='e-update-list'),
    url(r'^e--list/(?P<event_id>.+)/', views.EUpdateList.as_view(), name='e-update-list'),
    url(r'^e-delete-list/(?P<event_id>.+)/', views.EDeleteList.as_view(), name='e-delete-list'),
    url(r'^paste-cards/(?P<list_id>.+)/', views.PasteCards.as_view(), name='paste-cards'),
    url(r'^cut-list/(?P<list_id>.+)/', views.CutList.as_view(), name='cut-list'),
    url(r'^copy-list/(?P<list_id>.+)/', views.CopyList.as_view(), name='copy-list'),
    url(r'^setup-list-filter/(?P<board_id>.+)', views.SetupListFilter.as_view(), name='setup-list-filter'),
    url(r'^e-archive-list/(?P<event_id>.+)/', views.EArchiveList.as_view(), name='e-archive-list'),

]









































