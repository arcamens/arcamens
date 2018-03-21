from django.core.urlresolvers import reverse
from django.template.loader import get_template
from core_app.utils import splittokens
from django.db.models import Q
from functools import reduce
from core_app import ws
import operator

class UserMixin(object):
    def ws_alert(self):
        ws.client.publish('user%s' % self.id, 
            'alert-event', 0, False)

    def ws_sound(self):
        ws.client.publish('user%s' % self.id, 
            'sound', 0, False)

    def ws_subscribe_board(self, id):
        ws.client.publish('user%s' % self.id, 
            'subscribe board%s' % id, 0, False)

    def ws_unsubscribe_board(self, id):
        ws.client.publish('user%s' % self.id, 
            'unsubscribe board%s' % id, 0, False)

    def ws_subscribe_timeline(self, id):
        ws.client.publish('user%s' % self.id, 
            'subscribe timeline%s' % id, 0, False)

    def ws_unsubscribe_timeline(self, id):
        ws.client.publish('user%s' % self.id, 
            'unsubscribe timeline%s' % id, 0, False)

    def get_user_url(self):
        return reverse('core_app:user', 
        kwargs={'user_id': self.id})

    @classmethod
    def collect_users(cls, users, pattern):
        chks, tags = splittokens(pattern)

        for ind in tags:
            users = users.filter(Q(tags__name__istartswith=ind))

        users = users.filter(reduce(operator.and_, 
        (Q(name__icontains=ind) | Q(email__icontains=ind) 
        for ind in chks))) if chks else users
        return users

    def __str__(self):
        return self.name

class GlobalFilterMixin:
    pass

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

class OrganizationMixin(object):
    def ws_alert(self):
        ws.client.publish('organization%s' % self.id, 
            'alert-event', 0, False)

    def ws_sound(self):
        ws.client.publish('organization%s' % self.id, 
            'sound', 0, False)

