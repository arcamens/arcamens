from django.views.generic import View
from django.shortcuts import render, redirect
from django.db.models import Q
from core_app.views import GuardianView, FileDownload, Event
from django.http import HttpResponse
from django.conf import settings
from post_app.models import Post
from comment_app.models import CommentSearch, EUpdateComment, ERestoreComment
from jscroll.wrappers import JScroll
import board_app.models
import core_app.models
from . import models
from . import forms

class Comment(GuardianView):
    def get(self, request, comment_id):
        comment = models.Comment.locate(self.me, self.me.default, comment_id)

        attachments = comment.commentfilewrapper_set.all()

        return render(request, 'comment_app/comment.html', 
        {'comment': comment, 'post': comment.post, 'attachments': attachments})

class CommentLink(GuardianView):
    def get(self, request, comment_id):
        comment = models.Comment.locate(self.me, self.me.default, comment_id)

        organizations = self.me.organizations.exclude(id=self.me.default.id)

        return render(request, 'comment_app/comment-link.html', 
        {'comment': comment, 'post': comment.post, 'user': self.me, 
        'organizations': organizations, 'default': self.me.default, 
        'organization': self.me.default, 'settings': settings})

class CreateComment(GuardianView):
    """
    """

    def get(self, request, post_id):
        # Make sure i have access to the post.
        post = Post.locate(self.me, self.me.default, post_id)
        form = forms.CommentForm()

        return render(request, 'comment_app/create-comment.html', 
        {'form':form, 'post': post})

    def post(self, request, post_id):
        post = Post.locate(self.me, self.me.default, post_id)
        form = forms.CommentForm(request.POST)

        if not form.is_valid():
            return render(request, 'comment_app/create-comment.html', 
                {'form': form, 'post':post,}, status=400)

        comment       = form.save(commit=False)
        comment.owner = self.me
        comment.post  = post
        comment.save()

        event = models.ECreateComment.objects.create(
        organization=self.me.default, child=post, user=self.me, comment=comment)
        event.dispatch(*post.ancestor.users.all())

        return redirect('post_app:refresh-post', post_id=post.id)

class AttachFile(GuardianView):
    """
    """

    def get(self, request, comment_id):
        comment = models.Comment.locate(self.me, self.me.default, comment_id)

        attachments = comment.commentfilewrapper_set.all()
        form = forms.CommentFileWrapperForm()

        return render(request, 'comment_app/attach-file.html', 
        {'comment':comment, 'form': form, 'attachments': attachments})

    def post(self, request, comment_id):
        comment = models.Comment.locate(self.me, self.me.default, comment_id)
        attachments = comment.commentfilewrapper_set.all()

        form = forms.CommentFileWrapperForm(request.POST, 
        request.FILES, user=self.me)

        if not form.is_valid():
            return render(request, 'comment_app/attach-file.html', 
                {'comment':comment, 'form': form, 'attachments': attachments})
        record = form.save(commit = False)
        record.organization = self.me.default
        record.comment = comment
        form.save()

        event = models.EAttachCommentFile.objects.create(
        organization=self.me.default, filewrapper=record, 
        comment=comment, user=self.me)

        event.dispatch(*comment.post.ancestor.users.all())
        event.save()

        return self.get(request, comment_id)

class DetachFile(GuardianView):
    """
    """

    def get(self, request, filewrapper_id):
        # Make sure i can access the post through the post group
        # or being a worker of the post.
        filewrapper = models.CommentFileWrapper.objects.filter(
        Q(comment__post__ancestor__users=self.me) | Q(comment__post__workers=self.me),
        comment__post__ancestor__organization=self.me.default, 
        id=filewrapper_id).distinct().first()

        attachments = filewrapper.comment.commentfilewrapper_set.all()

        form = forms.CommentFileWrapperForm()

        event = models.EDettachCommentFile.objects.create(
        organization=self.me.default, filename=filewrapper.file.name, 
        comment=filewrapper.comment, user=self.me)

        event.dispatch(*filewrapper.comment.post.ancestor.users.all())
        event.save()

        filewrapper.delete()

        return render(request, 'comment_app/attach-file.html', 
        {'comment':filewrapper.comment, 'form': form, 'attachments': attachments})

class UpdateComment(GuardianView):
    def get(self, request, comment_id):
        comment = models.Comment.locate(self.me, self.me.default, comment_id)
        return render(request, 'comment_app/update-comment.html',
        {'comment': comment, 'post': comment.post, 
        'form': forms.CommentForm(instance=comment),})

    def post(self, request, comment_id):
        record = models.Comment.locate(self.me, self.me.default, comment_id)
        event  = models.EUpdateComment.objects.create(comment_title=record.title,
        organization=self.me.default, child=record.post, comment_data=record.data,
        comment=record, user=self.me, comment_html=record.html)

        form = forms.CommentForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'comment_app/update-comment.html',
                {'form': form, 'post': comment.post, 
                    'comment':record, }, status=400)

        record.save()
        event.dispatch(*record.post.ancestor.users.all())
        event.save()

        return redirect('comment_app:comment', 
        comment_id=record.id)

