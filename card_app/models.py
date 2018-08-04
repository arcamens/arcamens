from django.utils.translation import ugettext_lazy as _
from markdown.extensions.tables import TableExtension
from mdx_gfm import GithubFlavoredMarkdownExtension
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.urlresolvers import reverse
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

    @classmethod
    def get_allowed_cards(cls, user):
        """
        The user has access to all cards that he is a member
        of its board or an work of the card.
        """

        # boards = Board.get_user_boards(user)
        # cards  = Card.objects.none()
        # for indi in boards:
            # for indj in indi.lists.all():
                # cards = cards | indj.cards.all()

        cards = Card.objects.filter(Q(ancestor__ancestor__organization=user.default) &
            (Q(ancestor__ancestor__members=user) | Q(workers=user))).distinct()
        return cards

    @classmethod
    def from_sqlike(cls):
        owner   = lambda ind: Q(owner__name__icontains=ind) | Q(
        owner__email__icontains=ind)
        not_owner = lambda ind: ~owner(ind)

        worker  = lambda ind: Q(workers__name__icontains=ind) | Q(    
        workers__email__icontains=ind)
        not_worker = lambda ind: ~worker(ind)

        file     = lambda ind: Q(cardfilewrapper__file__icontains=ind)

        created_gt = lambda ind: Q(created__gt=ind)
        created_lt = lambda ind: Q(created__lt=ind)
        created = lambda ind: Q(created__date=ind)

        label   = lambda ind: Q(label__icontains=ind)
        not_label = lambda ind: ~label(ind)

        deadline_gt = lambda ind: Q(deadline__gt=ind)
        deadline_lt = lambda ind: Q(deadline__lt=ind)

        data    = lambda ind: Q(data__icontains=ind)
        not_data    = lambda ind: ~data(ind)

        note  = lambda ind: Q(notes__data__icontains=ind)
        not_note  = lambda ind: ~note(ind)

        tag   = lambda ind: Q(tags__name__icontains=ind)
        not_tag   = lambda ind: ~tag(ind)

        list  = lambda ind: Q(ancestor__name__icontains=ind)
        not_list = lambda ind: ~list(ind)

        board = lambda ind: Q(ancestor__ancestor__name__icontains=ind)
        not_board = lambda ind: ~board(ind)

        note_owner  = lambda ind: Q(notes__owner__name__icontains=ind) |\
        Q(notes__owner__email__icontains=ind)

        not_note_owner = lambda ind: ~note_owner(ind)

        note_file  = lambda ind: Q(notes__notefilewrapper__file__icontains=ind)

        fork   = lambda ind: Q(children__label__icontains=ind)|\
        Q(children__data__icontains=ind)
        not_fork = lambda ind: ~fork(ind)

        fork_label = lambda ind: Q(children__label__icontains=ind)
        not_fork_label = lambda ind: ~fork_label(ind)

        fork_data  = lambda ind: Q(children__data__icontains=ind)
        not_fork_data  = lambda ind: ~fork_data(ind)

        fork_tag   = lambda ind: Q(children__tags__name__icontains=ind)
        not_fork_tag   = lambda ind: ~fork_tag(ind)

        fork_worker   = lambda ind: Q(children__workers__name__icontains=ind)|\
        Q(children__workers__email__icontains=ind)

        not_fork_worker   = lambda ind: ~fork_worker(ind)

        parent   = lambda ind: Q(path__label__icontains=ind)|\
        Q(path__data__icontains=ind)

        parent_label = lambda ind: Q(path__label__icontains=ind)
        not_parent_label = lambda ind: ~parent_label(ind)

        parent_data  = lambda ind: Q(path__data__icontains=ind)
        not_parent_data  = lambda ind: ~parent_data(ind)

        parent_tag   = lambda ind: Q(path__tags__name__icontains=ind)
        not_parent_tag   = lambda ind: ~parent_tag(ind)

        parent_worker   = lambda ind: Q(path__workers__name__icontains=ind)|\
        Q(path__workers__email__icontains=ind)

        not_parent_worker   = lambda ind: ~parent_worker(ind)

        default = lambda ind: Q(label__icontains=ind) | Q(data__icontains=ind) 

        sqlike = SqLike(cls, SqNode(None, default),
        SqNode(('o', 'owner'), owner),
        SqNode(('!o', '!owner'), not_owner),

        SqNode(('w', 'worker'), worker, chain=True), 
        SqNode(('!w', '!worker'), not_worker, chain=True), 

        SqNode(('f', 'file'), file, chain=True),
        SqNode(('c>', 'created>'), created_gt),
        SqNode(('c<', 'created<'), created_lt),
        SqNode(('c', 'created'), created),

        SqNode(('l', 'label'), label),
        SqNode(('!l', '!label'), not_label),
        SqNode(('dl>', '>deadline'), deadline_gt),
        SqNode(('dl<', '<deadline'), deadline_lt),

        SqNode(('d', 'data'), data),
        SqNode(('!d', '!data'), not_data),

        SqNode(('n', 'note'), note, chain=True),
        SqNode(('!n', '!note'), not_note),

        SqNode(('t', 'tag'), tag, chain=True),
        SqNode(('!t', '!tag'), not_tag, chain=True),

        SqNode(('i', 'list'), list),
        SqNode(('!i', '!list'), not_list),

        SqNode(('no', 'note.owner'), note_owner, chain=True),
        SqNode(('!no', '!note.owner'), not_note_owner, chain=True),
        SqNode(('k', 'fork'), fork),
        SqNode(('!k', '!fork'), not_fork),

        SqNode(('kl', 'fork.label'), fork_label),
        SqNode(('!kl', '!fork.label'), not_fork_label),

        SqNode(('kd', 'fork.data'), fork_data),
        SqNode(('!kd', '!fork.data'), not_fork_data),

        SqNode(('kt', 'fork.tag'), fork_tag, chain=True),
        SqNode(('!kt', '!fork.tag'), not_fork_tag, chain=True),

        SqNode(('kw', 'fork.worker'), fork_worker, chain=True),
        SqNode(('!kw', '!fork.worker'), not_fork_worker, chain=True),

        SqNode(('p', 'parent'), parent),

        SqNode(('pl', 'parent.label'), parent_label),
        SqNode(('!pl', '!parent.label'), not_parent_label),

        SqNode(('pd', 'parent.data'), parent_data),
        SqNode(('!pd', '!parent.data'), not_parent_data),

        SqNode(('pt', 'parent.tag'), parent_tag, chain=True),
        SqNode(('!pt', '!parent.tag'), not_parent_tag, chain=True),

        SqNode(('pw', 'parent.worker'), parent_worker, chain=True),
        SqNode(('!pw', '!parent.worker'), not_parent_worker, chain=True),

        SqNode(('nf', 'note.file'), note_file, chain=True),
        SqNode(('b', 'board'), board),
        SqNode(('!b', '!board'), not_board),)

        return sqlike

    def __str__(self):
        """
        """
        return self.label

