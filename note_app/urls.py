from django.urls import path
from . import views

app_name = 'note_app'
urlpatterns = [
    path('create-note/<int:card_id>/', views.CreateNote.as_view(), name='create-note'),
    path('list-notes/<int:card_id>/', views.ListNotes.as_view(), name='list-notes'),
    path('note-link/<int:note_id>/', views.NoteLink.as_view(), name='note-link'),
    path('restore-note/<int:event_id>/', views.RestoreNote.as_view(), name='restore-note'),

    path('update-note/<int:note_id>/', views.UpdateNote.as_view(), name='update-note'),
    path('note-diff/<int:event_id>/', views.NoteDiff.as_view(), name='note-diff'),

    path('preview-note/<int:note_id>/', views.PreviewNote.as_view(), name='preview-note'),

    path('note/<int:note_id>/', views.Note.as_view(), name='note'),
    path('delete-note/<int:note_id>/', views.DeleteNote.as_view(), name='delete-note'),

    path('attach-file/<int:note_id>/', views.AttachFile.as_view(), name='attach-file'),
    path('detach-file/<int:filewrapper_id>/', views.DetachFile.as_view(), name='detach-file'),
    path('note-file-download/<int:filewrapper_id>/', views.NoteFileDownload.as_view(), name='note-file-download'),
    path('find/', views.Find.as_view(), name='find'),
    path('note-events/<int:note_id>/', views.NoteEvents.as_view(), name='note-events'),

]