class DeleteComment(GuardianView):
    def post(self, request, comment_id):
        comment = models.Comment.locate(self.me, self.me.default, comment_id)

        event = models.EDeleteComment.objects.create(organization=self.me.default,
        child=comment.post, comment=comment.title, user=self.me)

        event.dispatch(*comment.post.ancestor.users.all())
        comment.delete()

        return redirect('post_app:refresh-post', 
        post_id=comment.post.id)


class CommentFileDownload(FileDownload):
    def get(self, request, filewrapper_id):
        filewrapper = models.CommentFileWrapper.objects.filter(
        Q(comment__post__ancestor__users=self.me) | Q(comment__post__workers=self.me),
        comment__post__ancestor__organization=self.me.default, 
        id=filewrapper_id).distinct().first()

        return self.get_file_url(filewrapper.file)

class CommentDiff(GuardianView):
    def get(self, request, event_id):
        event = models.EUpdateComment.objects.get(id=event_id)
        comment = models.Comment.locate(self.me, self.me.default, event.comment.id)


        return render(request, 'comment_app/comment-diff.html', 
        {'comment': comment, 'event': event, 'post': comment.post})

class Find(GuardianView):
    def get(self, request):
        filter, _ = CommentSearch.objects.get_or_create(
        user=self.me, organization=self.me.default)

        form   = forms.CommentSearchForm(instance=filter)

        comments = models.Comment.objects.filter(
        Q(post__ancestor__users=self.me) &
        Q(post__ancestor__organization=self.me.default) |\
        Q(post__workers=self.me)).distinct()

        total  = comments.count()

        sqlike = models.Comment.from_sqlike()

        sqlike.feed(filter.pattern)

        comments = sqlike.run(comments)
        count = comments.count()

        comments = comments.only('post__label', 'post__id', 'data', 'id').order_by('id')
        elems = JScroll(self.me.id, 'comment_app/find-scroll.html', comments)

        return render(request, 'comment_app/find.html', 
        {'form': form, 'elems':  elems.as_div(), 'total': total, 'count': count})

    def post(self, request):
        filter, _ = CommentSearch.objects.get_or_create(
        user=self.me, organization=self.me.default)

        sqlike = models.Comment.from_sqlike()
        form  = forms.CommentSearchForm(request.POST, sqlike=sqlike, instance=filter)

        comments = models.Comment.objects.filter(
        Q(post__ancestor__users=self.me) &
        Q(post__ancestor__organization=self.me.default) |\
        Q(post__workers=self.me)).distinct()

        total = comments.count()

        if not form.is_valid():
            return render(request, 'comment_app/find.html', 
                {'form': form, 'total': total, 'count': 0}, status=400)
        form.save()

        comments = sqlike.run(comments)

        count =  comments.count()
        comments = comments.only('post__label', 'post__id', 'data', 'id').order_by('id')
        elems = JScroll(self.me.id, 'comment_app/find-scroll.html', comments)

        return render(request, 'comment_app/find.html', 
        {'form': form, 'elems':  elems.as_div(), 'total': total, 'count': count})

class RestoreComment(GuardianView):
    def post(self, request, event_id):
        event   = EUpdateComment.objects.get(id=event_id)
        comment = models.Comment.locate(self.me, self.me.default, event.comment.id)

        comment.title = event.comment_title
        comment.data  = event.comment_data
        comment.save()

        event = models.ERestoreComment.objects.create(
        event_html=event.html, organization=self.me.default, 
        post=comment.post, comment=comment, user=self.me)

        event.dispatch(*comment.post.ancestor.users.all())
        event.save()
        return redirect('comment_app:comment', comment_id=comment.id)

class CommentEvents(GuardianView):
    def get(self, request, comment_id):
        comment = models.Comment.locate(self.me, self.me.default, comment_id)

        query = Q(ecreatecomment__comment__id=comment.id) | \
        Q(eupdatecomment__comment__id=comment.id) |\
        Q(eattachcommentfile__comment__id=comment.id) |\
        Q(edettachcommentfile__comment__id=comment.id)|\
        Q(erestorecomment__id=comment.id)

        events = Event.objects.filter(query).order_by('-created').values('html')
        count = events.count()

        return render(request, 'comment_app/comment-events.html', 
        {'comment': comment, 'elems': events, 'count': count})




