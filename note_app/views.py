from django.views.generic import View
from django.conf import settings
from django.db.models import Q
from django.shortcuts import render, redirect
from core_app.views import GuardianView, FileDownload
from jscroll.wrappers import JScroll
from django.http import HttpResponse
from card_app.models import Card
from core_app.models import User, Event
from note_app.models import Note, NoteSearch, ERestoreNote, EUpdateNote
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

        event = models.EUpdateNote.objects.create(note_data=record.data,
        organization=self.me.default, child=record.card, note_html=record.html,
        note=record, user=self.me)

        form = forms.NoteForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'note_app/update-note.html',
                        {'form': form, 'note':record, }, status=400)

        record.save()
        event.dispatch(*record.card.ancestor.ancestor.members.all())
        event.save()

        return redirect('note_app:preview-note', 
        note_id=record.id)

class DeleteNote(GuardianView):
    def post(self, request, note_id):
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

class NoteDiff(GuardianView):
    def get(self, request, event_id):
        event = models.EUpdateNote.objects.get(id=event_id)
        note = models.Note.locate(self.me, self.me.default, event.note.id)


        return render(request, 'note_app/note-diff.html', 
        {'note': note, 'event': event, 'card': note.card})

class Find(GuardianView):
    def get(self, request):
        filter, _ = NoteSearch.objects.get_or_create(
        user=self.me, organization=self.me.default)

        form   = forms.NoteSearchForm(instance=filter)

        notes = models.Note.objects.filter(
        Q(card__ancestor__ancestor__members=self.me) &
        Q(card__ancestor__ancestor__organization=self.me.default) |\
        Q(card__workers=self.me)).distinct()

        total  = notes.count()

        sqlike = models.Note.from_sqlike()

        sqlike.feed(filter.pattern)

        notes = sqlike.run(notes)
        count = notes.count()

        notes = notes.only('card__label', 'card__id', 'data', 'id').order_by('id')
        elems = JScroll(self.me.id, 'note_app/find-scroll.html', notes)

        return render(request, 'note_app/find.html', 
        {'form': form, 'elems':  elems.as_div(), 'total': total, 'count': count})

    def post(self, request):
        filter, _ = NoteSearch.objects.get_or_create(
        user=self.me, organization=self.me.default)

        sqlike = models.Note.from_sqlike()
        form  = forms.NoteSearchForm(request.POST, sqlike=sqlike, instance=filter)

        notes = models.Note.objects.filter(
        Q(card__ancestor__ancestor__members=self.me) &
        Q(card__ancestor__ancestor__organization=self.me.default) |\
        Q(card__workers=self.me)).distinct()

        total = notes.count()

        if not form.is_valid():
            return render(request, 'note_app/find.html', 
                {'form': form, 'total': total, 'count': 0}, status=400)
        form.save()

        notes = sqlike.run(notes)

        count =  notes.count()
        notes = notes.only('card__label', 'card__id', 'data', 'id').order_by('id')
        elems = JScroll(self.me.id, 'note_app/find-scroll.html', notes)

        return render(request, 'note_app/find.html', 
        {'form': form, 'elems':  elems.as_div(), 'total': total, 'count': count})


class RestoreNote(GuardianView):
    def post(self, request, event_id):
        event = EUpdateNote.objects.get(id=event_id)
        note  = models.Note.locate(self.me, self.me.default, event.note.id)

        note.data = event.note_data
        note.save()

        event = models.ERestoreNote.objects.create(
        event_html=event.html, organization=self.me.default, 
        card=note.card, note=note, user=self.me)

        event.dispatch(*note.card.ancestor.ancestor.members.all())
        event.save()
        return redirect('note_app:preview-note', note_id=note.id)

class NoteEvents(GuardianView):
    def get(self, request, note_id):
        note = models.Note.locate(self.me, self.me.default, note_id)

        query = Q(ecreatenote__note__id=note.id) | \
        Q(eupdatenote__note__id=note.id) |\
        Q(eattachnotefile__note__id=note.id) |\
        Q(edettachnotefile__note__id=note.id)|\
        Q(erestorenote__id=note.id)

        events = Event.objects.filter(query).order_by('-created').values('html')
        count = events.count()

        return render(request, 'note_app/note-events.html', 
        {'note': note, 'elems': events, 'count': count})




