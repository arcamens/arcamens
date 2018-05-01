from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from core_app.models import  User, Organization, Event, Node
from board_app.model_mixins import *
from django.db.models import Q
from django.db import models

class Board(BoardMixin, Node):
    """    
    """

    members = models.ManyToManyField('core_app.User', 
    null=True, related_name='boards', blank=True, 
    symmetrical=False)

    admins = models.ManyToManyField('core_app.User', 
    null=True, related_name='managed_boards', blank=True, 
    symmetrical=False)

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







