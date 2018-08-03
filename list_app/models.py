from django.utils.translation import ugettext_lazy as _
from sqlike.parser import SqLike, SqNode
from django.core.urlresolvers import reverse
from board_app.models import Event, User
from django.db.models import Q
from django.db import models

class ListMixin(object):
    def duplicate(self, board=None):
        list          = List.objects.get(id=self.id)
        list.pk       = None
        list.ancestor = board
        list.save()

        for ind in self.cards.all():
            ind.duplicate(list)
        return list

    @classmethod
    def from_sqlike(cls):
        owner   = lambda ind: Q(owner__name__icontains=ind) | Q(
        owner__email__icontains=ind)
        name        = lambda ind: Q(name__icontains=ind)
        description = lambda ind: Q(description__icontains=ind)
        board       = lambda ind: Q(ancestor__name__icontains=ind) | Q(
        ancestor__description__icontains=ind)

        default = lambda ind: Q(name__icontains=ind) | Q(ancestor__name__icontains=ind)

        sqlike = SqLike(cls, SqNode(None, default),
        SqNode(('o', 'owner'), owner),
        SqNode(('n', 'name'), name),
        SqNode(('d', 'description'), description),
        SqNode(('b', 'board'), board),)
        return sqlike

    def get_ancestor_url(self):
        return reverse('board_app:list-boards')

    def get_link_url(self):
        return reverse('list_app:list-link', 
                    kwargs={'list_id': self.id})

class ListPinMixin(object):
    def get_absolute_url(self):
        return reverse('card_app:list-cards', 
            kwargs={'list_id': self.list.id})

class ListPin(ListPinMixin, models.Model):
    user = models.ForeignKey('core_app.User', null=True, blank=True)

    organization = models.ForeignKey('core_app.Organization', 
    blank=True, null=True)

    list = models.ForeignKey('list_app.List', null=True, blank=True)

    class Meta:
        unique_together = ('user', 'organization', 'list')

class List(ListMixin, models.Model):
    """    
    """
    name = models.CharField(null=True, blank=False,
    verbose_name=_("Name"), help_text='', max_length=250)

    owner = models.ForeignKey('core_app.User', null=True, 
    blank=True)

    created  = models.DateTimeField(auto_now_add=True, 
    null=True)

    ancestor = models.ForeignKey('board_app.Board', null=True, 
    related_name='lists', blank=True)

    description = models.CharField(blank=True, default='',
    verbose_name=_("Description"), help_text='Example: Things to do.', max_length=626)

    # done = models.BooleanField(blank=True, default=False)

    # members = models.ManyToManyField('core_app.User', 
    # null=True, related_name='boards_member', blank=True, 
    # symmetrical=False)

class ListFilter(models.Model):
    pattern      = models.CharField(max_length=255, blank=True, 
    default='')
    user         = models.ForeignKey('core_app.User', null=True, blank=True)
    organization = models.ForeignKey('core_app.Organization', blank=True,
    null=True)

    board = models.ForeignKey('board_app.Board', blank=True,
    related_name='list_filter', null=True)

    # done = models.BooleanField(blank=True, default=False)

    status = models.BooleanField(blank=True, default=False, 
    help_text='Filter On/Off.')

    # It warrants there will exist only one user and organization
    # filter. If we decide to permit more filters..
    class Meta:
        unique_together = ('user', 'organization', 'board')


class ECreateList(Event):
    """
    """

    ancestor = models.ForeignKey('board_app.Board', 
    related_name='e_create_list0', blank=True)

    child = models.ForeignKey('List', 
    related_name='e_create_list1', blank=True)
    html_template = 'list_app/e-create-list.html'

class EUpdateList(Event):
    """
    """

    ancestor = models.ForeignKey('board_app.Board', 
    related_name='e_update_list0', blank=True)

    child = models.ForeignKey('List', 
    related_name='e_update_list1', blank=True)
    html_template = 'list_app/e-update-list.html'

class EDeleteList(Event):
    ancestor = models.ForeignKey('board_app.Board', 
    related_name='e_delete_list0', blank=True)

    child_name = models.CharField(max_length=255, blank=True, null=True)
    html_template = 'list_app/e-delete-list.html'

class ECutList(Event):
    """
    """

    ancestor = models.ForeignKey('board_app.Board', 
    related_name='e_cut_list0', blank=True)

    child = models.ForeignKey('List', 
    related_name='e_cut_list1', blank=True)

    html_template = 'list_app/e-cut-list.html'

class ECopyList(Event):
    """
    """

    ancestor = models.ForeignKey('board_app.Board', 
    related_name='e_copy_list0', blank=True)

    child = models.ForeignKey('List', 
    related_name='e_copy_list1', blank=True)

    html_template = 'list_app/e-copy-list.html'

class EPasteCard(Event):
    """
    """

    ancestor = models.ForeignKey('list_app.List', 
    related_name='e_paste_card0', blank=True)

    cards = models.ManyToManyField('card_app.Card', 
    null=True, related_name='e_paste_card1', blank=True, 
    symmetrical=False)

    html_template = 'list_app/e-paste-card.html'