class CardFilterMixin(models.Model):
    class Meta:
        abstract = True

    def collect(self, cards):
        cards = cards.filter(done=False)

        if not self.status: 
            return cards

        sqlike = Card.from_sqlike()
        sqlike.feed(self.pattern)

        cards = sqlike.run(cards)
        return cards

class GlobalCardFilterMixin(models.Model):
    class Meta:
        abstract = True

    def get_partial(self, cards):
        cards = cards.filter(Q(done=self.done))
        if self.assigned:
            cards = cards.filter(Q(workers__isnull=False))
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
    user = models.ForeignKey('core_app.User', null=True, blank=True)

    organization = models.ForeignKey('core_app.Organization', 
    blank=True, null=True)

    card = models.ForeignKey('card_app.Card', null=True, blank=True)

    class Meta:
        unique_together = ('user', 'organization', 'card')

class CardTagship(models.Model):
    """    
    """
    card = models.ForeignKey('Card', null=True, blank=True)
    tag = models.ForeignKey('core_app.Tag', null=True, blank=True)

    tagger = models.ForeignKey('core_app.User', null=True, 
    related_name='card_taggership', blank=True)

    created  = models.DateTimeField(auto_now_add=True, null=True)

class CardTaskship(models.Model):
    """    
    """
    card = models.ForeignKey('Card', null=True, blank=True)
    worker = models.ForeignKey('core_app.User', null=True, 
    related_name='card_workership', blank=True)

    assigner = models.ForeignKey('core_app.User', null=True, 
    related_name='card_assingership', blank=True)

    created  = models.DateTimeField(auto_now_add=True, null=True)

