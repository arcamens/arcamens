# Models for Note post type.
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from board_app.models import Event

class CardComment(models.Model):
    file = models.FileField(upload_to='media/', 
    null=True, blank=True, verbose_name='Document')

    card = models.ForeignKey('card_app.Card', 
    null=True, blank=True)

    user = models.ForeignKey('core_app.User', 
    null=True, blank=True)

    data = models.CharField(
    null=True, blank=False, max_length=256)

    created = models.DateTimeField(
    auto_now=True, null=True)

    def get_absolute_url(self):
        url = reverse('card_comment_app:comment', 
        kwargs={'comment_id': self.id})
        return url

    def __str__(self):
        return self.data

class ECreateCardComment(Event):
    child = models.ForeignKey('card_app.Card', 
    blank=True)

    comment = models.ForeignKey('CardComment', 
    blank=True)

    def get_absolute_url(self):
        return reverse(
            'card_comment_app:e-create-comment', 
                 kwargs={'event_id': self.id})

    def __str__(self):
        return self.comment


















