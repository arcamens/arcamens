from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^create-note/(?P<card_id>.+)/', views.CreateNote.as_view(), name='create-note'),
    url(r'^list-notes/(?P<card_id>.+)/', views.ListNotes.as_view(), name='list-notes'),
    url(r'^note-link/(?P<note_id>.+)/', views.NoteLink.as_view(), name='note-link'),

    url(r'^update-note/(?P<note_id>.+)/', views.UpdateNote.as_view(), name='update-note'),
    url(r'^preview-note/(?P<note_id>.+)/', views.PreviewNote.as_view(), name='preview-note'),

    url(r'^note/(?P<note_id>.+)/', views.Note.as_view(), name='note'),
    url(r'^delete-note/(?P<note_id>.+)/', views.DeleteNote.as_view(), name='delete-note'),

    url(r'^attach-file/(?P<note_id>.+)/', views.AttachFile.as_view(), name='attach-file'),
    url(r'^detach-file/(?P<filewrapper_id>.+)/', views.DetachFile.as_view(), name='detach-file'),
    # url(r'^cancel-note-creation/(?P<note_id>.+)/', views.CancelNoteCreation.as_view(), name='cancel-note-creation'),
]





