from timeline_app.models import Timeline, ECreateTimeline, EDeleteTimeline, \
EUnbindTimelineUser, EUpdateTimeline, EPastePost, EBindTimelineUser, TimelinePin
from post_app.models import Post, PostFilter, GlobalPostFilter
from core_app.models import Organization, User, Clipboard
from core_app.views import GuardianView
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import View
from django.conf import settings
from jsim.jscroll import JScroll
from django.db.models import Q
import post_app.models
import operator
from . import forms
from . import models
import json
# Create your views here.

class ListPosts(GuardianView):
    """
    """

    def get(self, request, timeline_id):
        timeline  = Timeline.objects.get(id=timeline_id)
        user      = User.objects.get(id=self.user_id)

        filter, _ = PostFilter.objects.get_or_create(
        user=user, timeline=timeline)

        posts      = timeline.posts.all()
        total      = posts.count()
        boardpins = user.boardpin_set.filter(organization=user.default)
        listpins = user.listpin_set.filter(organization=user.default)
        cardpins = user.cardpin_set.filter(organization=user.default)
        timelinepins = user.timelinepin_set.filter(organization=user.default)

        posts = filter.collect(posts)
        posts = posts.order_by('-created')
        count = posts.count()
        elems = JScroll(user.id, 'timeline_app/list-posts-scroll.html', posts)

        return render(request, 'timeline_app/list-posts.html', 
        {'timeline':timeline, 'count': count, 'total': total, 'timelinepins': timelinepins,
        'elems':elems.as_window(), 'filter': filter, 'boardpins': boardpins,
        'listpins': listpins, 'cardpins': cardpins})

class CreateTimeline(GuardianView):
    """
    """

    def get(self, request, organization_id):
        form = forms.TimelineForm()
        return render(request, 'timeline_app/create-timeline.html', 
        {'form':form, 'user_id': self.user_id, 'organization_id':organization_id})

    def post(self, request, organization_id):
        form = forms.TimelineForm(request.POST)

        if not form.is_valid():
            return render(request, 'timeline_app/create-timeline.html',
                        {'form': form, 'user_id':self.user_id, 
                                'organization_id': organization_id}, status=400)

        organization = Organization.objects.get(id=organization_id)
        user         = User.objects.get(id=self.user_id)
        record       = form.save(commit=False)
        record.owner = user
        record.organization  = organization
        form.save()
        record.users.add(user)
        record.save()

        event = ECreateTimeline.objects.create(organization=user.default,
        timeline=record, user=user)

        event.dispatch(user)

        user.ws_subscribe(record)
        user.ws_sound()

        return redirect('core_app:list-nodes')

class DeleteTimeline(GuardianView):
    def get(self, request,  timeline_id):
        timeline = Timeline.objects.get(id = timeline_id)
        form = forms.ConfirmTimelineDeletionForm()

        return render(request, 'timeline_app/delete-timeline.html', 
        {'timeline': timeline, 'form': form})

    def post(self, request, timeline_id):
        timeline = Timeline.objects.get(id = timeline_id)

        form = forms.ConfirmTimelineDeletionForm(request.POST, 
        confirm_token=timeline.name)

        if not form.is_valid():
            return render(request, 
                'timeline_app/delete-timeline.html', 
                    {'timeline': timeline, 'form': form}, status=400)

        user     = User.objects.get(id=self.user_id)
        event    = EDeleteTimeline.objects.create(organization=user.default,
        timeline_name=timeline.name, user=user)

        user.ws_sound(timeline)
        user.ws_unsubscribe(timeline, target=timeline)

        # should tell users to unsubscribe here.
        # it may hide bugs.
        event.dispatch(*timeline.users.all())
        timeline.delete()

        return redirect('core_app:list-nodes')

