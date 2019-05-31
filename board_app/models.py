from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from core_app.models import  User, Organization, Event, Node
from django.urls import reverse
from sqlike.parser import SqLike, SqNode
from django.db.models import Q
from django.db import models

class BoardPinMixin(models.Model):
    class Meta:
        abstract = True

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


class Boardship(models.Model):
    """    
    """
    board = models.ForeignKey('Board', null=True, on_delete=models.CASCADE)

    member = models.ForeignKey('core_app.User', null=True, 
    related_name='member_boardship', on_delete=models.CASCADE)

    binder = models.ForeignKey('core_app.User', null=True, 
    related_name='binder_boardship', on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True, null=True)

    CHOICES = (
        ('0', 'Admin'),
        ('1','Member'),
        ('2','Guest'),
    )

    status = models.CharField(max_length=6, 
    choices=CHOICES, default='2')

    class Meta:
        unique_together = ('board', 'member', )

class Board(BoardMixin):
    """    
    """
    organization = models.ForeignKey('core_app.Organization', 
    related_name='boards', null=True, on_delete=models.CASCADE)

    name = models.CharField(null=True, blank=False,
    verbose_name=_("Name"), help_text='Example: Arcamens', max_length=250)

    description = models.CharField(blank=True, default='', 
    verbose_name=_("Description"), help_text='Example: /projectname/', max_length=626)

    owner = models.ForeignKey('core_app.User', null=True, on_delete=models.SET_NULL,
    blank=True, related_name='owned_boards')

    created  = models.DateTimeField(auto_now_add=True, 
    null=True)

    # open = models.BooleanField(blank=True, default=False,
    # help_text='Contributors can also post over.')

    public = models.BooleanField(blank=True, default=False,
    help_text='Visible to all organization members.')

    members = models.ManyToManyField('core_app.User', through=Boardship,
    related_name='boards', blank=True, symmetrical=False,
    through_fields=('board', 'member'))

    node = models.OneToOneField('core_app.Node', 
    null=False, related_name='board', on_delete=models.CASCADE)

    # done = models.BooleanField(blank=True, default=False)

class BoardPin(BoardPinMixin):
    user = models.ForeignKey('core_app.User', 
    null=True, on_delete=models.CASCADE)

    organization = models.ForeignKey('core_app.Organization', 
    blank=True, null=True, on_delete=models.CASCADE)

    board = models.ForeignKey('board_app.Board', 
    null=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'organization', 'board')

class EBindBoardUser(Event):
    board = models.ForeignKey('Board', 
    related_name='e_bind_board_user', null=True, on_delete=models.CASCADE)

    peer = models.ForeignKey('core_app.User', null=True, on_delete=models.CASCADE)

    CHOICES = (
        ('0', 'Admin'),
        ('1','Member'),
        ('2','Guest'),
    )

    status = models.CharField(max_length=6, choices=CHOICES)

    html_template = 'board_app/e-bind-board-user.html'

class EUnbindBoardUser(Event):
    board = models.ForeignKey('Board', 
    related_name='e_unbind_board_user', null=True, on_delete=models.CASCADE)
    peer = models.ForeignKey('core_app.User', null=True, on_delete=models.CASCADE)
    html_template = 'board_app/e-unbind-board-user.html'

class EUpdateBoard(Event):
    board = models.ForeignKey('Board', 
    related_name='e_update_board', null=True, on_delete=models.CASCADE)
    html_template = 'board_app/e-update-board.html'

class ECreateBoard(Event):
    board = models.ForeignKey('Board', 
    related_name='e_create_board', null=True, on_delete=models.CASCADE)
    html_template = 'board_app/e-create-board.html'

class EDeleteBoard(Event):
    board_name = models.CharField(max_length=250)
    html_template = 'board_app/e-delete-board.html'

class EPasteList(Event):
    board = models.ForeignKey('Board', 
    related_name='e_paste_list0', null=True, on_delete=models.CASCADE)

    lists = models.ManyToManyField('list_app.List', 
    related_name='e_paste_list1', blank=True,
    symmetrical=False)

    html_template = 'board_app/e-paste-list.html'


