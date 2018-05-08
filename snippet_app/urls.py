from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^create-snippet/(?P<post_id>.+)/(?P<snippet_id>.+)/', views.CreateSnippet.as_view(), name='create-snippet'),
    url(r'^create-snippet/(?P<post_id>.+)/', views.CreateSnippet.as_view(), name='create-snippet'),
    url(r'^update-snippet/(?P<snippet_id>.+)/', views.UpdateSnippet.as_view(), name='update-snippet'),
    url(r'^snippet/(?P<snippet_id>.+)/', views.Snippet.as_view(), name='snippet'),
    url(r'^delete-snippet/(?P<snippet_id>.+)/', views.DeleteSnippet.as_view(), name='delete-snippet'),

    url(r'^attach-file/(?P<snippet_id>.+)/', views.AttachFile.as_view(), name='attach-file'),
    url(r'^detach-file/(?P<filewrapper_id>.+)/', views.DetachFile.as_view(), name='detach-file'),
    url(r'^cancel-snippet-creation/(?P<snippet_id>.+)/', views.CancelSnippetCreation.as_view(), name='cancel-snippet-creation'),

]


