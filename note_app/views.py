from django.views.generic import View
from django.shortcuts import render, redirect
from board_app.views import GuardianView
from django.http import HttpResponse
import board_app.models
import card_app.models
import core_app.models
from . import models
from . import forms
from core_app import ws

class Note(GuardianView):
    def get(self, request, note_id):
        note = models.Note.objects.get(id=note_id)

        # First check if someone has cut this card.
        # Cards on clipboard shouldnt be accessed due to generating
        # too many inconsistencies.
        # on_clipboard = not (card.ancestor and card.ancestor.ancestor)
# 
        # if on_clipboard:
            # return HttpResponse("This card is on clipboard! \
               # It can't be accessed.", status=400)

        user = core_app.models.User.objects.get(id=self.user_id)
        attachments = note.notefilewrapper_set.all()

        return render(request, 'note_app/note.html', 
        {'note': note, 'attachments': attachments})

class ListNotes(GuardianView):
    def get(self, request, card_id):
        card = card_app.models.Card.objects.get(id=card_id)
        notes = card.notes.all()

        return render(request, 'note_app/list-notes.html', 
        {'records': notes, 'card': card})

class CreateNote(GuardianView):
    """
    """

    def get(self, request, card_id, note_id=None):
        card = card_app.models.Card.objects.get(id=card_id)
        user = core_app.models.User.objects.get(id=self.user_id)
        note = models.Note.objects.create(owner=user, 
        card=card)
        card.save()

        form = forms.NoteForm(instance=card)
        note.data = 'Draft.'
        note.save()
        return render(request, 'note_app/create-note.html', 
        {'form':form, 'card': card, 'note':note})

    def post(self, request, card_id, note_id):
        card = card_app.models.Card.objects.get(id=card_id)

        note = models.Note.objects.get(id=note_id)
        form = forms.NoteForm(request.POST, instance=note)
        user = core_app.models.User.objects.get(id=self.user_id)

        if not form.is_valid():
            return render(request, 'note_app/create-note.html', 
                {'form': form, 'card':card, 'note': note}, status=400)

        note.save()

        event = models.ECreateNote.objects.create(
        organization=user.default, child=card, user=user, note=note)
        event.users.add(*card.ancestor.ancestor.members.all())

        ws.client.publish('board%s' % card.ancestor.ancestor.id, 
            'sound', 0, False)

        return render(request, 'note_app/preview-note.html',
        {'note': note, 'card': note.card})

class ECreateNote(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.ECreateNote.objects.get(id=event_id)
        return render(request, 'note_app/e-create-note.html', 
        {'event':event})

class EDeleteNote(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.EDeleteNote.objects.get(id=event_id)
        return render(request, 'note_app/e-delete-note.html', 
        {'event':event})

class EUpdateNote(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.EUpdateNote.objects.get(id=event_id)
        return render(request, 'note_app/e-update-note.html', 
        {'event':event})

class AttachFile(GuardianView):
    """
    """

    def get(self, request, note_id):
        note = models.Note.objects.get(id=note_id)
        attachments = note.notefilewrapper_set.all()
        form = forms.NoteFileWrapperForm()

        return render(request, 'note_app/attach-file.html', 
        {'note':note, 'form': form, 'attachments': attachments})

    def post(self, request, note_id):
        note = models.Note.objects.get(id=note_id)
        attachments = note.notefilewrapper_set.all()
        form = forms.NoteFileWrapperForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, 'note_app/attach-file.html', 
                {'note':note, 'form': form, 'attachments': attachments})
        record = form.save(commit = False)
        record.note = note
        form.save()
        return self.get(request, note_id)

class DetachFile(GuardianView):
    """
    """

    def get(self, request, filewrapper_id):
        filewrapper = models.NoteFileWrapper.objects.get(id=filewrapper_id)
        filewrapper.delete()
        attachments = filewrapper.note.filewrapper_set.all()

        form = forms.FileWrapperForm()
        return render(request, 'note_app/attach-file.html', 
        {'note':filewrapper.note, 'form': form, 'attachments': attachments})

class PreviewNote(GuardianView):
    def get(self, request, note_id):
        note = models.Note.objects.get(id=note_id)
        
        return render(request, 'note_app/preview-note.html',
        {'note': note, 'card': note.card})

class UpdateNote(GuardianView):
    def get(self, request, note_id):
        note = models.Note.objects.get(id=note_id)
        return render(request, 'note_app/update-note.html',
        {'note': note, 'form': forms.NoteForm(instance=note),})

    def post(self, request, note_id):
        record  = models.Note.objects.get(id=note_id)
        form    = forms.NoteForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'note_app/update-note.html',
                        {'form': form, 'note':record, }, status=400)

        record.save()

        user  = core_app.models.User.objects.get(id=self.user_id)

        event = models.EUpdateNote.objects.create(
        organization=user.default, child=record.card, 
        note=record, user=user)

        event.users.add(*record.card.ancestor.ancestor.members.all())
        event.save()

        ws.client.publish('board%s' % record.card.ancestor.ancestor.id, 
            'sound', 0, False)

        return redirect('note_app:preview-note', 
        note_id=record.id)

class DeleteNote(GuardianView):
    def get(self, request, note_id):
        note = models.Note.objects.get(id = note_id)

        user = core_app.models.User.objects.get(id=self.user_id)

        event = models.EDeleteNote.objects.create(organization=user.default,
        child=note.card, note='Note', user=user)

        event.users.add(*note.card.ancestor.ancestor.members.all())
        note.delete()

        ws.client.publish('board%s' % note.card.ancestor.ancestor.id, 
            'sound', 0, False)

        return redirect('note_app:list-notes', 
        card_id=note.card.id)

class CancelNoteCreation(GuardianView):
    def get(self, request, note_id):
        note = models.Note.objects.get(id = note_id)
        note.delete()

        return HttpResponse(status=200)


