# Models for Note Event type.
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from group_app.models import Event
import group_app.models

class ECreateFeedback(Event):
    # No need to hold this ref because feedback events will
    # not have feedbacks on it.
    # target = models.ForeignKey('Feedback', blank=True, 
    # related_name='e_create_feedback0')

    event = models.ForeignKey('core_app.Event', null=False, on_delete=models.CASCADE,
    related_name='e_create_feedback1')
    data = models.CharField(null=True, blank=False, max_length=256)

    html_template = 'feedback_app/e-create-feedback.html'






