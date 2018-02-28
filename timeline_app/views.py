from core_app.views import GuardianView, CashierView
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import View
from timeline_app import models
from timeline_app import forms
from functools import reduce
from django.db.models import Q
from core_app import ws
from core_app.models import Organization, User
import timeline_app.models
import post_app.models
from post_app.models import Post
from core_app.models import Clipboard
import operator

# Create your views here.

class Timeline(GuardianView):
    """
    """

    def get(self, request, timeline_id):
        timeline = models.Timeline.objects.get(id=timeline_id)
        return render(request, 'timeline_app/timeline.html', 
        {'timeline':timeline})

class PostPaginator(GuardianView):
    def get(self, request, timeline_id):
        pass

class ListPosts(GuardianView):
    """
    """

    def get(self, request, timeline_id):
        timeline  = models.Timeline.objects.get(id=timeline_id)
        user      = User.objects.get(id=self.user_id)

        filter, _ = post_app.models.PostFilter.objects.get_or_create(
        user=user, timeline=timeline)

        posts      = timeline.posts.all()
        total      = posts.count()

        posts      = Post.collect_posts(posts, 
        filter.pattern, filter.done) if filter.status \
        else posts.filter(done=False)

        posts = posts.order_by('-created')

        return render(request, 'timeline_app/list-posts.html', 
        {'timeline':timeline, 'total': total, 'posts':posts, 'filter': filter})

class ListAllPosts(ListPosts):
    """
    """

    def get(self, request, user_id):
        user = User.objects.get(id=self.user_id)

        filter, _ = post_app.models.GlobalPostFilter.objects.get_or_create(
        user=user, organization=user.default)

        posts = Post.get_allowed_posts(user)
        total = posts.count()

        posts = Post.collect_posts(posts, 
        filter.pattern, filter.done) if filter.status \
        else posts.filter(done=False)

        return render(request, 'timeline_app/list-all-posts.html', 
        {'user':user, 'posts':posts, 'total': total, 'filter': filter, 
        'organization': user.default})

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

        event = models.ECreateTimeline.objects.create(organization=user.default,
        timeline=record, user=user)

        # Wondering if organization admins should be notified of this
        # event. The same behavior for board creation too.
        event.users.add(user)

        ws.client.publish('user%s' % user.id, 
            'subscribe timeline%s' % record.id, 0, False)

        ws.client.publish('user%s' % user.id, 
            'sound', 0, False)

        # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        # channel    = connection.channel()
        
        # channel.queue_bind(exchange=str(organization.id),
        # queue=str(user.id), routing_key=str(record.id))
        # connection.close()

        return redirect('timeline_app:list-timelines')

class DeleteTimeline(GuardianView):
    def get(self, request,  timeline_id):
        timeline = models.Timeline.objects.get(id = timeline_id)
        user     = User.objects.get(id=self.user_id)
        event    = models.EDeleteTimeline.objects.create(organization=user.default,
        timeline_name=timeline.name, user=user)

        ws.client.publish('timeline%s' % timeline.id, 
            'sound', 0, False)

        # should tell users to unsubscribe here.
        # it may hide bugs.
        event.users.add(*timeline.users.all())
        timeline.delete()

            
        return redirect('timeline_app:list-timelines')

class UnbindTimelineUser(GuardianView):
    def get(self, request, timeline_id, user_id):
        user = User.objects.get(id=user_id)
        timeline = models.Timeline.objects.get(id=timeline_id)
        timeline.users.remove(user)
        timeline.save()
        me = User.objects.get(id=self.user_id)

        event    = models.EUnbindTimelineUser.objects.create(organization=me.default,
        timeline=timeline, user=me, peer=user)

        event.users.add(*timeline.users.all())

        ws.client.publish('timeline%s' % timeline.id, 
            'sound', 0, False)

        # When user is removed from timline then it
        # gets unsubscribed from the timeline.
        ws.client.publish('user%s' % user.id, 
            'unsubscribe timeline%s' % timeline.id, 0, False)

        # As said before, order of events cant be determined
        # when dispatched towards two queues. It might
        # happen of sound event being dispatched before subscribe event.
        # So, we warrant soud to happen.
        ws.client.publish('user%s' % user.id, 
            'sound', 0, False)

        return HttpResponse(status=200)

