from django.views.generic import View
from django.shortcuts import render, redirect
from timeline_app.views import GuardianView
import timeline_app.models
import core_app.models
from . import models
from . import forms
from core_app import ws

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
        user = timeline_app.models.User.objects.get(id=self.user_id)
        event = core_app.models.Event.objects.get(id=event_id)
        records = event.comment_set.order_by('-created')
        form = forms.CommentForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, 'comment_app/list-comments.html',
                {'form': form, 'event':event, 'records': records}, status=400)

        record      = form.save(commit = False)
        record.event = event
        record.user = user
        record.save()

        target = models.ECreateComment.objects.create(
        organization=user.default,comment=record, 
        event=event, user=user)
    
        target.users.add(*event.users.all())
        target.save()

        # event.ancestor.ws_sound()

        return redirect('comment_app:list-comments', 
        event_id=event.id)

class ECreateComment(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.ECreateComment.objects.get(id=event_id)
        return render(request, 'comment_app/e-create-comment.html', 
        {'event':event})


















