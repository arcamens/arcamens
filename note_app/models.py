# Models for Note post type.
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from markdown.extensions.tables import TableExtension
from markdown import markdown
from board_app.models import Event

class NoteMixin(object):
    def save(self, *args, **kwargs):
        self.html = markdown(self.data, 
            extensions=[TableExtension(),
                'markdown.extensions.tables'])
        super(NoteMixin, self).save(*args, **kwargs)

    def __str__(self):
        """
        """
        return self.label

class NoteFileWrapperMixin(object):
    def duplicate(self, card=None):
        wrapper       = NoteFileWrapper.objects.get(id=self.id)
        wrapper.pk    = None
        wrapper.card  = card
        wrapper.save()
        return wrapper

class NoteFileWrapper(NoteFileWrapperMixin, models.Model):
    """
    """

    note = models.ForeignKey('Note', null=True, 
    on_delete=models.CASCADE, blank=True)

    file = models.FileField(upload_to='media/', 
    verbose_name='', help_text='')

class Note(NoteMixin, models.Model):
    card = models.ForeignKey('card_app.Card', 
    null=True, related_name='notes', blank=True)

    owner = models.ForeignKey('core_app.User', 
    null=True, blank=True)

    title = models.CharField(null=True, blank=False, 
    default='Draft', verbose_name=_("Title"), 
    max_length=626)

    data = models.TextField(null=True,
    blank=True, verbose_name=_("Data"), 
    help_text='Markdown content.', default='')

    created = models.DateTimeField(
    auto_now=True, null=True)

    html = models.TextField(null=True, blank=True)

    def get_absolute_url(self):
        url = reverse('card_comment_app:comment', 
        kwargs={'comment_id': self.id})
        return url

    def __str__(self):
        return self.data

class ECreateNote(Event):
    child = models.ForeignKey('card_app.Card', 
    blank=True)

    note = models.ForeignKey('Note', 
    blank=True)

    def get_absolute_url(self):
        return reverse(
            'note_app:e-create-note', 
                 kwargs={'event_id': self.id})

    def __str__(self):
        return self.user.name



