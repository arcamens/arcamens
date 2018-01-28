from django.utils.translation import ugettext_lazy as _
from markdown.extensions.tables import TableExtension
from django.core.urlresolvers import reverse
from core_app.models import Event, User, GlobalFilterMixin
from board_app.models import Board
from django.db.models import Q
from django.db import models
from markdown import markdown
import core_app

# Create your models here.

class CardMixin(object):
    def save(self, *args, **kwargs):
        self.html = markdown(self.data, 
            extensions=[TableExtension(),
                'markdown.extensions.tables'])
        super(CardMixin, self).save(*args, **kwargs)

    def duplicate(self, list=None):
        card          = Card.objects.get(id=self.id)
        card.pk       = None
        card.ancestor = list
        card.save()

        for ind in self.filewrapper_set.all():
            ind.duplicate(list)
        return card

    @classmethod
    def get_user_cards(cls, user):
        boards = Board.get_user_boards(user)
        cards  = Card.objects.none()

        for indi in boards:
            for indj in indi.lists.all():
                cards = cards | indj.cards.all()
        return cards

    def __str__(self):
        """
        """
        return self.label

class FileWrapperMixin(object):
    def duplicate(self, card=None):
        wrapper       = FileWrapper.objects.get(id=self.id)
        wrapper.pk    = None
        wrapper.card  = card
        wrapper.save()
        return wrapper

class Card(CardMixin, models.Model):
    """    
    """
    owner = models.ForeignKey('core_app.User', null=True, 
    blank=True)

    ancestor = models.ForeignKey('list_app.List', 
    null=True, related_name='cards', blank=True)

    created  = models.DateTimeField(auto_now_add=True, 
    null=True)

    label = models.CharField(null=True, blank=False, 
    verbose_name=_("Label"), help_text='Label, Priority, Deadline, ...', 
    max_length=626)

    data = models.TextField(null=True,
    blank=True, verbose_name=_("Data"), 
    help_text='Markdown content.', default='')

    workers = models.ManyToManyField('core_app.User', 
    null=True, related_name='tasks', blank=True, 
    symmetrical=False)

    relations = models.ManyToManyField('Card', 
    null=True, related_name='related', blank=True, 
    symmetrical=True)

    tags = models.ManyToManyField(
    'core_app.Tag', related_name='cards', 
    null=True, blank=True, symmetrical=False)
    done = models.BooleanField(blank=True, default=False)

    html = models.TextField(null=True, blank=True)

class Fork(Card):
    parent = models.ForeignKey('Card', null=True, related_name='forks',
    blank=True)

    path = models.ManyToManyField('Card', 
    null=True, related_name='children', blank=True, 
    symmetrical=False)

class CardClipboard(models.Model):
    user = models.ForeignKey('core_app.User', null=True, 
    blank=True)

    card = models.OneToOneField('Card', null=True, 
    related_name='selected', blank=True)

class ImageWrapper(models.Model):
    """
    """
    
    card = models.ForeignKey('Card', null=True, 
    on_delete=models.CASCADE, blank=True)

    file = models.ImageField(upload_to='media/', 
    verbose_name='', help_text='')

class FileWrapper(FileWrapperMixin, models.Model):
    """
    """

    card = models.ForeignKey('Card', null=True, 
    on_delete=models.CASCADE, blank=True)

    file = models.FileField(upload_to='media/', 
    verbose_name='', help_text='')

class ERelateCard(Event):
    """
    """

    ancestor0 = models.ForeignKey('list_app.List', 
    related_name='e_relate_card0', blank=True)

    ancestor1 = models.ForeignKey('list_app.List', 
    related_name='e_relate_card1', blank=True)

    child0 = models.ForeignKey('Card', 
    related_name='e_relate_card2', blank=True)

    child1 = models.ForeignKey('Card', 
    related_name='e_relate_card3', blank=True)

    def get_absolute_url(self):
        return reverse('card_app:e-relate-card', 
                    kwargs={'event_id': self.id})

class EUnrelateCard(Event):
    """
    """

    ancestor0 = models.ForeignKey('list_app.List', 
    related_name='e_unrelate_card0', blank=True)

    ancestor1 = models.ForeignKey('list_app.List', 
    related_name='e_unrelate_card1', blank=True)

    child0 = models.ForeignKey('Card', 
    related_name='e_unrelate_card2', blank=True)

    child1 = models.ForeignKey('Card', 
    related_name='e_unrelate_card3', blank=True)

    def get_absolute_url(self):
        return reverse('card_app:e-unrelate-card', 
                    kwargs={'event_id': self.id})

class ECreateCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_create_card0', blank=True)

    child = models.ForeignKey('Card', 
    related_name='e_create_card1', blank=True)

    def get_absolute_url(self):
        return reverse('card_app:e-create-card', 
                    kwargs={'event_id': self.id})

