from django.views.generic import View
from django.shortcuts import render, redirect
from board_app.views import GuardianView
from django.http import HttpResponse
from django.conf import settings
import board_app.models
import post_app.models
import core_app.models
from . import models
from . import forms

class Snippet(GuardianView):
    def get(self, request, snippet_id):
        snippet = models.Snippet.objects.get(id=snippet_id)

        # First check if someone has cut this post.
        # Posts on clipboard shouldnt be accessed due to generating
        # too many inconsistencies.
        # on_clipboard = not (post.ancestor and post.ancestor.ancestor)
# 
        # if on_clipboard:
            # return HttpResponse("This post is on clipboard! \
               # It can't be accessed.", status=400)

        attachments = snippet.snippetfilewrapper_set.all()

        return render(request, 'snippet_app/snippet.html', 
        {'snippet': snippet, 'post': snippet.post, 'attachments': attachments})


class SnippetLink(GuardianView):
    def get(self, request, snippet_id):
        snippet = models.Snippet.objects.get(id=snippet_id,
        post__ancestor__organization=self.me.default)

        organizations = self.me.organizations.exclude(id=self.me.default.id)

        return render(request, 'snippet_app/snippet-link.html', 
        {'snippet': snippet, 'post': snippet.post, 'user': self.me, 
        'organizations': organizations, 'default': self.me.default, 
        'organization': self.me.default, 'settings': settings})

class CreateSnippet(GuardianView):
    """
    """

    def get(self, request, post_id):
        post = post_app.models.Post.objects.get(id=post_id)
        form = forms.SnippetForm()

        return render(request, 'snippet_app/create-snippet.html', 
        {'form':form, 'post': post})

    def post(self, request, post_id):
        post = post_app.models.Post.objects.get(id=post_id)
        form = forms.SnippetForm(request.POST)

        if not form.is_valid():
            return render(request, 'snippet_app/create-snippet.html', 
                {'form': form, 'post':post,}, status=400)

        snippet       = form.save(commit=False)
        snippet.owner = self.me
        snippet.post  = post
        snippet.save()

        event = models.ECreateSnippet.objects.create(
        organization=self.me.default, child=post, user=self.me, snippet=snippet)
        event.dispatch(*post.ancestor.users.all())

        return redirect('post_app:refresh-post', post_id=post.id)

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

        event = models.EAttachSnippetFile.objects.create(
        organization=self.me.default, filewrapper=record, 
        snippet=snippet, user=self.me)

        event.dispatch(*snippet.post.ancestor.users.all())
        event.save()

        return self.get(request, snippet_id)

class DetachFile(GuardianView):
    """
    """

    def get(self, request, filewrapper_id):
        filewrapper = models.SnippetFileWrapper.objects.get(id=filewrapper_id)
        attachments = filewrapper.snippet.snippetfilewrapper_set.all()

        form = forms.SnippetFileWrapperForm()

        event = models.EDettachSnippetFile.objects.create(
        organization=self.me.default, filename=filewrapper.file.name, 
        snippet=filewrapper.snippet, user=self.me)

        event.dispatch(*filewrapper.snippet.post.ancestor.users.all())
        event.save()

        filewrapper.delete()

        return render(request, 'snippet_app/attach-file.html', 
        {'snippet':filewrapper.snippet, 'form': form, 'attachments': attachments})

class UpdateSnippet(GuardianView):
    def get(self, request, snippet_id):
        snippet = models.Snippet.objects.get(id=snippet_id)
        return render(request, 'snippet_app/update-snippet.html',
        {'snippet': snippet, 'post': snippet.post, 
        'form': forms.SnippetForm(instance=snippet),})

    def post(self, request, snippet_id):
        record  = models.Snippet.objects.get(id=snippet_id)
        form    = forms.SnippetForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'snippet_app/update-snippet.html',
                {'form': form, 'post': snippet.post, 
                    'snippet':record, }, status=400)

        record.save()

        event = models.EUpdateSnippet.objects.create(
        organization=self.me.default, child=record.post, 
        snippet=record, user=self.me)

        event.dispatch(*record.post.ancestor.users.all())
        event.save()

        return redirect('snippet_app:snippet', 
        snippet_id=record.id)

class DeleteSnippet(GuardianView):
    def get(self, request, snippet_id):
        snippet = models.Snippet.objects.get(id = snippet_id)

        event = models.EDeleteSnippet.objects.create(organization=self.me.default,
        child=snippet.post, snippet=snippet.title, user=self.me)

        event.dispatch(*snippet.post.ancestor.users.all())
        snippet.delete()

        return redirect('post_app:refresh-post', 
        post_id=snippet.post.id)

class CancelSnippetCreation(GuardianView):
    def get(self, request, snippet_id):
        snippet = models.Snippet.objects.get(id = snippet_id)
        snippet.delete()

        return HttpResponse(status=200)











