from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from core_app.models import  User, Organization, Event
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
        else:
            return reverse('card_app:list-cards', 
                kwargs={'list_id': self.list.id})

    def get_target_name(self):
        if self.board:
            return self.board.name
        elif self.card:
            return self.card.label
        else:
            return self.list.name

class EBindBoardUserMixin(object):
    def get_absolute_url(self):
        return reverse('board_app:e-bind-board-user', 
        kwargs={'event_id': self.id})

class EUnbindBoardUserMixin(object):
    def get_absolute_url(self):
        return reverse('board_app:e-unbind-board-user', 
        kwargs={'event_id': self.id})

class EUpdateBoardMixin(object):
    def get_absolute_url(self):
        return reverse('board_app:e-update-board', 
        kwargs={'event_id': self.id})

class ECreateBoardMixin(object):
    def get_absolute_url(self):
        return reverse('board_app:e-create-board', 
        kwargs={'event_id': self.id})

class BoardMixin:
    @classmethod
    def get_user_boards(cls, user):
        boards = user.boards.all()
        return boards

class Board(BoardMixin, models.Model):
    """    
    """
    name = models.CharField(null=True, blank=False,
    verbose_name=_("Name"), help_text='Example: /projects/labor/bugs, \
    Management, Blackdawn Team, ...', max_length=250)

    description = models.CharField(null=True, blank=True, default='', 
    verbose_name=_("Description"), help_text='Example: Deals with \
    labor bugs.', max_length=626)

    owner = models.ForeignKey('core_app.User', null=True, 
    blank=True)

    created  = models.DateTimeField(auto_now_add=True, 
    null=True)

    members = models.ManyToManyField('core_app.User', 
    null=True, related_name='boards', blank=True, 
    symmetrical=False)
    done = models.BooleanField(blank=True, default=False)

    organization = models.ForeignKey('core_app.Organization', 
    related_name='boards', null=True, blank=True)

    def get_ancestor_url(self):
        return reverse('board_app:list-boards')


class BoardFilter(models.Model):
    pattern      = models.CharField(max_length=255, blank=True, null=True)
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

class OrganizationUserFilter(models.Model):
    pattern      = models.CharField(max_length=255, blank=True, null=True)
    user         = models.ForeignKey('core_app.User', null=True, blank=True)
    organization = models.ForeignKey('core_app.Organization', blank=True,
    null=True)
    status = models.BooleanField(blank=True, default=False, 
    help_text='Filter On/Off.')

    # It warrants there will exist only one user and organization
    # filter. If we decide to permit more filters..
    class Meta:
        unique_together = ('user', 'organization',)

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

    def get_absolute_url(self):
        return reverse('board_app:e-delete-board', 
        kwargs={'event_id': self.id})

class EArchiveBoard(Event):
    ancestor = models.ForeignKey('core_app.Organization', 
    related_name='e_archive_board0', blank=True)

    child = models.ForeignKey('Board', 
    related_name='e_archive_board1', blank=True)

    def get_absolute_url(self):
        return reverse('board_app:e-archive-board', 
        kwargs={'event_id': self.id})




