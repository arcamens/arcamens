from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from core_app.models import  User, Organization, Event, Node
from django.core.urlresolvers import reverse
from wsbells.models import QueueWS
from django.db.models import Q
from django.db import models

class PinMixin(object):
    def get_absolute_url(self):
        if self.board:
            return reverse('list_app:list-lists', 
                kwargs={'board_id': self.board.id})
        elif self.card:
            return reverse('card_app:view-data', 
                kwargs={'card_id': self.card.id})
        elif self.timeline:
            return reverse('timeline_app:list-posts', 
                kwargs={'timeline_id': self.timeline.id})
        else:
            return reverse('card_app:list-cards', 
                kwargs={'list_id': self.list.id})

    def get_link_url(self):
        if self.board:
            return reverse('board_app:board-link', 
                kwargs={'board_id': self.board.id})
        elif self.card:
            return reverse('card_app:card-link', 
                kwargs={'card_id': self.card.id})
        elif self.timeline:
            return reverse('timeline_app:list-posts', 
                kwargs={'timeline_id': self.timeline.id})
        else:
            return reverse('list_app:list-link', 
                kwargs={'list_id': self.list.id})

    def get_target_name(self):
        if self.board:
            return self.board.name
        elif self.card:
            return self.card.label
        else:
            return self.list.name

class BoardMixin(QueueWS):
    @classmethod
    def get_user_boards(cls, user):
        boards = user.boards.filter(organization=user.default)
        return boards

    def get_ancestor_url(self):
        return reverse('board_app:list-boards')

    def get_link_url(self):
        return reverse('board_app:board-link', 
                    kwargs={'board_id': self.id})

    def save(self, *args, **kwargs):
        self.node = Node.objects.create()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class EBindBoardUserMixin(object):
    pass

class EUnbindBoardUserMixin(object):
    pass

class EUpdateBoardMixin(object):
    pass

class ECreateBoardMixin(object):
    pass

class Board(BoardMixin, models.Model):
    """    
    """
    organization = models.ForeignKey('core_app.Organization', 
    related_name='boards', null=True, blank=True)

    name = models.CharField(null=True, blank=False,
    verbose_name=_("Name"), help_text='Example: /projects/labor/bugs, \
    Management, Blackdawn Team, ...', max_length=250)

    description = models.CharField(blank=True, default='', 
    verbose_name=_("Description"), help_text='Example: Deals with \
    labor bugs.', max_length=626)

    owner = models.ForeignKey('core_app.User', null=True, 
    blank=True, related_name='owned_boards')

    created  = models.DateTimeField(auto_now_add=True, 
    null=True)

    members = models.ManyToManyField('core_app.User', 
    null=True, related_name='boards', blank=True, 
    symmetrical=False)

    admins = models.ManyToManyField('core_app.User', 
    null=True, related_name='managed_boards', blank=True, 
    symmetrical=False)

    node = models.OneToOneField('core_app.Node', 
    null=True, related_name='board')

    # done = models.BooleanField(blank=True, default=False)

class Pin(PinMixin, models.Model):
    user = models.ForeignKey('core_app.User', null=True, 
    blank=True)

    organization = models.ForeignKey('core_app.Organization', blank=True,
    null=True)

    # I should use concrete inheritance here.
    board = models.ForeignKey('board_app.Board', 
    null=True, blank=True)

    list = models.ForeignKey('list_app.List', 
    null=True, blank=True)

    card = models.ForeignKey('card_app.Card', 
    null=True, blank=True)

    timeline = models.ForeignKey('timeline_app.Timeline', 
    null=True, blank=True)

    class Meta:
        unique_together = (('user', 'organization', 'board'), 
        ('user', 'organization', 'timeline'), ('user', 'organization', 'list'), 
        ('user', 'organization', 'card'))

class EBindBoardUser(Event, EBindBoardUserMixin):
    board = models.ForeignKey('Board', 
    related_name='e_bind_board_user', blank=True)

    peer = models.ForeignKey('core_app.User', null=True, blank=True)
    html_template = 'board_app/e-bind-board-user.html'

class EUnbindBoardUser(Event, EUnbindBoardUserMixin):
    board = models.ForeignKey('Board', 
    related_name='e_unbind_board_user', blank=True)
    peer = models.ForeignKey('core_app.User', null=True, blank=True)
    html_template = 'board_app/e-unbind-board-user.html'

class EUpdateBoard(Event, EUpdateBoardMixin):
    board = models.ForeignKey('Board', 
    related_name='e_update_board', blank=True)
    html_template = 'board_app/e-update-board.html'

class ECreateBoard(Event, ECreateBoardMixin):
    board = models.ForeignKey('Board', 
    related_name='e_create_board', blank=True)
    html_template = 'board_app/e-create-board.html'


class EDeleteBoard(Event):
    board_name = models.CharField(max_length=255, 
    blank=True, null=True)
    html_template = 'board_app/e-delete-board.html'

class EPasteList(Event, ECreateBoardMixin):
    board = models.ForeignKey('Board', 
    related_name='e_paste_list0', blank=True)

    lists = models.ManyToManyField('list_app.List', 
    null=True, related_name='e_paste_list1', blank=True, 
    symmetrical=False)

    html_template = 'board_app/e-paste-list.html'








