from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from core_app.models import  User, Organization, Event, Node
from django.core.urlresolvers import reverse
from sqlike.parser import SqLike, SqNode
from django.db.models import Q
from django.db import models

class BoardPinMixin(object):
    def get_absolute_url(self):
        return reverse('list_app:list-lists', 
            kwargs={'board_id': self.board.id})

class BoardMixin(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def from_sqlike(cls):
        default = lambda ind: Q(name__icontains=ind) |\
         Q(description__icontains=ind)

        sqlike = SqLike(cls, SqNode(None, default))
        return sqlike

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
        # The node objects should be created just once.
        if not self.pk:
            self.node = Node.objects.create()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def revoke_access(self, admin, user):
        """
        Remove user access and allow admin access. Set ownership
        to admin if the user is the owner of the board.
        """

        self.members.remove(user)
        self.admins.remove(user)

        if self.owner == user: 
            self.set_ownership(admin)

    def set_ownership(self, admin):
        self.members.add(admin)
        self.admins.add(admin)

        self.owner = admin
        self.save()            

class EBindBoardUserMixin(object):
    pass

class EUnbindBoardUserMixin(object):
    pass

class EUpdateBoardMixin(object):
    pass

class ECreateBoardMixin(object):
    pass

class Boardship(models.Model):
    """    
    """
    board = models.ForeignKey('Board', null=True, blank=True)

    member = models.ForeignKey('core_app.User', null=True, 
    related_name='member_boardship', blank=True)

    binder = models.ForeignKey('core_app.User', null=True, 
    related_name='binder_boardship', blank=True)

    created = models.DateTimeField(auto_now_add=True, null=True)
    admin   = models.BooleanField(default=False)

    class Meta:
        unique_together = ('board', 'member', )

class Board(BoardMixin):
    """    
    """
    organization = models.ForeignKey('core_app.Organization', 
    related_name='boards', null=True, blank=True)

    name = models.CharField(null=True, blank=False,
    verbose_name=_("Name"), help_text='Example: Arcamens', max_length=250)

    description = models.CharField(blank=True, default='', 
    verbose_name=_("Description"), help_text='Example: /projectname/', max_length=626)

    owner = models.ForeignKey('core_app.User', null=True, 
    blank=True, related_name='owned_boards')

    created  = models.DateTimeField(auto_now_add=True, 
    null=True)

    open = models.BooleanField(blank=True, default=False,
    help_text='Include all organization members.')

    members = models.ManyToManyField('core_app.User', through=Boardship,
    null=True, related_name='boards', blank=True, symmetrical=False,
    through_fields=('board', 'member'))

    node = models.OneToOneField('core_app.Node', 
    null=False, related_name='board')

    # done = models.BooleanField(blank=True, default=False)

class BoardPin(BoardPinMixin, models.Model):
    user = models.ForeignKey('core_app.User', null=True, blank=True)

    organization = models.ForeignKey('core_app.Organization', 
    blank=True, null=True)

    board = models.ForeignKey('board_app.Board', null=True, blank=True)

    class Meta:
        unique_together = ('user', 'organization', 'board')

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
    board_name = models.CharField(max_length=250, 
    blank=True, null=True)
    html_template = 'board_app/e-delete-board.html'

class EPasteList(Event, ECreateBoardMixin):
    board = models.ForeignKey('Board', 
    related_name='e_paste_list0', blank=True)

    lists = models.ManyToManyField('list_app.List', 
    null=True, related_name='e_paste_list1', blank=True, 
    symmetrical=False)

    html_template = 'board_app/e-paste-list.html'