class Card(CardMixin):
    """    
    """
    owner = models.ForeignKey('core_app.User', null=True, 
    blank=True)

    ancestor = models.ForeignKey('list_app.List', 
    null=True, related_name='cards', blank=True)

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
    null=True, related_name='tasks', blank=True, through=CardTaskship, 
    through_fields=('card', 'worker',), symmetrical=False)

    relations = models.ManyToManyField('Card', 
    null=True, related_name='related', blank=True)

    tags = models.ManyToManyField('core_app.Tag', related_name='cards', 
    null=True, blank=True, symmetrical=False, through=CardTagship,
    through_fields=('card', 'tag'))

    done = models.BooleanField(blank=True, default=False)

    html = models.TextField(null=True, blank=True)

    parent = models.ForeignKey('self', null=True, related_name='forks',
    blank=True)

    parent_post = models.ForeignKey('post_app.Post', null=True, 
    related_name='card_forks', blank=True)

    path = models.ManyToManyField('Card', 
    null=True, related_name='children', blank=True, 
    symmetrical=False)

class GlobalCardFilter(GlobalCardFilterMixin):
    pattern  = models.CharField(max_length=255, blank=True, 
    default='', help_text='tag:issue + owner:iury')

    organization = models.ForeignKey('core_app.Organization', 
    blank=True, null=True)

    user = models.ForeignKey('core_app.User', null=True, 
    blank=True)

    done = models.BooleanField(blank=True, 
    default=False, help_text='Done cards?.')

    assigned = models.BooleanField(blank=False, 
    default=True, help_text='Only tasks.')

    assigned_to_me = models.BooleanField(blank=True, 
    default=True, help_text='Only your tasks.')

    created_by_me = models.BooleanField(blank=True, 
    default=False, help_text='Only cards you created.')

    class Meta:
        unique_together = ('user', 'organization', )

class CardClipboard(models.Model):
    user = models.ForeignKey('core_app.User', null=True, 
    blank=True)

    card = models.OneToOneField('Card', null=True, 
    related_name='selected', blank=True)

class CardFileWrapper(CardFileWrapperMixin, models.Model):
    """
    """
    organization = models.ForeignKey('core_app.Organization', 
    null=True, blank=True)

    card = models.ForeignKey('Card', null=True, 
    on_delete=models.CASCADE, blank=True)

    file = models.FileField(
    verbose_name='', help_text='')

class ERelateCard(Event):
    """
    """

    ancestor0 = models.ForeignKey('list_app.List', 
    related_name='e_relate_card0', blank=True)

    ancestor1 = models.ForeignKey('list_app.List', 
    related_name='e_relate_card1', blank=True)

    card0 = models.ForeignKey('Card', 
    related_name='e_relate_card2', blank=True)

    card1 = models.ForeignKey('Card', 
    related_name='e_relate_card3', blank=True)

    # For listing board activity correctly.
    board0 = models.ForeignKey('board_app.Board', 
    default=None, related_name='e_relate_card4', 
    blank=True)

    board1 = models.ForeignKey('board_app.Board', 
    default=None, related_name='e_relate_card5', 
    blank=True)

    html_template = 'card_app/e-relate-card.html'

