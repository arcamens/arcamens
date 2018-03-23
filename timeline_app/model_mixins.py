from django.core.urlresolvers import reverse
from core_app import ws

class TimelineMixin(object):
    """
    Mixins.
    """
    def ws_alert(self):
        ws.client.publish('timeline%s' % self.id, 
            'alert-event', 0, False)

    def ws_sound(self):
        ws.client.publish('timeline%s' % self.id, 
            'sound', 0, False)

    @classmethod
    def get_user_timelines(cls, user):
        timelines = user.timelines.filter(
            organization=user.default)
        return timelines

    def get_link_url(self):
        return reverse('timeline_app:timeline-link', 
                    kwargs={'timeline_id': self.id})

class EUpdateTimelineMixin(object):
    pass

class EDeleteTimelineMixin(object):
    pass

class EUnbindTimelineUserMixin(object):
    pass

class ECreateTimelineMixin(object):
    pass

class EBindTimelineUserMixin(object):
    pass





