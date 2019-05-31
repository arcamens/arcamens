from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from core_app.models import  User, Event, Node
from sqlike.parser import SqLike, SqNode
from django.db import models
from django.db.models import Q
import datetime

class GroupMixin(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def from_sqlike(cls):
        owner   = lambda ind: Q(owner__name__icontains=ind) | Q(
        owner__email__icontains=ind)
        name        = lambda ind: Q(name__icontains=ind)
        description = lambda ind: Q(description__icontains=ind)
        default     = lambda ind: Q(name__icontains=ind) \
        | Q(description__icontains=ind)

        sqlike = SqLike(cls, SqNode(None, default),
        SqNode(('o', 'owner'), owner),
        SqNode(('n', 'name'), name),
        SqNode(('d', 'description'), description),)
        return sqlike

    @classmethod
    def get_user_groups(cls, user):
        groups = user.groups.filter(
            organization=user.default)
        return groups

    def get_link_url(self):
        return reverse('group_app:group-link', 
                    kwargs={'group_id': self.id})

    def save(self, *args, **kwargs):
        if not self.pk:
            self.node = Node.objects.create()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def revoke_access(self, admin, user):
        """
        Remove user access and allow admin access.
        """

        self.users.remove(user)
        if self.owner == user: 
            self.set_ownership(admin)

    def set_ownership(self, admin):
        self.users.add(admin)
        self.owner = admin
        self.save()            

class GroupPinMixin(models.Model):
    class Meta:
        abstract = True

    def get_absolute_url(self):
        return reverse('group_app:list-posts', 
            kwargs={'group_id': self.group.id})

class GroupPin(GroupPinMixin):
    user = models.ForeignKey('core_app.User', 
    null=True, on_delete=models.CASCADE)

    organization = models.ForeignKey('core_app.Organization', 
    null=True, on_delete=models.CASCADE)

    group = models.ForeignKey('group_app.Group', 
    null=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'organization', 'group')

class Groupship(models.Model):
    """    
    """
    group = models.ForeignKey('Group', null=True, on_delete=models.CASCADE)

    user = models.ForeignKey('core_app.User', null=True, on_delete=models.CASCADE,
    related_name='user_groupship')

    binder = models.ForeignKey('core_app.User', null=True, on_delete=models.CASCADE,
    related_name='binder_groupship', blank=True)

    created  = models.DateTimeField(auto_now_add=True, null=True)

    CHOICES = (
        ('0', 'Admin'),
        ('1','Member'),
        ('2','Guest'),

    )

    status = models.CharField(max_length=6, 
    choices=CHOICES, default='2')

    class Meta:
        unique_together = ('group', 'user', )

class Group(GroupMixin):
    users = models.ManyToManyField('core_app.User',
    through=Groupship, related_name='groups', blank=True, 
    through_fields=('group', 'user'), symmetrical=False)

    organization = models.ForeignKey('core_app.Organization', 
    related_name='groups', null=False, on_delete=models.CASCADE)

    open = models.BooleanField(blank=True, default=False,
    help_text='Contributors can also post over.')

    public = models.BooleanField(blank=True, default=False,
    help_text='Visible to all organization members.')

    name = models.CharField(null=True, blank=False,
    verbose_name=_("Name"), help_text='Example: Bugs', max_length=250)

    description = models.CharField(blank=True, default='', 
    verbose_name=_("Description"), help_text='Example: /projectname/', 
    max_length=626)

    owner = models.ForeignKey('core_app.User', null=True, 
    on_delete=models.CASCADE, related_name='owned_groups')

    created  = models.DateTimeField(auto_now_add=True, 
    null=True)

    node = models.OneToOneField('core_app.Node', 
    null=False, related_name='group', on_delete=models.CASCADE)

class EDeleteGroup(Event):
    group_name = models.CharField(null=True,
    blank=False, max_length=250)

    html_template = 'group_app/e-delete-group.html'

class ECreateGroup(Event):
    group = models.ForeignKey('Group', 
    related_name='e_create_group', null=True, on_delete=models.CASCADE)
    html_template = 'group_app/e-create-group.html'

class EUpdateGroup(Event):
    group = models.ForeignKey('Group', 
    related_name='e_update_group', null=True, on_delete=models.CASCADE)
    html_template = 'group_app/e-update-group.html'

class EBindGroupUser(Event):
    group = models.ForeignKey('Group', 
    related_name='e_bind_group_user', null=True, on_delete=models.CASCADE)

    peer = models.ForeignKey('core_app.User', null=True, on_delete=models.CASCADE)

    CHOICES = (
        ('0', 'Admin'),
        ('1','Member'),
        ('2','Guest'),
    )

    status = models.CharField(max_length=6, choices=CHOICES)

    html_template = 'group_app/e-bind-group-user.html'

class EUnbindGroupUser(Event):
    group = models.ForeignKey('Group', 
    related_name='e_unbind_group_user', null=True, on_delete=models.CASCADE)

    peer = models.ForeignKey('core_app.User', null=True, on_delete=models.CASCADE)
    html_template = 'group_app/e-unbind-group-user.html'

class EPastePost(Event):
    group = models.ForeignKey('group_app.Group', 
    related_name='e_paste_post0', null=True, on_delete=models.CASCADE)

    posts = models.ManyToManyField('post_app.Post',
    related_name='e_paste_post1', blank=True, symmetrical=False)
    html_template = 'group_app/e-paste-post.html'




