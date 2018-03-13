from django.views.generic import View
from django.shortcuts import render, redirect
from timeline_app.views import GuardianView
import timeline_app.models
import post_app.models
from . import models
from . import forms
from core_app import ws

class ListPostComments(GuardianView):
    """
    """

    def get(self, request, post_id):
        post    = post_app.models.Post.objects.get(id=post_id)
        records = post.postcomment_set.order_by('-created')
        return render(request, 'comment_app/list-comments.html', 
        {'form':forms.PostCommentForm(), 'post': post, 'records': records})

class CreatePostComment(GuardianView):
    def post(self, request, post_id):
        user = timeline_app.models.User.objects.get(id=self.user_id)
        post = post_app.models.Post.objects.get(id=post_id)
        records = post.postcomment_set.order_by('-created')
        form = forms.PostCommentForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, 'comment_app/list-comments.html',
                {'form': form, 'post':post, 'records': records}, status=400)

        record      = form.save(commit = False)
        record.post = post
        record.user = user
        record.save()

        event = models.ECreatePostComment.objects.create(
        organization=user.default,comment=record, post=post, user=user)
    
        scope = post.ancestor.users.all() | post.workers.all()
        event.users.add(*scope)

        post.ancestor.ws_sound()

        return redirect('comment_app:list-comments', 
        post_id=post.id)

class ECreatePostComment(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.ECreatePostComment.objects.get(id=event_id)
        return render(request, 'comment_app/e-create-comment.html', 
        {'event':event})
















