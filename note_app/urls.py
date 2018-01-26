from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^e-create-note/(?P<event_id>.+)/', views.ECreateNote.as_view(), name='e-create-note'),
    url(r'^e-delete-note/(?P<event_id>.+)/', views.EDeleteNote.as_view(), name='e-delete-note'),
    url(r'^e-update-note/(?P<event_id>.+)/', views.EUpdateNote.as_view(), name='e-update-note'),

    url(r'^create-note/(?P<card_id>.+)/(?P<note_id>.+)/', views.CreateNote.as_view(), name='create-note'),
    url(r'^create-note/(?P<card_id>.+)/', views.CreateNote.as_view(), name='create-note'),
    url(r'^list-notes/(?P<card_id>.+)/', views.ListNotes.as_view(), name='list-notes'),

    url(r'^update-note/(?P<note_id>.+)/', views.UpdateNote.as_view(), name='update-note'),
    url(r'^note/(?P<note_id>.+)/', views.Note.as_view(), name='note'),
    url(r'^delete-note/(?P<note_id>.+)/', views.DeleteNote.as_view(), name='delete-note'),

    url(r'^attach-file/(?P<note_id>.+)/', views.AttachFile.as_view(), name='attach-file'),
    url(r'^detach-file/(?P<filewrapper_id>.+)/', views.DetachFile.as_view(), name='detach-file'),

]





























