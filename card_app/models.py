from django.utils.translation import ugettext_lazy as _
from markdown.extensions.tables import TableExtension
from mdx_gfm import GithubFlavoredMarkdownExtension
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.urls import reverse
from core_app.models import Event, User, Organization
from sqlike.parser import SqLike, SqNode
from board_app.models import Board
from core_app.miscutils import disk_cleaner
from django.db.models import Q, F
from django.db import models
from markdown import markdown
from functools import reduce
from operator import and_, or_
from slock.views import RenderExc
# Create your models here.

class CardMixin(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def locate(cls, user, organization, card_id):
        """
        Supposed to retrieve a given card only if the card matches
        the required constraints.
        """

        card = cls.objects.filter(
        Q(ancestor__ancestor__members=user) | Q(workers=user),
        ancestor__ancestor__organization=organization, id=card_id).distinct()
        card = card.first()

        if not card:
            return cls.access_error(card_id)
        return card

    @classmethod
    def access_error(cls, card_id):
        card = cls.objects.get(id=card_id)
        clipboard = card.card_clipboard_users.first()

        if clipboard: 
            raise RenderExc('card_app/card-on-clipboard.html', 
                {'card': card, 'user': clipboard.user} , status=403)

    def save(self, *args, **kwargs):
        self.html = markdown(self.data,
        extensions=[TableExtension(), GithubFlavoredMarkdownExtension()], safe_mode=True,  
        enable_attributes=False)

        # Define the new card with the greatest priority.
        if not self.pk and self.ancestor:
            self.set_priority()
        super(CardMixin, self).save(*args, **kwargs)

    def set_priority(self):
        card = self.ancestor.cards.order_by('-priority').first()
        self.priority = (card.priority + 1) if card else 0
    
    def get_absolute_url(self):
        return reverse('card_app:view-data', 
                    kwargs={'card_id': self.id})

    def get_link_url(self):
        return reverse('card_app:card-link', 
                    kwargs={'card_id': self.id})

    def duplicate(self, list=None):
        card             = Card.objects.get(id=self.id)
        card.pk          = None
        card.ancestor    = list
        card.parent      = None
        card.parent_post = None
        card.save()
        card.path.clear()

        for ind in self.cardfilewrapper_set.all():
            ind.duplicate(card)
        return card

    def __str__(self):
        """
        """
        return self.label

class CardFilterMixin(models.Model):
    class Meta:
        abstract = True

    def from_sqcard(self, cards):
        from card_app.sqlikes import SqCard

        sqlike = SqCard()
        sqlike.feed(self.pattern)

        cards = sqlike.run(cards)
        return cards

class CardSearchMixin(models.Model):
    class Meta:
        abstract = True

    def get_partial(self, cards):
        cards = cards.filter(Q(done=self.done))
        if self.assigned:
            cards = cards.filter(Q(workers__isnull=False))
        if self.assigned_by_me:
            cards = cards.filter(Q(cardtaskship__assigner=self.user))
        if self.assigned_to_me:
            cards = cards.filter(workers=self.user)
        if self.created_by_me:
            cards = cards.filter(owner=self.user)
        return cards

class CardFileWrapperMixin(object):
    def duplicate(self, card=None):
        wrapper       = CardFileWrapper.objects.get(id=self.id)
        wrapper.pk    = None
        wrapper.card  = card
        wrapper.save()
        return wrapper

class CardPinMixin(models.Model):
    def get_absolute_url(self):
        return reverse('card_app:view-data', 
            kwargs={'card_id': self.card.id})

class CardPin(CardPinMixin):
    user = models.ForeignKey('core_app.User', 
    null=True, on_delete=models.CASCADE)

    organization = models.ForeignKey('core_app.Organization', 
    null=True, on_delete=models.CASCADE)

    card = models.ForeignKey('card_app.Card', 
    null=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'organization', 'card')

class CardTagship(models.Model):
    """    
    """
    card = models.ForeignKey('Card', null=True, on_delete=models.CASCADE)
    tag  = models.ForeignKey('core_app.Tag', 
    null=True, related_name='card_tagship', on_delete=models.CASCADE)

    tagger = models.ForeignKey('core_app.User', null=True, 
    related_name='card_taggership', on_delete=models.CASCADE)

    created  = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ('card', 'tag', )

class CardTaskship(models.Model):
    """    
    """
    card   = models.ForeignKey('Card', null=True, on_delete=models.CASCADE)
    worker = models.ForeignKey('core_app.User', 
    null=True, related_name='card_workership', on_delete=models.CASCADE)

    assigner = models.ForeignKey('core_app.User', null=True, 
    related_name='card_assingership', on_delete=models.CASCADE)

    created  = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=626, null=True, blank=True)

    class Meta:
        unique_together = ('card', 'worker', )

