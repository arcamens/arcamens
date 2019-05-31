# Models for Note post type.
from django.db import models
from django.db.models import Q
from sqlike.parser import SqLike, SqNode
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from mdx_gfm import GithubFlavoredMarkdownExtension
from markdown.extensions.tables import TableExtension
from markdown import markdown
from board_app.models import Event
from card_app.models import clean_disk

class NoteMixin(object):
    @classmethod
    def locate(cls, user, organization, note_id):
        """
        Return the requested note only if the user has access to the note
        by belonging to the note's card group or being a worker of the card.

        It also checks if the note is on someone's clipboard, if it is
        then the note is not supposed to be viewable.
        """

        note = cls.objects.filter(
        Q(card__ancestor__ancestor__members=user) | Q(card__workers=user), 
        card__ancestor__ancestor__organization=organization, id=note_id,
        card__card_clipboard_users__isnull=True).distinct()

        return note.first()

    @classmethod
    def from_sqlike(cls):
        owner   = lambda ind: Q(owner__name__icontains=ind) | Q(
        owner__email__icontains=ind)
        not_owner = lambda ind: ~owner(ind)

        data     = lambda ind: Q(data__icontains=ind)
        not_data = lambda ind: ~data(ind)
        default  = lambda ind: Q(data__icontains=ind) 

        sqlike = SqLike(cls, SqNode(None, default),
        SqNode(('o', 'owner'), owner),
        SqNode(('!o', '!owner'), not_owner),
        SqNode(('d', 'data'), data),
        SqNode(('!d', '!data'), not_data),)
        return sqlike

    def save(self, *args, **kwargs):
        self.html = markdown(self.data,
        extensions=[TableExtension(), GithubFlavoredMarkdownExtension()], safe_mode=True,  
        enable_attributes=False)
        super(NoteMixin, self).save(*args, **kwargs)

    def get_link_url(self):
        return reverse('note_app:note-link', 
                    kwargs={'note_id': self.id})

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
    organization = models.ForeignKey('core_app.Organization', 
    null=False, on_delete=models.CASCADE)

    note = models.ForeignKey('Note', null=True, 
    on_delete=models.CASCADE, blank=True)

    file = models.FileField(
    verbose_name='', help_text='')

class Note(NoteMixin, models.Model):
    card = models.ForeignKey('card_app.Card', 
    null=False, related_name='notes', on_delete=models.CASCADE)

    owner = models.ForeignKey('core_app.User', 
    null=True, on_delete=models.CASCADE)

    data = models.TextField(null=True, 
    blank=True, verbose_name=_("Data"), 
    help_text='Markdown content.', default='')

    created = models.DateTimeField(auto_now_add=True, null=True)

    html = models.TextField(null=True, blank=True)

    def get_absolute_url(self):
        url = reverse('card_feedback_app:feedback', 
        kwargs={'feedback_id': self.id})
        return url

    def __str__(self):
        return self.data

class NoteSearchMixin(models.Model):
    class Meta:
        abstract = True

class NoteSearch(NoteSearchMixin):
    pattern  = models.CharField(max_length=255, 
    blank=True, default='', help_text='')

    organization = models.ForeignKey('core_app.Organization', 
    null=False, on_delete=models.CASCADE)

    user = models.ForeignKey('core_app.User',
    null=False, on_delete=models.CASCADE)

    done = models.BooleanField(blank=True, default=False)

    class Meta:
        unique_together = ('user', 'organization', )

class ECreateNote(Event):
    child = models.ForeignKey('card_app.Card', 
    null=True, on_delete=models.CASCADE)

    note = models.ForeignKey('Note', 
    null=True, on_delete=models.CASCADE)
    html_template = 'note_app/e-create-note.html'

    def __str__(self):
        return self.user.name

class EDeleteNote(Event):
    child = models.ForeignKey('card_app.Card', 
    null=True, on_delete=models.CASCADE)

    note = models.CharField(null=True, 
    blank=False, max_length=626)

    html_template = 'note_app/e-delete-note.html'

    def __str__(self):
        return self.user.name



class EUpdateNote(Event):
    child = models.ForeignKey('card_app.Card', 
    null=True, on_delete=models.CASCADE)

    note = models.ForeignKey('Note', 
    null=True, on_delete=models.CASCADE)

    note_html = models.TextField(null=True, blank=True)

    note_data = models.TextField(blank=True, 
    verbose_name=_("Data"), help_text='Markdown content.', default='')

    html_template = 'note_app/e-update-note.html'

    def __str__(self):
        return self.user.name

class ERestoreNote(Event):
    """
    """

    card = models.ForeignKey('card_app.Card', 
    related_name='e_restore_note0', null=True, on_delete=models.CASCADE)

    note = models.ForeignKey('Note', 
    related_name='e_restore_note1', null=True, on_delete=models.CASCADE)

    event_html    = models.TextField(null=True, blank=True)
    html_template = 'note_app/e-restore-note.html'

class EAttachNoteFile(Event):
    """
    """

    filewrapper = models.ForeignKey('NoteFileWrapper', 
    related_name='e_attach_note_file0', null=True, on_delete=models.CASCADE)

    note = models.ForeignKey('Note', 
    related_name='e_attach_note_file1', null=True, on_delete=models.CASCADE)

    html_template = 'note_app/e-attach-note-file.html'

class EDettachNoteFile(Event):
    """
    """
    filename = models.CharField(null=True, max_length=626)
    note = models.ForeignKey('Note', 
    related_name='e_dettach_note_file1', null=True, on_delete=models.CASCADE)

    html_template = 'note_app/e-dettach-note-file.html'

# It is not necessary at all bacause notes arent
# copied altogether with cards but it might be necessary
# in the future..
@receiver(pre_delete, sender=NoteFileWrapper)
def delete_filewrapper(sender, instance, **kwargs):
    is_unique = NoteFileWrapper.objects.filter(file=instance.file)
    is_unique = is_unique.count() == 1
    if is_unique: 
        clean_disk(instance)