class UpdateTimeline(GuardianView):
    def get(self, request, timeline_id):
        timeline = models.Timeline.objects.get(id=timeline_id)
        return render(request, 'timeline_app/update-timeline.html',
        {'timeline': timeline, 'form': forms.TimelineForm(instance=timeline)})

    def post(self, request, timeline_id):
        record  = models.Timeline.objects.get(id=timeline_id)
        form    = forms.TimelineForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'timeline_app/update-timeline.html',
                                    {'timeline': record, 'form': form})
        form.save()

        user  = User.objects.get(id=self.user_id)
        event = models.EUpdateTimeline.objects.create(organization=user.default,
        timeline=record, user=user)

        event.users.add(*record.users.all())

        ws.client.publish('timeline%s' % record.id, 
            'subscribe timeline%s' % record.id, 0, False)

        ws.client.publish('timeline%s' % record.id, 
            'sound', 0, False)

        return redirect('timeline_app:list-posts', 
        timeline_id=record.id)

class PastePosts(GuardianView):
    def get(self, request, timeline_id):
        timeline = models.Timeline.objects.get(id=timeline_id)
        user     = User.objects.get(id=self.user_id)
        users    = timeline.users.all()

        clipboard, _    = Clipboard.objects.get_or_create(
        user=user, organization=user.default)

        for ind in clipboard.posts.all():
            ind.ancestor = timeline
            ind.save()
            event = post_app.models.ECreatePost.objects.create(
            organization=user.default, timeline=timeline, 
            post=ind, user=user)
            event.users.add(*users)

        ws.client.publish('timeline%s' % timeline.id, 
            'sound', 0, False)
    
        clipboard.posts.clear()
        return redirect('timeline_app:list-posts', 
        timeline_id=timeline.id)

class SetupTimelineFilter(GuardianView):
    def get(self, request, organization_id):
        filter = models.TimelineFilter.objects.get(
        user__id=self.user_id, organization__id=organization_id)
        organization = Organization.objects.get(id=organization_id)

        return render(request, 'timeline_app/setup-timeline-filter.html', 
        {'form': forms.TimelineFilterForm(instance=filter), 
        'organization': organization})

    def post(self, request, organization_id):
        record = models.TimelineFilter.objects.get(
        organization__id=organization_id, user__id=self.user_id)

        form   = forms.TimelineFilterForm(request.POST, instance=record)
        organization = Organization.objects.get(id=organization_id)

        if not form.is_valid():
            return render(request, 'timeline_app/setup-timeline-filter.html',
                   {'timeline': record, 'form': form, 
                        'organization': organization}, status=400)
        form.save()
        return redirect('timeline_app:list-timelines')

class EUpdateTimeline(GuardianView):
    def get(self, request, event_id):
        event = models.EUpdateTimeline.objects.get(id=event_id)
        return render(request, 'timeline_app/e-update-timeline.html', 
        {'event':event})

class EBindTimelineUser(GuardianView):
    def get(self, request, event_id):
        event = models.EBindTimelineUser.objects.get(id=event_id)
        return render(request, 'timeline_app/e-bind-timeline-user.html', 
        {'event':event})

class ECreateTimeline(GuardianView):
    def get(self, request, event_id):
        event = models.ECreateTimeline.objects.get(id=event_id)
        return render(request, 'timeline_app/e-create-timeline.html', 
        {'event':event})

class EUnbindTimelineUser(GuardianView):
    def get(self, request, event_id):
        event = models.EUnbindTimelineUser.objects.get(id=event_id)
        return render(request, 'timeline_app/e-unbind-timeline-user.html', 
        {'event':event})

class EDeleteTimeline(GuardianView):
    def get(self, request, event_id):
        event = models.EDeleteTimeline.objects.get(id=event_id)
        return render(request, 'timeline_app/e-delete-timeline.html', 
        {'event':event})

class Logout(View):
    """
    """

    def get(self, request):
        del request.session['user_id']
        return redirect('site_app:index')

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

class TimelinePaginator(GuardianView):
    def get(self, request):
        pass