class Card(CardMixin):
    """    
    """
    owner = models.ForeignKey('core_app.User', 
    null=True, on_delete=models.CASCADE)

    ancestor = models.ForeignKey('list_app.List', 
    null=True, related_name='cards', on_delete=models.CASCADE)

    created  = models.DateTimeField(auto_now_add=True, null=True)
    deadline = models.DateTimeField(null=True, blank=True)

    expired = models.BooleanField(blank=True, db_index=True, default=False)

    label = models.CharField(null=True, blank=False, 
    verbose_name=_("Label"), help_text='Label, Deadline, ...', 
    max_length=626)

    priority = models.IntegerField(default=0)

    data = models.TextField(blank=True, verbose_name=_("Data"), 
    help_text='Markdown content.', default='')

    workers = models.ManyToManyField('core_app.User', 
    related_name='tasks', through=CardTaskship,
    through_fields=('card', 'worker',), symmetrical=False)

    relations = models.ManyToManyField('Card', related_name='related')

    tags = models.ManyToManyField('core_app.Tag', related_name='cards', 
    symmetrical=False, through=CardTagship,
    through_fields=('card', 'tag'))

    done = models.BooleanField(blank=True, default=False)

    html = models.TextField(null=True, blank=True)

    parent = models.ForeignKey('self', null=True, 
    related_name='forks', on_delete=models.CASCADE)

    parent_post = models.ForeignKey('post_app.Post', null=True, 
    related_name='card_forks', on_delete=models.CASCADE)

    path = models.ManyToManyField('Card', 
    related_name='children', symmetrical=False)

class CardSearch(CardSearchMixin):
    pattern  = models.CharField(max_length=255, blank=True, 
    default='', help_text='tag:issue + owner:iury')

    organization = models.ForeignKey('core_app.Organization', 
    null=False, on_delete=models.CASCADE)

    user = models.ForeignKey('core_app.User',
    null=False, on_delete=models.CASCADE)

    done = models.BooleanField(blank=True, default=False)

    assigned = models.BooleanField(blank=False, default=True)
    assigned_by_me = models.BooleanField(blank=False, default=True)

    assigned_to_me = models.BooleanField(blank=True, default=True)

    created_by_me = models.BooleanField(blank=True, default=False)

    class Meta:
        unique_together = ('user', 'organization', )

class CardClipboard(models.Model):
    user = models.ForeignKey('core_app.User', 
    null=False, on_delete=models.CASCADE)

    card = models.OneToOneField('Card', 
    null=False, on_delete=models.CASCADE, related_name='selected')

class CardFileWrapper(CardFileWrapperMixin, models.Model):
    """
    """
    organization = models.ForeignKey('core_app.Organization', 
    null=False, on_delete=models.CASCADE)

    card = models.ForeignKey('Card', 
    null=True, on_delete=models.CASCADE, blank=True)

    file = models.FileField(
    verbose_name='', help_text='')

