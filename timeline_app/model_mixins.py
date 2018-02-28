from django.core.urlresolvers import reverse

class TimelineMixin(object):
    """
    Mixins.
    """

    @classmethod
    def get_user_timelines(cls, user):
        timelines = user.timelines.filter(
            organization=user.default)
        return timelines

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



