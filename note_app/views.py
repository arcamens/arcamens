from django.views.generic import View
from django.conf import settings
from django.db.models import Q
from django.shortcuts import render, redirect
from core_app.views import GuardianView, FileDownload

from django.http import HttpResponse
from card_app.models import Card
from core_app.models import User
from . import models
from . import forms

class Note(GuardianView):
    def get(self, request, note_id):
        note = models.Note.locate(self.me, self.me.default, note_id)
        attachments = note.notefilewrapper_set.all()

        return render(request, 'note_app/note.html', 
        {'note': note, 'attachments': attachments})

class NoteLink(GuardianView):
    def get(self, request, note_id):
        note = models.Note.locate(self.me, self.me.default, note_id)
        organizations = self.me.organizations.exclude(id=self.me.default.id)

        return render(request, 'note_app/note-link.html', 
        {'note': note, 'card': note.card, 'user': self.me, 
        'organizations': organizations, 'default': self.me.default, 
        'organization': self.me.default, 'settings': settings})

class ListNotes(GuardianView):
    def get(self, request, card_id):
        card = Card.locate(self.me, self.me.default, card_id)
        notes = card.notes.all().order_by('-created')

        return render(request, 'note_app/list-notes.html', 
        {'records': notes, 'card': card})

class CreateNote(GuardianView):
    """
    """

    def get(self, request, card_id):
        card = Card.locate(self.me, self.me.default, card_id)
        form = forms.NoteForm()
        return render(request, 'note_app/create-note.html', 
        {'form':form, 'card': card})

    def post(self, request, card_id):
        card = Card.locate(self.me, self.me.default, card_id)
        form = forms.NoteForm(request.POST)
        user = User.objects.get(id=self.user_id)

        if not form.is_valid():
            return render(request, 'note_app/create-note.html', 
                {'form': form, 'card':card}, status=400)

        note       = form.save(commit=False)
        note.owner = self.me
        note.card  = card
        note.save()

        event = models.ECreateNote.objects.create(
        organization=self.me.default, child=card, user=self.me, note=note)
        event.dispatch(*card.ancestor.ancestor.members.all())

        return render(request, 'note_app/preview-note.html',
        {'note': note, 'card': note.card})

class AttachFile(GuardianView):
    """
    """

    def get(self, request, note_id):
        note = models.Note.locate(self.me, self.me.default, note_id)
        attachments = note.notefilewrapper_set.all()
        form = forms.NoteFileWrapperForm()

        return render(request, 'note_app/attach-file.html', 
        {'note':note, 'form': form, 'attachments': attachments})

    def post(self, request, note_id):
        note = models.Note.locate(self.me, self.me.default, note_id)
        note = models.Note.objects.get(id=note_id)
        attachments = note.notefilewrapper_set.all()

        form = forms.NoteFileWrapperForm(request.POST, 
        request.FILES, user=self.me)

        if not form.is_valid():
            return render(request, 'note_app/attach-file.html', 
                {'note':note, 'form': form, 'attachments': attachments})
        record = form.save(commit = False)
        record.organization = self.me.default
        record.note = note
        form.save()

        event = models.EAttachNoteFile.objects.create(
        organization=self.me.default, filewrapper=record, 
        note=note, user=self.me)

        event.dispatch(*note.card.ancestor.ancestor.members.all())
        event.save()

        return self.get(request, note_id)

class DetachFile(GuardianView):
    """
    """

    def get(self, request, filewrapper_id):
        filewrapper = models.NoteFileWrapper.objects.filter(
        Q(note__card__ancestor__ancestor__members=self.me) | Q(note__card__workers=self.me), 
        note__card__ancestor__ancestor__organization=self.me.default, 
        id=filewrapper_id).distinct().first()

        attachments = filewrapper.note.notefilewrapper_set.all()
        form        = forms.NoteFileWrapperForm()

        event = models.EDettachNoteFile.objects.create(
        organization=self.me.default, filename=filewrapper.file.name, 
        note=filewrapper.note, user=self.me)

        event.dispatch(*filewrapper.note.card.ancestor.ancestor.members.all())
        event.save()
        filewrapper.delete()

        return render(request, 'note_app/attach-file.html', 
        {'note':filewrapper.note, 'form': form, 'attachments': attachments})

class PreviewNote(GuardianView):
    def get(self, request, note_id):
        note = models.Note.locate(self.me, self.me.default, note_id)
        
        return render(request, 'note_app/preview-note.html',
        {'note': note, 'card': note.card})

class UpdateNote(GuardianView):
    def get(self, request, note_id):
        note = models.Note.locate(self.me, self.me.default, note_id)
        return render(request, 'note_app/update-note.html',
        {'note': note, 'form': forms.NoteForm(instance=note),})

    def post(self, request, note_id):
        record = models.Note.locate(self.me, self.me.default, note_id)
        form    = forms.NoteForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'note_app/update-note.html',
                        {'form': form, 'note':record, }, status=400)

        record.save()

        event = models.EUpdateNote.objects.create(
        organization=self.me.default, child=record.card, 
        note=record, user=self.me)

        event.dispatch(*record.card.ancestor.ancestor.members.all())
        event.save()

        # user.ws_sound(record.card.ancestor.ancestor)

        return redirect('note_app:preview-note', 
        note_id=record.id)

class DeleteNote(GuardianView):
    def get(self, request, note_id):
        note = models.Note.locate(self.me, self.me.default, note_id)

        event = models.EDeleteNote.objects.create(organization=self.me.default,
        child=note.card, note='Note', user=self.me)

        event.dispatch(*note.card.ancestor.ancestor.members.all())
        note.delete()

        # user.ws_sound(note.card.ancestor.ancestor)

        return redirect('note_app:list-notes', 
        card_id=note.card.id)

class NoteFileDownload(FileDownload):
    def get(self, request, filewrapper_id):
        filewrapper = models.NoteFileWrapper.objects.filter(
        Q(note__card__ancestor__ancestor__members=self.me) | Q(note__card__workers=self.me), 
        note__card__ancestor__ancestor__organization=self.me.default, 
        id=filewrapper_id).distinct().first()

        return self.get_file_url(filewrapper.file)


