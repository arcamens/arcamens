from django.utils.translation import ugettext_lazy as _
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

    def get_ancestor_url(self):
        return reverse('board_app:list-boards')

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

    description = models.CharField(null=True, blank=True, default='',
    verbose_name=_("Description"), help_text='Example: Things to do.', max_length=626)

    # members = models.ManyToManyField('core_app.User', 
    # null=True, related_name='boards_member', blank=True, 
    # symmetrical=False)

class ListFilter(models.Model):
    pattern      = models.CharField(max_length=255, blank=True, null=True)
    user         = models.ForeignKey('core_app.User', null=True, blank=True)
    organization = models.ForeignKey('core_app.Organization', blank=True,
    null=True)

    board = models.ForeignKey('board_app.Board', blank=True,
    related_name='list_filter', null=True)

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

    def get_absolute_url(self):
        return reverse('list_app:e-create-list', 
                    kwargs={'event_id': self.id})