class ListTimelines(CashierView):
    """
    """

    def get(self, request):
        user      = User.objects.get(id=self.user_id)
        filter, _ = timeline_app.models.TimelineFilter.objects.get_or_create(
        user=user, organization=user.default)

        total = user.timelines.filter(organization=user.default)
        children = total.filter(Q(name__icontains=filter.pattern) | \
        Q(description__icontains=filter.pattern) if filter.status \
        else Q(organization=user.default))

        return render(request, 'timeline_app/list-timelines.html', 
        {'user': user, 'children': children, 'total': total,
        'organization':user.default, 'filter': filter})

class UnbindUser(GuardianView):
    def get(self, request, organization_id, user_id):
        user = User.objects.get(id=user_id)

        return redirect('timeline_app:list-users', 
        organization_id=organization.id)

class CheckEvent(GuardianView):
    def get(self, request, user_id):
        user = User.objects.get(
        id=self.user_id)

        try:
            event = user.events.latest('id')
        except Exception:
            return HttpResponse(status=400)
        return HttpResponse(str(event.id), status=200)

class SeenEvent(GuardianView):
    def get(self, request, event_id):
        user  = User.objects.get(id=self.user_id)
        event = models.Event.objects.get(id=event_id)
        event.users.remove(user)
        event.save()
        return redirect('timeline_app:list-events')


class BindTimelineUser(GuardianView):
    def get(self, request, timeline_id, user_id):
        user = User.objects.get(id=user_id)
        timeline = timeline_app.models.Timeline.objects.get(id=timeline_id)

        timeline.users.add(user)
        timeline.save()

        me = User.objects.get(id=self.user_id)

        event    = models.EBindTimelineUser.objects.create(organization=me.default,
        timeline=timeline, user=me, peer=user)

        event.users.add(*timeline.users.all())

        ws.client.publish('timeline%s' % timeline.id, 
            'sound', 0, False)

        ws.client.publish('user%s' % user.id, 
            'subscribe timeline%s' % timeline.id, 0, False)

        # it seems i cant warrant the order the events will be dispatched
        # to the queue, if it is userid queue or timelineid queue
        # then i have to just send again the sound event to the 
        # user queue to warrant the event sound being dispatched.
        # obs: if i'll abandon sound when user interacts it is not
        # necessary.
        ws.client.publish('user%s' % user.id, 
            'sound', 0, False)

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

        me = core_app.models.User.objects.get(id=self.user_id)
        timelines = me.timelines.filter(organization=me.default)

        if not form.is_valid():
            return render(request, 'timeline_app/manage-user-timelines.html', 
                {'user': user, 'included': included, 'excluded': excluded,
                    'me': me, 'organization': me.default, 
                        'form':forms.BindTimelinesForm()}, status=400)

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
        'me': me, 'organization': me.default,'form':forms.BindTimelinesForm()})


class ManageTimelineUsers(GuardianView):
    def get(self, request, timeline_id):
        me = User.objects.get(id=self.user_id)
        timeline = models.Timeline.objects.get(id=timeline_id)

        included = timeline.users.all()
        users = me.default.users.all()
        excluded = users.exclude(timelines=timeline)

        return render(request, 'timeline_app/manage-timeline-users.html', 
        {'included': included, 'excluded': excluded, 'timeline': timeline,
        'me': me, 'organization': me.default,'form':forms.UserSearchForm()})

    def post(self, request, timeline_id):
        form = forms.UserSearchForm(request.POST)

        me = User.objects.get(id=self.user_id)
        timeline = models.Timeline.objects.get(id=timeline_id)
        included = timeline.users.all()
        excluded = User.objects.exclude(timelines=timeline)

        if not form.is_valid():
            return render(request, 'timeline_app/manage-timeline-users.html', 
                {'included': included, 'excluded': excluded,
                    'me': me, 'organization': me.default, 'timeline': timeline,
                        'form':forms.UserSearchForm()}, status=400)

        included = included.filter(
        name__contains=form.cleaned_data['name'])

        excluded = excluded.filter(
        name__contains=form.cleaned_data['name'])

        return render(request, 'timeline_app/manage-timeline-users.html', 
        {'included': included, 'excluded': excluded, 'timeline': timeline,
        'me': me, 'organization': me.default,'form':form})




