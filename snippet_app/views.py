from django.views.generic import View
from django.shortcuts import render, redirect
from board_app.views import GuardianView
from django.http import HttpResponse
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

        user = core_app.models.User.objects.get(id=self.user_id)
        attachments = snippet.snippetfilewrapper_set.all()

        return render(request, 'snippet_app/snippet.html', 
        {'snippet': snippet, 'post': snippet.post, 'attachments': attachments})


class SnippetLink(GuardianView):
    def get(self, request, snippet_id):
        snippet = models.Snippet.objects.get(id=snippet_id)

        return render(request, 'snippet_app/snippet-link.html', 
        {'snippet': snippet, 'post': snippet.post})

class CreateSnippet(GuardianView):
    """
    """

    def get(self, request, post_id, snippet_id=None):
        post = post_app.models.Post.objects.get(id=post_id)
        user = core_app.models.User.objects.get(id=self.user_id)
        snippet = models.Snippet.objects.create(owner=user, post=post)
        post.save()

        form = forms.SnippetForm(instance=snippet)
        return render(request, 'snippet_app/create-snippet.html', 
        {'form':form, 'post': post, 'snippet':snippet})

    def post(self, request, post_id, snippet_id):
        post = post_app.models.Post.objects.get(id=post_id)

        snippet = models.Snippet.objects.get(id=snippet_id)
        form = forms.SnippetForm(request.POST, instance=snippet)
        user = core_app.models.User.objects.get(id=self.user_id)

        if not form.is_valid():
            return render(request, 'snippet_app/create-snippet.html', 
                {'form': form, 'post':post, 'snippet': snippet}, status=400)

        snippet.save()

        event = models.ECreateSnippet.objects.create(
        organization=user.default, child=post, user=user, snippet=snippet)
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
        return self.get(request, snippet_id)

class DetachFile(GuardianView):
    """
    """

    def get(self, request, filewrapper_id):
        filewrapper = models.SnippetFileWrapper.objects.get(id=filewrapper_id)
        filewrapper.delete()
        attachments = filewrapper.snippet.snippetfilewrapper_set.all()

        form = forms.SnippetFileWrapperForm()
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

        user  = core_app.models.User.objects.get(id=self.user_id)

        event = models.EUpdateSnippet.objects.create(
        organization=user.default, child=record.post, 
        snippet=record, user=user)

        event.dispatch(*record.post.ancestor.users.all())
        event.save()

        return redirect('snippet_app:snippet', 
        snippet_id=record.id)

class DeleteSnippet(GuardianView):
    def get(self, request, snippet_id):
        snippet = models.Snippet.objects.get(id = snippet_id)

        user = core_app.models.User.objects.get(id=self.user_id)

        event = models.EDeleteSnippet.objects.create(organization=user.default,
        child=snippet.post, snippet=snippet.title, user=user)

        event.dispatch(*snippet.post.ancestor.users.all())
        snippet.delete()

        return redirect('post_app:refresh-post', 
        post_id=snippet.post.id)

class CancelSnippetCreation(GuardianView):
    def get(self, request, snippet_id):
        snippet = models.Snippet.objects.get(id = snippet_id)
        snippet.delete()

        return HttpResponse(status=200)







