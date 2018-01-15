from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^e-create-note/(?P<event_id>.+)/', views.ECreateNote.as_view(), name='e-create-note'),
    url(r'^create-note/(?P<card_id>.+)/(?P<note_id>.+)/', views.CreateNote.as_view(), name='create-note'),
    url(r'^create-note/(?P<card_id>.+)/', views.CreateNote.as_view(), name='create-note'),
    url(r'^update-note/(?P<note_id>.+)/', views.UpdateNote.as_view(), name='update-note'),

    url(r'^attach-file/(?P<note_id>.+)/', views.AttachFile.as_view(), name='attach-file'),
    url(r'^detach-file/(?P<filewrapper_id>.+)/', views.DetachFile.as_view(), name='detach-file'),

]


























