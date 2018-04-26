from django.utils.translation import ugettext_lazy as _
from core_app.models import  User, Event
from timeline_app.model_mixins import *
from django.db import models
from django.db.models import Q
import datetime

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

    description = models.CharField(blank=True, 
    verbose_name=_("Description"), help_text='Short Description', 
    default='', max_length=300)

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

    html_template = 'timeline_app/e-delete-timeline.html'

class ECreateTimeline(Event, ECreateTimelineMixin):
    timeline = models.ForeignKey('Timeline', 
    related_name='e_create_timeline', blank=True)
    html_template = 'timeline_app/e-create-timeline.html'

class EUpdateTimeline(Event, EUpdateTimelineMixin):
    timeline = models.ForeignKey('Timeline', 
    related_name='e_update_timeline', blank=True)
    html_template = 'timeline_app/e-update-timeline.html'

class EBindTimelineUser(Event, EBindTimelineUserMixin):
    timeline = models.ForeignKey('Timeline', 
    related_name='e_bind_timeline_user', blank=True)

    peer = models.ForeignKey('core_app.User', null=True, blank=True)
    html_template = 'timeline_app/e-bind-timeline-user.html'

class EUnbindTimelineUser(Event, EUnbindTimelineUserMixin):
    timeline = models.ForeignKey('Timeline', 
    related_name='e_unbind_timeline_user', blank=True)

    peer = models.ForeignKey('core_app.User', null=True, blank=True)
    html_template = 'timeline_app/e-unbind-timeline-user.html'

class EPastePost(Event):
    timeline = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_paste_post0', blank=True)

    posts = models.ManyToManyField('post_app.Post', null=True,  
    related_name='e_paste_post1', blank=True, symmetrical=False)
    html_template = 'timeline_app/e-paste-post.html'