class ERelateCard(Event):
    """
    """

    ancestor0 = models.ForeignKey('list_app.List', 
    related_name='e_relate_card0', null=True, on_delete=models.CASCADE)

    ancestor1 = models.ForeignKey('list_app.List', 
    related_name='e_relate_card1', null=True, on_delete=models.CASCADE)

    card0 = models.ForeignKey('Card', 
    related_name='e_relate_card2', null=True, on_delete=models.CASCADE)

    card1 = models.ForeignKey('Card', 
    related_name='e_relate_card3', null=True, on_delete=models.CASCADE)

    # For listing board activity correctly.
    board0 = models.ForeignKey('board_app.Board', 
    default=None, related_name='e_relate_card4', 
    null=True, on_delete=models.CASCADE)

    board1 = models.ForeignKey('board_app.Board', 
    default=None, related_name='e_relate_card5', 
    null=True, on_delete=models.CASCADE)

    html_template = 'card_app/e-relate-card.html'

class EUnrelateCard(Event):
    """
    """

    ancestor0 = models.ForeignKey('list_app.List', 
    related_name='e_unrelate_card0', null=True, on_delete=models.CASCADE)

    ancestor1 = models.ForeignKey('list_app.List', 
    related_name='e_unrelate_card1', null=True, on_delete=models.CASCADE)

    card0 = models.ForeignKey('Card', 
    related_name='e_unrelate_card2', null=True, on_delete=models.CASCADE)

    card1 = models.ForeignKey('Card', 
    related_name='e_unrelate_card3', null=True, on_delete=models.CASCADE)

    # For listing board activity correctly.
    board0 = models.ForeignKey('board_app.Board', 
    default=None, related_name='e_unrelate_card4', 
    null=True, on_delete=models.CASCADE)

    board1 = models.ForeignKey('board_app.Board', 
    default=None, related_name='e_unrelate_card5', 
    null=True, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('card_app:e-unrelate-card', 
                    kwargs={'event_id': self.id})

    html_template = 'card_app/e-unrelate-card.html'

class ECreateCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_create_card0', null=True, on_delete=models.CASCADE)

    card = models.ForeignKey('Card', 
    related_name='e_create_card1', null=True, on_delete=models.CASCADE)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_create_card2', default=None, 
    null=True, on_delete=models.CASCADE)

    html_template = 'card_app/e-create-card.html'

class EBindCardWorker(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_bind_card_worker0', null=True, on_delete=models.CASCADE)

    card = models.ForeignKey('Card', 
    related_name='e_bind_card_worker1', null=True, on_delete=models.CASCADE)

    peer = models.ForeignKey('core_app.User', 
    related_name='e_bind_card_worker2', null=True, on_delete=models.CASCADE)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_bind_card_worker3', default=None, 
    null=True, on_delete=models.CASCADE)

    status = models.CharField(max_length=626, null=True)
    html_template = 'card_app/e-bind-card-worker.html'

class EUnbindCardWorker(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_unbind_card_worker0', null=True, on_delete=models.CASCADE)

    card = models.ForeignKey('Card', 
    related_name='e_unbind_card_worker1', null=True, on_delete=models.CASCADE)

    peer = models.ForeignKey('core_app.User', 
    related_name='e_unbind_card_worker2', null=True, on_delete=models.CASCADE)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_unbind_card_worker3', default=None, 
    null=True, on_delete=models.CASCADE)

    html_template = 'card_app/e-unbind-card-worker.html'

class ECreateFork(Event):
    """
    """

    ancestor0 = models.ForeignKey('list_app.List', 
    related_name='e_create_fork0', null=True, on_delete=models.CASCADE)

    card0 = models.ForeignKey('Card', 
    related_name='e_create_fork1', null=True, on_delete=models.CASCADE)

    card1 = models.ForeignKey('Card', 
    related_name='e_create_fork2', null=True, on_delete=models.CASCADE)

    board0 = models.ForeignKey('board_app.Board', 
    related_name='e_create_fork3', default=None, 
    null=True, on_delete=models.CASCADE)

    board1 = models.ForeignKey('board_app.Board', 
    related_name='e_create_fork4', default=None, 
    null=True, on_delete=models.CASCADE)

    ancestor1 = models.ForeignKey('list_app.List', 
    related_name='e_create_fork5', default=None, 
    null=True, on_delete=models.CASCADE)

    html_template = 'card_app/e-create-fork.html'

class EUpdateCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_update_card0', null=True, on_delete=models.CASCADE)

    card = models.ForeignKey('Card', 
    related_name='e_update_card1', null=True, on_delete=models.CASCADE)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_update_card2', default=None, 
    null=True, on_delete=models.CASCADE)

    card_label = models.CharField(null=True, blank=False, 
    verbose_name=_("Label"), help_text='Label, Deadline, ...', 
    max_length=626)
    card_html = models.TextField(null=True, blank=True)

    card_data = models.TextField(blank=True, verbose_name=_("Data"), 
    help_text='Markdown content.', default='')

    html_template = 'card_app/e-update-card.html'

class ERestoreCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_restore_card0', null=True, on_delete=models.CASCADE)

    card = models.ForeignKey('Card', 
    related_name='e_restore_card1', null=True, on_delete=models.CASCADE)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_restore_card2', default=None, 
    null=True, on_delete=models.CASCADE)

    event_html    = models.TextField(null=True, blank=True)
    html_template = 'card_app/e-restore-card.html'

class EAttachCardFile(Event):
    """
    """

    filewrapper = models.ForeignKey('CardFileWrapper', 
    related_name='e_attach_card_file0', null=True, on_delete=models.CASCADE)

    card = models.ForeignKey('Card', 
    related_name='e_attach_card_file1', null=True, on_delete=models.CASCADE)

    list = models.ForeignKey('list_app.List', 
    related_name='e_attach_card_file2', null=True, on_delete=models.CASCADE)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_attach_card_file3', 
    null=True, on_delete=models.CASCADE)

    html_template = 'card_app/e-attach-card-file.html'

class EDettachCardFile(Event):
    """
    """
    filename = models.CharField(null=True, 
    blank=False, max_length=626)

    card = models.ForeignKey('Card', 
    related_name='e_dettach_card_file1', null=True, on_delete=models.CASCADE)

    list = models.ForeignKey('list_app.List', 
    related_name='e_dettach_card_file2', null=True, on_delete=models.CASCADE)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_dettach_card_file3', 
    null=True, on_delete=models.CASCADE)

    html_template = 'card_app/e-dettach-card-file.html'

class EDeleteCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_delete_card0', null=True, on_delete=models.CASCADE)

    label = models.CharField(null=True, max_length=626)

    board = models.ForeignKey('board_app.Board', null=True, 
    on_delete=models.CASCADE, related_name='e_delete_card1')

    html_template = 'card_app/e-delete-card.html'

class CardFilter(CardFilterMixin, models.Model):
    pattern  = models.CharField(max_length=255,  blank=True, default='', 
    help_text='Example: owner:oliveira  + tag:bug')

    organization = models.ForeignKey('core_app.Organization', 
    null=False, on_delete=models.CASCADE)

    list = models.ForeignKey('list_app.List',
    related_name='card_filter', null=True, on_delete=models.CASCADE)

    status = models.BooleanField(blank=True, 
    default=False, help_text='Filter On/Off.')

    # done = models.BooleanField(blank=True, 
    # default=False, help_text='Done cards?.')

    user = models.ForeignKey('core_app.User', 
    null=False, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'organization', 'list')

class EBindTagCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_bind_tag_card0', null=True, on_delete=models.CASCADE)

    card = models.ForeignKey('Card', 
    related_name='e_bind_tag_card1', null=True, on_delete=models.CASCADE)

    tag = models.ForeignKey('core_app.Tag', 
    related_name='e_bind_tag_card2', null=True, on_delete=models.CASCADE)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_bind_tag_card3', null=True, on_delete=models.CASCADE)

    html_template = 'card_app/e-bind-tag-card.html'

class EUnbindTagCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_unbind_tag_card0', null=True, on_delete=models.CASCADE)

    card = models.ForeignKey('Card', 
    related_name='e_unbind_tag_card1', null=True, on_delete=models.CASCADE)

    tag = models.ForeignKey('core_app.Tag', 
    related_name='e_unbind_tag_card2', null=True, on_delete=models.CASCADE)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_unbind_tag_card3', null=True, on_delete=models.CASCADE)

    html_template = 'card_app/e-unbind-tag-card.html'

class ECutCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_cut_card0', null=True, on_delete=models.CASCADE)

    card = models.ForeignKey('Card', 
    related_name='e_cut_card1', null=True, on_delete=models.CASCADE)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_cut_card2', null=True, on_delete=models.CASCADE)

    html_template = 'card_app/e-cut-card.html'

class ESetCardPriorityUp(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_set_card_priority_up0', null=True, on_delete=models.CASCADE)

    card0 = models.ForeignKey('Card', 
    related_name='e_set_card_priority_up1', null=True, on_delete=models.CASCADE)

    card1 = models.ForeignKey('Card', 
    related_name='e_set_card_priority_up2', null=True, on_delete=models.CASCADE)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_set_card_priority_up3', null=True, on_delete=models.CASCADE)

    html_template = 'card_app/e-set-card-priority-up.html'

class ESetCardPriorityDown(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_set_card_priority_down0', null=True, on_delete=models.CASCADE)

    card0 = models.ForeignKey('Card', 
    related_name='e_set_card_priority_down1', null=True, on_delete=models.CASCADE)

    card1 = models.ForeignKey('Card', 
    related_name='e_set_card_priority_down2', null=True, on_delete=models.CASCADE)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_set_card_priority_down3', null=True, on_delete=models.CASCADE)

    html_template = 'card_app/e-set-card-priority-down.html'

class EArchiveCard(Event):
    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_archive_card0', null=True, on_delete=models.CASCADE)

    cards = models.ManyToManyField('Card', 
    related_name='e_archive_card1')

    board = models.ForeignKey('board_app.Board', 
    related_name='e_archive_card2', null=True, on_delete=models.CASCADE)

    html_template = 'card_app/e-archive-card.html'

class EUnarchiveCard(Event):
    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_unarchive_card0', null=True, on_delete=models.CASCADE)

    card = models.ForeignKey('Card', 
    related_name='e_unarchive_card1', null=True, on_delete=models.CASCADE)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_unarchive_card2', null=True, on_delete=models.CASCADE)

    html_template = 'card_app/e-unarchive-card.html'

class ECopyCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_copy_card0', null=True, on_delete=models.CASCADE)

    card = models.ForeignKey('card', 
    related_name='e_copy_card1', null=True, on_delete=models.CASCADE)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_copy_card2', null=True, on_delete=models.CASCADE)

    html_template = 'card_app/e-copy-card.html'

class ESetCardDeadline(Event):
    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_set_card_deadline0', null=True, on_delete=models.CASCADE)

    card = models.ForeignKey('card', 
    related_name='e_set_card_deadline1', null=True, on_delete=models.CASCADE)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_set_card_deadline2', null=True, on_delete=models.CASCADE)

    html_template = 'card_app/e-set-card-deadline.html'

class EArrivedCardDeadline(Event):
    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_arrived_card_deadline0', null=True, on_delete=models.CASCADE)

    card = models.ForeignKey('card', 
    related_name='e_arrived_card_deadline0', null=True, on_delete=models.CASCADE)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_arrived_card_deadline0', null=True, on_delete=models.CASCADE)

    # It might sound useless and bad, but saving the deadline
    # that was expired on the event it may be useful in the future.
    deadline = models.DateTimeField(null=True, blank=True)

    html_template = 'card_app/e-arrived-card-deadline.html'

@receiver(pre_delete, sender=CardFileWrapper)
def delete_filewrapper(sender, instance, **kwargs):
    is_unique = CardFileWrapper.objects.filter(file=instance.file)
    is_unique = is_unique.count() == 1
    if is_unique: clean_disk(instance)

def clean_disk(record):
    org = Organization.objects.only('owner__c_storage')
    org = org.get(id=record.organization_id)
    org.owner.c_storage = F('c_storage') + record.file.size
    org.owner.save()
    record.file.delete(save=False)