class EUnrelateCard(Event):
    """
    """

    ancestor0 = models.ForeignKey('list_app.List', 
    related_name='e_unrelate_card0', blank=True)

    ancestor1 = models.ForeignKey('list_app.List', 
    related_name='e_unrelate_card1', blank=True)

    card0 = models.ForeignKey('Card', 
    related_name='e_unrelate_card2', blank=True)

    card1 = models.ForeignKey('Card', 
    related_name='e_unrelate_card3', blank=True)

    # For listing board activity correctly.
    board0 = models.ForeignKey('board_app.Board', 
    default=None, related_name='e_unrelate_card4', 
    blank=True)

    board1 = models.ForeignKey('board_app.Board', 
    default=None, related_name='e_unrelate_card5', 
    blank=True)

    def get_absolute_url(self):
        return reverse('card_app:e-unrelate-card', 
                    kwargs={'event_id': self.id})

    html_template = 'card_app/e-unrelate-card.html'

class ECreateCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_create_card0', blank=True)

    card = models.ForeignKey('Card', 
    related_name='e_create_card1', blank=True)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_create_card2', default=None, 
    blank=True)

    html_template = 'card_app/e-create-card.html'

class EBindCardWorker(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_bind_card_worker0', blank=True)

    card = models.ForeignKey('Card', 
    related_name='e_bind_card_worker1', blank=True)

    peer = models.ForeignKey('core_app.User', 
    related_name='e_bind_card_worker2', blank=True)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_bind_card_worker3', default=None, 
    blank=True)

    html_template = 'card_app/e-bind-card-worker.html'

class EUnbindCardWorker(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_unbind_card_worker0', blank=True)

    card = models.ForeignKey('Card', 
    related_name='e_unbind_card_worker1', blank=True)

    peer = models.ForeignKey('core_app.User', 
    related_name='e_unbind_card_worker2', blank=True)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_unbind_card_worker3', default=None, 
    blank=True)

    html_template = 'card_app/e-unbind-card-worker.html'

class ECreateFork(Event):
    """
    """

    ancestor0 = models.ForeignKey('list_app.List', 
    related_name='e_create_fork0', blank=True)

    card0 = models.ForeignKey('Card', 
    related_name='e_create_fork1', blank=True)

    card1 = models.ForeignKey('Card', 
    related_name='e_create_fork2', blank=True)

    board0 = models.ForeignKey('board_app.Board', 
    related_name='e_create_fork3', default=None, 
    blank=True)

    board1 = models.ForeignKey('board_app.Board', 
    related_name='e_create_fork4', default=None, 
    blank=True)

    ancestor1 = models.ForeignKey('list_app.List', 
    related_name='e_create_fork5', default=None, 
    blank=True)

    html_template = 'card_app/e-create-fork.html'

class EUpdateCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_update_card0', blank=True)

    card = models.ForeignKey('Card', 
    related_name='e_update_card1', blank=True)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_update_card2', default=None, 
    blank=True)

    html_template = 'card_app/e-update-card.html'

class EAttachCardFile(Event):
    """
    """

    filewrapper = models.ForeignKey('CardFileWrapper', 
    related_name='e_attach_card_file0', blank=True)

    card = models.ForeignKey('Card', 
    related_name='e_attach_card_file1', blank=True)

    list = models.ForeignKey('list_app.List', 
    related_name='e_attach_card_file2', blank=True)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_attach_card_file3', 
    blank=True)

    html_template = 'card_app/e-attach-card-file.html'

class EDettachCardFile(Event):
    """
    """
    filename = models.CharField(null=True, blank=False, 
    max_length=626)

    card = models.ForeignKey('Card', 
    related_name='e_dettach_card_file1', blank=True)

    list = models.ForeignKey('list_app.List', 
    related_name='e_dettach_card_file2', blank=True)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_dettach_card_file3', 
    blank=True)

    html_template = 'card_app/e-dettach-card-file.html'

class EDeleteCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_delete_card0', blank=True)

    label = models.CharField(null=True, blank=False, 
    max_length=626)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_delete_card1', blank=True)

    html_template = 'card_app/e-delete-card.html'