class UnbindTimelineUser(GuardianView):
    def get(self, request, timeline_id, user_id):
        user = User.objects.get(id=user_id)
        timeline = Timeline.objects.get(id=timeline_id)
        timeline.users.remove(user)
        timeline.save()

        me    = User.objects.get(id=self.user_id)
        event = EUnbindTimelineUser.objects.create(organization=me.default,
        timeline=timeline, user=me, peer=user)

        event.dispatch(*timeline.users.all())

        me.ws_sound(timeline)

        # When user is removed from timline then it
        # gets unsubscribed from the timeline.
        me.ws_unsubscribe(timeline, target=user)

        # As said before, order of events cant be determined
        # when dispatched towards two queues. It might
        # happen of sound event being dispatched before subscribe event.
        # So, we warrant soud to happen.
        me.ws_sound(user)

        return HttpResponse(status=200)

class UpdateTimeline(GuardianView):
    def get(self, request, timeline_id):
        timeline = Timeline.objects.get(id=timeline_id)
        return render(request, 'timeline_app/update-timeline.html',
        {'timeline': timeline, 'form': forms.TimelineForm(instance=timeline)})

    def post(self, request, timeline_id):
        record  = Timeline.objects.get(id=timeline_id)
        form    = forms.TimelineForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 
                'timeline_app/update-timeline.html',
                     {'timeline': record, 'form': form})
        form.save()

        user  = User.objects.get(id=self.user_id)
        event = EUpdateTimeline.objects.create(
        organization=user.default, timeline=record, user=user)

        event.dispatch(*record.users.all())

        user.ws_sound(record)

        return redirect('timeline_app:list-posts', 
        timeline_id=record.id)

class PastePosts(GuardianView):
    def get(self, request, timeline_id):
        timeline = Timeline.objects.get(id=timeline_id)
        user     = User.objects.get(id=self.user_id)
        users    = timeline.users.all()

        clipboard, _ = Clipboard.objects.get_or_create(
        user=user, organization=user.default)

        posts = clipboard.posts.all()

        if not posts.exists():
            return HttpResponse("There is no post on \
                the clipboard.", status=403)

        posts.update(ancestor=timeline)
        event = EPastePost(
        organization=user.default, timeline=timeline, user=user)
        event.save(hcache=False)
        event.posts.add(*posts)
        event.dispatch(*users)
        event.save()

        user.ws_sound(timeline)

        clipboard.posts.clear()
        return redirect('timeline_app:list-posts', 
        timeline_id=timeline.id)

class ListEvents(GuardianView):
    """
    """

    def get(self, request):
        user   = User.objects.get(id=self.user_id)
        events = user.events.filter(organization=user.default).order_by('-created')

        # Missing dynamic filter.
        total = user.events.filter(organization=user.default).order_by('-created')

        form = forms.FindEventForm()
        return render(request, 'timeline_app/list-events.html',
        {'user': user, 'events': events, 'form': form, 
        'total': total, 'organization': user.default})

class BindTimelineUser(GuardianView):
    def get(self, request, timeline_id, user_id):
        user = User.objects.get(id=user_id)
        timeline = Timeline.objects.get(id=timeline_id)

        timeline.users.add(user)
        timeline.save()

        me = User.objects.get(id=self.user_id)

        event    = EBindTimelineUser.objects.create(organization=me.default,
        timeline=timeline, user=me, peer=user)

        event.dispatch(*timeline.users.all())

        me.ws_sound(timeline)
        me.ws_subscribe(timeline, target=user)

        # it seems i cant warrant the order the events will be dispatched
        # to the queue, if it is userid queue or timelineid queue
        # then i have to just send again the sound event to the 
        # user queue to warrant the event sound being dispatched.
        # obs: if i'll abandon sound when user interacts it is not
        # necessary.
        me.ws_sound(user)

        return HttpResponse(status=200)