class EBindCardWorker(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_bind_card_worker0', blank=True)

    child = models.ForeignKey('Card', 
    related_name='e_bind_card_worker1', blank=True)

    peer = models.ForeignKey('core_app.User', 
    related_name='e_bind_card_worker2', blank=True)

    def get_absolute_url(self):
        return reverse('card_app:e-bind-card-worker', 
                    kwargs={'event_id': self.id})

class EUnbindCardWorker(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_unbind_card_worker0', blank=True)

    child = models.ForeignKey('Card', 
    related_name='e_unbind_card_worker1', blank=True)

    peer = models.ForeignKey('core_app.User', 
    related_name='e_unbind_card_worker2', blank=True)

    def get_absolute_url(self):
        return reverse('card_app:e-unbind-card-worker', 
                    kwargs={'event_id': self.id})

class ECreateFork(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_create_fork0', blank=True)

    child0 = models.ForeignKey('Card', 
    related_name='e_create_fork1', blank=True)

    child1 = models.ForeignKey('Card', 
    related_name='e_create_fork2', blank=True)

    def get_absolute_url(self):
        return reverse('card_app:e-create-fork', 
                    kwargs={'event_id': self.id})

class EUpdateCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_update_card0', blank=True)

    child = models.ForeignKey('Card', 
    related_name='e_update_card1', blank=True)

    def get_absolute_url(self):
        return reverse('card_app:e-update-card', 
                kwargs={'event_id': self.id})

class EDeleteCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_delete_card0', blank=True)

    label = models.CharField(null=True, blank=False, 
    max_length=626)

    def get_absolute_url(self):
        return reverse('card_app:e-delete-card', 
            kwargs={'event_id': self.id})

class GlobalCardFilter(models.Model):
    pattern      = models.CharField(max_length=255, blank=True, default='', null=True)
    user         = models.ForeignKey('core_app.User', null=True, blank=True)
    organization = models.ForeignKey('core_app.Organization', blank=True,
    null=True)

    user = models.ForeignKey('core_app.User', 
    null=True, blank=True)
    organization = models.ForeignKey('core_app.Organization', 
    null=True, blank=True)

    done = models.BooleanField(blank=True, 
    default=False, help_text='Done cards?.')

    class Meta:
        unique_together = ('user', 'organization', )

class CardFilter(GlobalFilterMixin, models.Model):
    pattern      = models.CharField(max_length=255, blank=True, null=True, default='',
    help_text='Pattern0 + Pattern1 + #Tag0 + #Tag1 ...')
    user         = models.ForeignKey('core_app.User', null=True, blank=True)
    organization = models.ForeignKey('core_app.Organization', blank=True,
    null=True)

    board = models.ForeignKey('board_app.Board', blank=True,
    related_name='card_filter',
    null=True)

    list = models.ForeignKey('list_app.List', blank=True, 
    related_name='card_filter', null=True)

    status = models.BooleanField(blank=True, default=False, 
    help_text='Filter On/Off.')

    done = models.BooleanField(blank=True, 
    default=False, help_text='Done cards?.')

    # It warrants there will exist only one user and organization
    # filter. If we decide to permit more filters..
    class Meta:
        unique_together = ('user', 'organization', 'board', 'list')

class ExternObject(models.Model):
    """
    Cards can be related to any kind of extern objects/events.
    Like github commits or even comments. This model provides
    an abstract approach for providing quick integration with
    other platforms.
    
    """

    card = models.ForeignKey('core_app.User', null=True, 
    blank=True)


class EBindTagCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_bind_tag_card0', blank=True)

    card = models.ForeignKey('Card', 
    related_name='e_bind_tag_card1', blank=True)

    tag = models.ForeignKey('core_app.Tag', 
    related_name='e_bind_tag_card2', blank=True)

    def get_absolute_url(self):
        return reverse('card_app:e-bind-tag-card', 
                    kwargs={'event_id': self.id})


class EUnbindTagCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_unbind_tag_card0', blank=True)

    card = models.ForeignKey('Card', 
    related_name='e_unbind_tag_card1', blank=True)

    tag = models.ForeignKey('core_app.Tag', 
    related_name='e_unbind_tag_card2', blank=True)

    def get_absolute_url(self):
        return reverse('card_app:e-unbind-tag-card', 
                    kwargs={'event_id': self.id})

class ECutCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_cut_card0', blank=True)

    child = models.ForeignKey('Card', 
    related_name='e_cut_card1', blank=True)

    def get_absolute_url(self):
        return reverse('card_app:e-cut-card', 
                    kwargs={'event_id': self.id})

class EArchiveCard(Event):
    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_archive_card0', blank=True)

    child = models.ForeignKey('Card', 
    related_name='e_archive_card1', blank=True)

    def get_absolute_url(self):
        return reverse('card_app:e-archive-card', 
        kwargs={'event_id': self.id})







