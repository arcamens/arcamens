from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^e-create-snippet/(?P<event_id>.+)/', views.ECreateSnippet.as_view(), name='e-create-snippet'),
    url(r'^e-delete-snippet/(?P<event_id>.+)/', views.EDeleteSnippet.as_view(), name='e-delete-snippet'),
    url(r'^e-update-snippet/(?P<event_id>.+)/', views.EUpdateSnippet.as_view(), name='e-update-snippet'),

    url(r'^create-snippet/(?P<card_id>.+)/(?P<snippet_id>.+)/', views.CreateSnippet.as_view(), name='create-snippet'),
    url(r'^create-snippet/(?P<card_id>.+)/', views.CreateSnippet.as_view(), name='create-snippet'),
    url(r'^update-snippet/(?P<snippet_id>.+)/', views.UpdateSnippet.as_view(), name='update-snippet'),
    url(r'^snippet/(?P<snippet_id>.+)/', views.Snippet.as_view(), name='snippet'),
    url(r'^delete-snippet/(?P<snippet_id>.+)/', views.DeleteSnippet.as_view(), name='delete-snippet'),

    url(r'^attach-file/(?P<snippet_id>.+)/', views.AttachFile.as_view(), name='attach-file'),
    url(r'^detach-file/(?P<filewrapper_id>.+)/', views.DetachFile.as_view(), name='detach-file'),

]





























