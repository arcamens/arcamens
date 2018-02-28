from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from core_app.models import  User, Organization, Event
from board_app.model_mixins import *
from django.db.models import Q
from django.db import models

class Board(BoardMixin, models.Model):
    """    
    """
    name = models.CharField(null=True, blank=False,
    verbose_name=_("Name"), help_text='Example: /projects/labor/bugs, \
    Management, Blackdawn Team, ...', max_length=250)

    description = models.CharField(blank=True, default='', 
    verbose_name=_("Description"), help_text='Example: Deals with \
    labor bugs.', max_length=626)

    owner = models.ForeignKey('core_app.User', null=True, 
    blank=True)

    created  = models.DateTimeField(auto_now_add=True, 
    null=True)

    members = models.ManyToManyField('core_app.User', 
    null=True, related_name='boards', blank=True, 
    symmetrical=False)

    # done = models.BooleanField(blank=True, default=False)

    organization = models.ForeignKey('core_app.Organization', 
    related_name='boards', null=True, blank=True)

class BoardFilter(models.Model):
    pattern = models.CharField(max_length=255, blank=True, 
    default='')

    user         = models.ForeignKey('core_app.User', null=True, blank=True)
    organization = models.ForeignKey('core_app.Organization', blank=True,
    null=True)
    status = models.BooleanField(blank=True, default=False, 
    help_text='Filter On/Off.')
    done = models.BooleanField(blank=True, default=False,
    help_text='Include archived boards.')

    # It warrants there will exist only one user and organization
    # filter. If we decide to permit more filters..
    class Meta:
        unique_together = ('user', 'organization',)

class Pin(PinMixin, models.Model):
    user = models.ForeignKey('core_app.User', null=True, 
    blank=True)

    organization = models.ForeignKey('core_app.Organization', blank=True,
    null=True)

    # I should use concrete inheritance here.
    board = models.ForeignKey('board_app.Board', 
    unique=True, null=True, blank=True)

    list = models.ForeignKey('list_app.List', 
    unique=True, null=True, blank=True)

    card = models.ForeignKey('card_app.Card', 
    unique=True, null=True, blank=True)

class EBindBoardUser(Event, EBindBoardUserMixin):
    board = models.ForeignKey('Board', 
    related_name='e_bind_board_user', blank=True)

    peer = models.ForeignKey('core_app.User', null=True, blank=True)

class EUnbindBoardUser(Event, EUnbindBoardUserMixin):
    board = models.ForeignKey('Board', 
    related_name='e_unbind_board_user', blank=True)
    peer = models.ForeignKey('core_app.User', null=True, blank=True)

class EUpdateBoard(Event, EUpdateBoardMixin):
    board = models.ForeignKey('Board', 
    related_name='e_update_board', blank=True)

class ECreateBoard(Event, ECreateBoardMixin):
    board = models.ForeignKey('Board', 
    related_name='e_create_board', blank=True)


class EDeleteBoard(Event):
    board_name = models.CharField(max_length=255, 
    blank=True, null=True)

class EArchiveBoard(Event):
    ancestor = models.ForeignKey('core_app.Organization', 
    related_name='e_archive_board0', blank=True)

    child = models.ForeignKey('Board', 
    related_name='e_archive_board1', blank=True)

class EPasteList(Event, ECreateBoardMixin):
    board = models.ForeignKey('Board', 
    related_name='e_paste_list0', blank=True)

    lists = models.ManyToManyField('list_app.List', 
    null=True, related_name='e_paste_list1', blank=True, 
    symmetrical=False)









