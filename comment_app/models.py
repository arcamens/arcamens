# Models for Note Event type.
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from timeline_app.models import Event
import timeline_app.models

class Comment(models.Model):
    event = models.ForeignKey('core_app.Event', null=True, blank=False)
    user = models.ForeignKey('core_app.User', null=True, blank=True)
    data = models.CharField(null=True, blank=False, max_length=256)

    file = models.FileField(null=True, blank=True, 
    verbose_name='Document')

    created = models.DateTimeField(
    auto_now=True, null=True)

    def get_absolute_url(self):
        return reverse('comment_app:comment', 
        kwargs={'comment_id': self.id})

    def __str__(self):
        return self.data


class ECreateComment(Event):
    target = models.ForeignKey('Comment', blank=True, 
    related_name='e_create_comment0')

    event = models.ForeignKey('core_app.Event', blank=True, 
    related_name='e_create_comment1')

    html_template = 'comment_app/e-create-comment.html'