class ManageUserTimelines(GuardianView):
    def get(self, request, user_id):
        me = User.objects.get(id=self.user_id)
        user = User.objects.get(id=user_id)

        timelines = me.timelines.filter(organization=me.default)
        excluded = timelines.exclude(users=user)
        included = timelines.filter(users=user)

        return render(request, 'timeline_app/manage-user-timelines.html', 
        {'user': user, 'included': included, 'excluded': excluded,
        'me': me, 'organization': me.default,'form':forms.BindTimelinesForm()})

    def post(self, request, user_id):
        user = User.objects.get(id=user_id)
        form = forms.BindTimelinesForm(request.POST)

        me = User.objects.get(id=self.user_id)
        timelines = me.timelines.filter(organization=me.default)

        if not form.is_valid():
            return render(request, 'timeline_app/manage-user-timelines.html', 
                {'user': user, 'included': included, 'excluded': excluded,
                    'me': me, 'organization': me.default, 
                        'form':form}, status=400)

        timelines = timelines.filter(Q(
        name__contains=form.cleaned_data['name']) | Q(
        description__contains=form.cleaned_data['name']))

        # timeline.users.add(user)
        # timeline.save()

        # return redirect('timeline_app:list-user-tags', 
        # user_id=user.id)
        excluded = timelines.exclude(users=user)
        included = timelines.filter(users=user)

        return render(request, 'timeline_app/manage-user-timelines.html', 
        {'user': user, 'included': included, 'excluded': excluded,
        'me': me, 'organization': me.default,'form':form})

class ManageTimelineUsers(GuardianView):
    def get(self, request, timeline_id):
        me = User.objects.get(id=self.user_id)
        timeline = Timeline.objects.get(id=timeline_id)

        included = timeline.users.all()
        users    = me.default.users.all()
        excluded = users.exclude(timelines=timeline)
        total    = included.count() + excluded.count()

        return render(request, 'timeline_app/manage-timeline-users.html', 
        {'included': included, 'excluded': excluded, 'timeline': timeline,
        'me': me, 'organization': me.default,'form':forms.UserSearchForm(), 
        'count': total, 'total': total,})

    def post(self, request, timeline_id):
        sqlike = User.from_sqlike()
        form = forms.UserSearchForm(request.POST, sqlike=sqlike)
        me   = User.objects.get(id=self.user_id)

        timeline = Timeline.objects.get(id=timeline_id)
        included = timeline.users.all()
        users    = me.default.users.all()
        excluded = users.exclude(timelines=timeline)

        total = included.count() + excluded.count()
        
        if not form.is_valid():
            return render(request, 'timeline_app/manage-timeline-users.html', 
                {'me': me, 'timeline': timeline, 'count': 0, 'total': total,
                        'form':form}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)
        count = included.count() + excluded.count()

        return render(request, 'timeline_app/manage-timeline-users.html', 
        {'included': included, 'excluded': excluded, 'timeline': timeline,
        'me': me, 'organization': me.default,'form':form, 
        'count': count, 'total': total,})

class TimelineLink(GuardianView):
    """
    """

    def get(self, request, timeline_id):
        record = Timeline.objects.get(id=timeline_id)

        user = User.objects.get(id=self.user_id)
        boardpins = user.boardpin_set.filter(organization=user.default)
        listpins = user.listpin_set.filter(organization=user.default)
        cardpins = user.cardpin_set.filter(organization=user.default)
        timelinepins = user.timelinepin_set.filter(organization=user.default)

        organizations = user.organizations.exclude(id=user.default.id)

        return render(request, 'timeline_app/timeline-link.html', 
        {'timeline': record, 'user': user, 'boardpins': boardpins, 'default': user.default,
        'listpins': listpins, 'cardpins': cardpins, 'timelinepins': timelinepins,
        'organization': user.default, 'organizations': organizations, 
        'settings': settings})

class PinTimeline(GuardianView):
    def get(self, request, timeline_id):
        user  = User.objects.get(id=self.user_id)
        timeline = Timeline.objects.get(id=timeline_id)
        pin   = TimelinePin.objects.create(user=user, 
        organization=user.default, timeline=timeline)
        return redirect('board_app:list-pins')

class Unpin(GuardianView):
    def get(self, request, pin_id):
        pin = TimelinePin.objects.get(id=pin_id)
        pin.delete()
        return redirect('board_app:list-pins')


