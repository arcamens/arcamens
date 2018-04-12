from django.core.urlresolvers import reverse
from django.template.loader import get_template
from sqlike.parser import SqLike, SqNode
from django.db.models import Q
from functools import reduce
from wsbells.models import UserWS, QueueWS
import operator

class UserMixin(UserWS):
    def ws_alert(self, target=None):
        target = target if target else self
        self.ws_cmd(target, 'ws-alert-event')

    def ws_sound(self, target=None):
        target = target if target else self
        self.ws_cmd(target, 'ws-sound')

    def connected_queues(self):
        """
        Return all timelines the user should have 
        ws client to be subscribed to.
        """

        qnames = self.ws_queues(self.timelines.all())
        qnames.append(self.default.qname())
        qnames.extend(self.ws_queues(self.boards.all()))
        return qnames

    def get_user_url(self):
        return reverse('core_app:user', 
        kwargs={'user_id': self.id})

    @classmethod
    def from_sqlike(cls):
        email = lambda ind: Q(email__icontains=ind)
        name  = lambda ind: Q(name__icontains=ind)
        desc  = lambda ind: Q(description__icontains=ind)
        tag   = lambda ind: Q(tags__name__icontains=ind)
        default = lambda ind: Q(email__icontains=ind) | Q(name__icontains=ind)
        sqlike = SqLike(SqNode(None, default),
        SqNode(('m', 'email'), email),
        SqNode(('n', 'name'), name), 
        SqNode(('t', 'tag'), tag, chain=True), 
        SqNode(('d', 'description'), desc),)
        return sqlike

    @classmethod
    def collect_users(cls, users, pattern):
        sqlike = cls.from_sqlike()
        sqlike.feed(pattern)
        users = sqlike.run(users)
        return users


    def __str__(self):
        return self.name

class EventMixin:
    def save(self, *args, hcache=True, **kwargs):
        super().save(*args, **kwargs)

        if hcache and self.html_template:
            self.create_html_cache()

    def create_html_cache(self):
        tmp       = get_template(self.html_template)
        self.html = tmp.render({'event': self})
        super().save()

    def seen(self, user):
        """
        """

        self.users.remove(user)
        self.signers.add(user)
        self.save(hcache=False)

class OrganizationMixin(QueueWS):
    def __str__(self):
        return self.name


class InviteMixin:
    def __str__(self):
        return '%s %s %s' % (self.user.name, 
            self.token, self.organization.name)

class TagMixin:
    @classmethod
    def from_sqlike(cls):
        default  = lambda ind: Q(name__icontains=ind) | Q(
        description__icontains=ind)

        sqlike = SqLike(SqNode(None, default))
        return sqlike








