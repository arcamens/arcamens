from django.utils.translation import ugettext_lazy as _
from core_app.models import  User, Event, Node
from timeline_app.model_mixins import *
from django.db import models
from django.db.models import Q
import datetime

class Timeline(TimelineMixin, Node):
    users = models.ManyToManyField('core_app.User', null=True,  
    related_name='timelines', blank=True, symmetrical=False)

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








