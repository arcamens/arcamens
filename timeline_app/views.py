from timeline_app.models import Timeline, ECreateTimeline, EDeleteTimeline, \
EUnbindTimelineUser, EUpdateTimeline, EPastePost, TimelineFilter, EBindTimelineUser
from post_app.models import Post, PostFilter, GlobalPostFilter
from core_app.models import Organization, User, Clipboard
from core_app.views import GuardianView, CashierView
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import View
from django.db.models import Q
from core_app import ws
import post_app.models
import operator
from . import forms
from . import models
# Create your views here.

class PostPaginator(GuardianView):
    def get(self, request, timeline_id):
        pass

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
        user      = User.objects.get(id=self.user_id)
        filter, _ = GlobalPostFilter.objects.get_or_create(
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

        event = ECreateTimeline.objects.create(organization=user.default,
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
        timeline = Timeline.objects.get(id=timeline_id)
        timeline.users.remove(user)
        timeline.save()

        me    = User.objects.get(id=self.user_id)
        event = EUnbindTimelineUser.objects.create(organization=me.default,
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

        event.users.add(*record.users.all())

        ws.client.publish('timeline%s' % record.id, 
            'subscribe timeline%s' % record.id, 0, False)

        ws.client.publish('timeline%s' % record.id, 
            'sound', 0, False)

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
        posts.update(ancestor=timeline)

        event = EPastePost(
        organization=user.default, timeline=timeline, user=user)
        event.save(hcache=False)
        event.posts.add(*posts)
        event.users.add(*users)
        event.save()

        ws.client.publish('timeline%s' % timeline.id, 
            'sound', 0, False)
    
        clipboard.posts.clear()
        return redirect('timeline_app:list-posts', 
        timeline_id=timeline.id)

class SetupTimelineFilter(GuardianView):
    def get(self, request, organization_id):
        filter = TimelineFilter.objects.get(
        user__id=self.user_id, organization__id=organization_id)
        organization = Organization.objects.get(id=organization_id)

        return render(request, 'timeline_app/setup-timeline-filter.html', 
        {'form': forms.TimelineFilterForm(instance=filter), 
        'organization': organization})

    def post(self, request, organization_id):
        record = TimelineFilter.objects.get(
        organization__id=organization_id, user__id=self.user_id)

        form   = forms.TimelineFilterForm(request.POST, instance=record)
        organization = Organization.objects.get(id=organization_id)

        if not form.is_valid():
            return render(request, 'timeline_app/setup-timeline-filter.html',
                   {'timeline': record, 'form': form, 
                        'organization': organization}, status=400)
        form.save()
        return redirect('timeline_app:list-timelines')

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
        filter, _ = TimelineFilter.objects.get_or_create(
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

class BindTimelineUser(GuardianView):
    def get(self, request, timeline_id, user_id):
        user = User.objects.get(id=user_id)
        timeline = Timeline.objects.get(id=timeline_id)

        timeline.users.add(user)
        timeline.save()

        me = User.objects.get(id=self.user_id)

        event    = EBindTimelineUser.objects.create(organization=me.default,
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

        me = User.objects.get(id=self.user_id)
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
        form = forms.UserSearchForm(request.POST)
        me   = User.objects.get(id=self.user_id)

        timeline = Timeline.objects.get(id=timeline_id)
        included = timeline.users.all()
        excluded = User.objects.exclude(timelines=timeline)
        total = included.count() + excluded.count()
        
        if not form.is_valid():
            return render(request, 'timeline_app/manage-timeline-users.html', 
                {'me': me, 'timeline': timeline, 'count': 0, 'total': total,
                        'form':form}, status=400)

        included = User.collect_users(included, form.cleaned_data['name'])
        excluded = User.collect_users(excluded, form.cleaned_data['name'])
        count = included.count() + excluded.count()

        return render(request, 'timeline_app/manage-timeline-users.html', 
        {'included': included, 'excluded': excluded, 'timeline': timeline,
        'me': me, 'organization': me.default,'form':form, 
        'count': count, 'total': total,})