class CardFilter(CardFilterMixin, models.Model):
    pattern  = models.CharField(
    max_length=255,  blank=True, default='', 
    help_text='Example: owner:oliveira  + tag:bug')

    organization = models.ForeignKey('core_app.Organization', 
    blank=True, null=True)

    board = models.ForeignKey('board_app.Board', blank=True,
    related_name='card_filter',
    null=True)

    list = models.ForeignKey('list_app.List', blank=True, 
    related_name='card_filter', null=True)

    status = models.BooleanField(blank=True, default=False, 
    help_text='Filter On/Off.')

    # done = models.BooleanField(blank=True, 
    # default=False, help_text='Done cards?.')

    user = models.ForeignKey('core_app.User', 
    null=True, blank=True)

    # It warrants there will exist only one user and organization
    # filter. If we decide to permit more filters..
    class Meta:
        unique_together = ('user', 'organization', 'board', 'list')

class EBindTagCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_bind_tag_card0', blank=True)

    card = models.ForeignKey('Card', 
    related_name='e_bind_tag_card1', blank=True)

    tag = models.ForeignKey('core_app.Tag', 
    related_name='e_bind_tag_card2', blank=True)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_bind_tag_card3', blank=True)

    html_template = 'card_app/e-bind-tag-card.html'

class EUnbindTagCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_unbind_tag_card0', blank=True)

    card = models.ForeignKey('Card', 
    related_name='e_unbind_tag_card1', blank=True)

    tag = models.ForeignKey('core_app.Tag', 
    related_name='e_unbind_tag_card2', blank=True)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_unbind_tag_card3', blank=True)

    html_template = 'card_app/e-unbind-tag-card.html'

class ECutCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_cut_card0', blank=True)

    card = models.ForeignKey('Card', 
    related_name='e_cut_card1', blank=True)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_cut_card2', blank=True)

    html_template = 'card_app/e-cut-card.html'

class ESetCardPriorityUp(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_set_card_priority_up0', blank=True)

    card0 = models.ForeignKey('Card', 
    related_name='e_set_card_priority_up1', blank=True)

    card1 = models.ForeignKey('Card', 
    related_name='e_set_card_priority_up2', blank=True)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_set_card_priority_up3', blank=True)

    html_template = 'card_app/e-set-card-priority-up.html'

class ESetCardPriorityDown(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_set_card_priority_down0', blank=True)

    card0 = models.ForeignKey('Card', 
    related_name='e_set_card_priority_down1', blank=True)

    card1 = models.ForeignKey('Card', 
    related_name='e_set_card_priority_down2', blank=True)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_set_card_priority_down3', blank=True)

    html_template = 'card_app/e-set-card-priority-down.html'

class EArchiveCard(Event):
    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_archive_card0', blank=True)

    cards = models.ManyToManyField('Card', 
    related_name='e_archive_card1', blank=True)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_archive_card2', blank=True)

    html_template = 'card_app/e-archive-card.html'

class EUnarchiveCard(Event):
    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_unarchive_card0', blank=True)

    card = models.ForeignKey('Card', 
    related_name='e_unarchive_card1', blank=True)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_unarchive_card2', blank=True)

    html_template = 'card_app/e-unarchive-card.html'

class ECopyCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_copy_card0', blank=True)

    card = models.ForeignKey('card', 
    related_name='e_copy_card1', blank=True)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_copy_card2', blank=True)

    html_template = 'card_app/e-copy-card.html'

class ESetCardDeadline(Event):
    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_set_card_deadline0', blank=True)

    card = models.ForeignKey('card', 
    related_name='e_set_card_deadline1', blank=True)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_set_card_deadline2', blank=True)

    html_template = 'card_app/e-set-card-deadline.html'

class EArrivedCardDeadline(Event):
    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_arrived_card_deadline0', blank=True)

    card = models.ForeignKey('card', 
    related_name='e_arrived_card_deadline0', blank=True)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_arrived_card_deadline0', blank=True)

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










