from django.views.generic import View
from django.shortcuts import render, redirect
from group_app.views import GuardianView
import group_app.models
import core_app.models
from . import models
from . import forms


class CreateFeedback(GuardianView):
    def get(self, request, event_id):
        event = core_app.models.Event.objects.get(id=event_id)
        records = event.e_create_feedback1.order_by('-created')

        return render(request, 'feedback_app/create-feedback.html', 
        {'form':forms.ECreateFeedbackForm(), 'event': event, 'records': records})

    def post(self, request, event_id):
        event = core_app.models.Event.objects.get(id=event_id)
        records = event.e_create_feedback1.order_by('-created')
        form = forms.ECreateFeedbackForm(request.POST)

        if not form.is_valid():
            return render(request, 'feedback_app/create-feedback.html',
                {'form': form, 'event':event, 'records': records}, status=400)

        record      = form.save(commit = False)
        record.event = event
        record.user = self.me
        record.organization=self.me.default
        record.save()

        scope = event.users.all() | event.signers.all()
        record.dispatch(*scope)

        return redirect('feedback_app:create-feedback', event_id=event_id)

