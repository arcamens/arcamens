from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from paybills.models import Service
from core_app.models import  User, Event
import datetime

class EUpdateTimelineMixin(object):
    def get_absolute_url(self):
        return reverse('timeline_app:e-update-timeline', 
        kwargs={'event_id': self.id})

class EDeleteTimelineMixin(object):
    def get_absolute_url(self):
        return reverse('timeline_app:e-delete-timeline', 
        kwargs={'event_id': self.id})

class ECreateTimelineMixin(object):
    def get_absolute_url(self):
        return reverse('timeline_app:e-create-timeline', 
        kwargs={'event_id': self.id})

class EBindTimelineUserMixin(object):
    def get_absolute_url(self):
        return reverse('timeline_app:e-bind-timeline-user', 
        kwargs={'event_id': self.id})

class EUnbindTimelineUserMixin(object):
    def get_absolute_url(self):
        return reverse('timeline_app:e-unbind-timeline-user', 
        kwargs={'event_id': self.id})

class TimelineMixin(object):
    """
    Mixins.
    """

    @classmethod
    def get_user_timelines(cls, user):
        timelines = user.timelines.filter(organization=user.default)
        return timelines

class Timeline(TimelineMixin, models.Model):
    owner = models.ForeignKey('core_app.User', 
    related_name='owned_timelines', null=True)

    organization = models.ForeignKey('core_app.Organization', 
    null=True, related_name='timelines')

    users = models.ManyToManyField('core_app.User', null=True,  
    related_name='timelines', blank=True, symmetrical=False)

    name = models.CharField(null=True,
    blank=False, verbose_name=_("Name"), 
    help_text='Ex: /project/bugs, /project/dev', max_length=50)

    description = models.CharField(null=True, 
    blank=True, verbose_name=_("Description"), 
    help_text='Short Description', 
    max_length=300)

    created = models.DateTimeField(auto_now=True, 
    null=True)

    # The timeline page where it holds more detailed
    # instructions on the objective behind the timelnie.
    # markdown = models.TextField(null=True,
    # blank=False, verbose_name=_("Description"), default='Timeline',
    # help_text='Timeline Description', max_length=190)

class TimelineFilter(models.Model):
    pattern = models.CharField(max_length=255, blank=True, 
    default='')
    user         = models.ForeignKey('core_app.User', null=True, blank=True)
    organization = models.ForeignKey('core_app.Organization', blank=True,
    null=True)
    status = models.BooleanField(blank=True, default=False, 
    help_text='Filter On/Off.')

    # It warrants there will exist only one user and organization
    # filter. If we decide to permit more filters..
    class Meta:
        unique_together = ('user', 'organization',)

class EDeleteTimeline(Event, EDeleteTimelineMixin):
    timeline_name = models.CharField(null=True,
    blank=False, max_length=50)

class ECreateTimeline(Event, ECreateTimelineMixin):
    timeline = models.ForeignKey('Timeline', 
    related_name='e_create_timeline', blank=True)

class EUpdateTimeline(Event, EUpdateTimelineMixin):
    timeline = models.ForeignKey('Timeline', 
    related_name='e_update_timeline', blank=True)

class EBindTimelineUser(Event, EBindTimelineUserMixin):
    timeline = models.ForeignKey('Timeline', 
    related_name='e_bind_timeline_user', blank=True)

    peer = models.ForeignKey('core_app.User', null=True, blank=True)

class EUnbindTimelineUser(Event, EUnbindTimelineUserMixin):
    timeline = models.ForeignKey('Timeline', 
    related_name='e_unbind_timeline_user', blank=True)

    peer = models.ForeignKey('core_app.User', null=True, blank=True)

class EPastePost(Event):
    timeline = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_create_post0', blank=True)

    posts = models.ManyToManyField('post_app.Post', null=True,  
    related_name='e_create_post1', blank=True, symmetrical=False)











