from django.views.generic import View
from django.shortcuts import render, redirect
from board_app.views import GuardianView
from django.http import HttpResponse
import board_app.models
import card_app.models
import core_app.models
from . import models
from . import forms

class Snippet(GuardianView):
    def get(self, request, snippet_id):
        snippet = models.Snippet.objects.get(id=snippet_id)

        # First check if someone has cut this card.
        # Cards on clipboard shouldnt be accessed due to generating
        # too many inconsistencies.
        # on_clipboard = not (card.ancestor and card.ancestor.ancestor)
# 
        # if on_clipboard:
            # return HttpResponse("This card is on clipboard! \
               # It can't be accessed.", status=400)

        user = core_app.models.User.objects.get(id=self.user_id)
        attachments = snippet.snippetfilewrapper_set.all()

        return render(request, 'snippet_app/snippet.html', 
        {'snippet': snippet, 'card': snippet.card, 'attachments': attachments})


class CreateSnippet(GuardianView):
    """
    """

    def get(self, request, card_id, snippet_id=None):
        card = card_app.models.Card.objects.get(id=card_id)
        user = core_app.models.User.objects.get(id=self.user_id)
        snippet = models.Snippet.objects.create(owner=user, 
        card=card)
        card.save()

        form = forms.SnippetForm(instance=snippet)
        return render(request, 'snippet_app/create-snippet.html', 
        {'form':form, 'card': card, 'snippet':snippet})

    def post(self, request, card_id, snippet_id):
        card = card_app.models.Card.objects.get(id=card_id)

        snippet = models.Snippet.objects.get(id=snippet_id)
        form = forms.SnippetForm(request.POST, instance=snippet)
        user = core_app.models.User.objects.get(id=self.user_id)

        if not form.is_valid():
            return render(request, 'snippet_app/create-snippet.html', 
                {'form': form, 'card':card, 'snippet': snippet}, status=400)

        snippet.save()

        event = models.ECreateSnippet.objects.create(
        organization=user.default, child=card, user=user, snippet=snippet)
        event.dispatch(*card.ancestor.ancestor.members.all())

        user.ws_sound(card.ancestor.ancestor)

        return redirect('card_app:view-data', card_id=card.id)

class AttachFile(GuardianView):
    """
    """

    def get(self, request, snippet_id):
        snippet = models.Snippet.objects.get(id=snippet_id)
        attachments = snippet.snippetfilewrapper_set.all()
        form = forms.SnippetFileWrapperForm()

        return render(request, 'snippet_app/attach-file.html', 
        {'snippet':snippet, 'form': form, 'attachments': attachments})

    def post(self, request, snippet_id):
        snippet = models.Snippet.objects.get(id=snippet_id)
        attachments = snippet.snippetfilewrapper_set.all()
        form = forms.SnippetFileWrapperForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, 'snippet_app/attach-file.html', 
                {'snippet':snippet, 'form': form, 'attachments': attachments})
        record = form.save(commit = False)
        record.snippet = snippet
        form.save()
        return self.get(request, snippet_id)

class DetachFile(GuardianView):
    """
    """

    def get(self, request, filewrapper_id):
        filewrapper = models.SnippetFileWrapper.objects.get(id=filewrapper_id)
        filewrapper.delete()
        attachments = filewrapper.snippet.filewrapper_set.all()

        form = forms.FileWrapperForm()
        return render(request, 'snippet_app/attach-file.html', 
        {'snippet':filewrapper.snippet, 'form': form, 'attachments': attachments})

class UpdateSnippet(GuardianView):
    def get(self, request, snippet_id):
        snippet = models.Snippet.objects.get(id=snippet_id)
        return render(request, 'snippet_app/update-snippet.html',
        {'snippet': snippet, 'card': snippet.card, 
        'form': forms.SnippetForm(instance=snippet),})

    def post(self, request, snippet_id):
        record  = models.Snippet.objects.get(id=snippet_id)
        form    = forms.SnippetForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'snippet_app/update-snippet.html',
                {'form': form, 'card': snippet.card, 
                    'snippet':record, }, status=400)

        record.save()

        user  = core_app.models.User.objects.get(id=self.user_id)

        event = models.EUpdateSnippet.objects.create(
        organization=user.default, child=record.card, 
        snippet=record, user=user)

        event.dispatch(*record.card.ancestor.ancestor.members.all())
        event.save()

        user.ws_sound(record.card.ancestor.ancestor)

        return redirect('snippet_app:snippet', 
        snippet_id=record.id)

class DeleteSnippet(GuardianView):
    def get(self, request, snippet_id):
        snippet = models.Snippet.objects.get(id = snippet_id)

        user = core_app.models.User.objects.get(id=self.user_id)

        event = models.EDeleteSnippet.objects.create(organization=user.default,
        child=snippet.card, snippet=snippet.title, user=user)

        event.dispatch(*snippet.card.ancestor.ancestor.members.all())
        snippet.delete()

        user.ws_sound(snippet.card.ancestor.ancestor)

        return redirect('card_app:view-data', 
        card_id=snippet.card.id)

class CancelSnippetCreation(GuardianView):
    def get(self, request, snippet_id):
        snippet = models.Snippet.objects.get(id = snippet_id)
        snippet.delete()

        return HttpResponse(status=200)



