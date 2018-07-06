from django.views.generic import View
from django.shortcuts import render, redirect
from group_app.views import GuardianView
import group_app.models
import core_app.models
from . import models
from . import forms

class ListComments(GuardianView):
    """
    """

    def get(self, request, event_id):
        event    = core_app.models.Event.objects.get(id=event_id)
        records = event.comment_set.order_by('-created')
        return render(request, 'comment_app/list-comments.html', 
        {'form':forms.CommentForm(), 'event': event, 'records': records})

class CreateComment(GuardianView):
    def post(self, request, event_id):
        event = core_app.models.Event.objects.get(id=event_id)
        records = event.comment_set.order_by('-created')
        form = forms.CommentForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, 'comment_app/list-comments.html',
                {'form': form, 'event':event, 'records': records}, status=400)

        record      = form.save(commit = False)
        record.event = event
        record.user = self.me
        record.save()

        target = models.ECreateComment.objects.create(
        organization=self.me.default,comment=record, 
        event=event, user=self.me)

        scope = event.users.all() | event.signers.all()
        target.dispatch(*scope)
        target.save()

        return redirect('comment_app:list-comments', 
        event_id=event.id)

class ECreateComment(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.ECreateComment.objects.get(id=event_id)
        return render(request, 'comment_app/e-create-comment.html', 
        {'event':event})
























