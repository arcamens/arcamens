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
    This view is performed to be executed just if the logged user
    in fact belongs to the timeline. 

    It also checks if the logged user organization contains the timeline.
    """

    def get(self, request, timeline_id):
        # Make sure i belong to the timeline and my default
        # organization contains the timeline.
        timeline = self.me.timelines.get(
            id=timeline_id, organization=self.me.default)

        filter, _ = PostFilter.objects.get_or_create(
        user=self.me, timeline=timeline)

        posts     = timeline.posts.all()
        total     = posts.count()
        boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        listpins  = self.me.listpin_set.filter(organization=self.me.default)
        cardpins  = self.me.cardpin_set.filter(organization=self.me.default)

        timelinepins = self.me.timelinepin_set.filter(
        organization=self.me.default)

        posts = filter.collect(posts)
        posts = posts.order_by('-created')
        count = posts.count()
        elems = JScroll(self.me.id, 'timeline_app/list-posts-scroll.html', posts)

        env = {'timeline':timeline, 'count': count, 'total': total, 
        'timelinepins': timelinepins, 'elems':elems.as_window(), 
        'filter': filter, 'boardpins': boardpins, 'listpins': listpins, 
        'cardpins': cardpins}

        return render(request, 'timeline_app/list-posts.html', env)

class CreateTimeline(GuardianView):
    """
    As every user has its own workspace everyone can create timelines.
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
        record       = form.save(commit=False)
        record.owner = self.me
        record.organization  = organization
        form.save()
        record.users.add(self.me)
        record.save()

        event = ECreateTimeline.objects.create(organization=self.me.default,
        timeline=record, user=self.me)

        event.dispatch(self.me)

        return redirect('core_app:list-nodes')

class DeleteTimeline(GuardianView):
    """
    Just the owner of the timeline is supposed to delete the timeline.
    The timeline also has to be in the logged user default organization.
    """

    def get(self, request,  timeline_id):
        # Make sure i belong to the organization.
        timeline = self.me.timelines.get(id = timeline_id,
        organization=self.me.default)

        form = forms.ConfirmTimelineDeletionForm()

        return render(request, 'timeline_app/delete-timeline.html', 
        {'timeline': timeline, 'form': form})

    def post(self, request, timeline_id):
        timeline = self.me.timelines.get(id = timeline_id,
        organization=self.me.default)

        if timeline.owner != self.me:
            return HttpResponse('Just owner can do that!', status=403)

        form = forms.ConfirmTimelineDeletionForm(request.POST, 
        confirm_token=timeline.name)

        if not form.is_valid():
            return render(request, 
                'timeline_app/delete-timeline.html', 
                    {'timeline': timeline, 'form': form}, status=400)

        event    = EDeleteTimeline.objects.create(organization=self.me.default,
        timeline_name=timeline.name, user=self.me)

        event.dispatch(*timeline.users.all())
        timeline.delete()

        return redirect('core_app:list-nodes')

class UnbindTimelineUser(GuardianView):
    """
    Just users whose default organization matches the timeline organization
    can perform this view. Everyone in timeline is supposed to add/remove members.
    """

    def get(self, request, timeline_id, user_id):
        user = User.objects.get(id=user_id, organizations=self.me.default)

        # Make sure i belong to the timeline.
        timeline = self.me.timelines.get(id=timeline_id, 
        organization=self.me.default)

        if timeline.owner == user:
            return HttpResponse("You can't remove \
                the timeline owner!", status=403)

        event = EUnbindTimelineUser.objects.create(organization=self.me.default,
        timeline=timeline, user=self.me, peer=user)
        event.dispatch(*timeline.users.all())

        timeline.users.remove(user)
        return HttpResponse(status=200)

class UpdateTimeline(GuardianView):
    """
    Just the owner is supposed to perform this view.
    But for viewing the dialog it is necessary to belong to the timeline.
    """

    def get(self, request, timeline_id):
        timeline = self.me.timelines.get(id=timeline_id, 
        organization=self.me.default)

        return render(request, 'timeline_app/update-timeline.html',
        {'timeline': timeline, 'form': forms.TimelineForm(instance=timeline)})

    def post(self, request, timeline_id):
        record = self.me.timelines.get(id=timeline_id, 
        organization=self.me.default)

        if record.owner != self.me:
            return HttpResponse('Just owner can do that!', status=403)

        form = forms.TimelineForm(request.POST, instance=record)
        if not form.is_valid():
            return render(request, 
                'timeline_app/update-timeline.html',
                     {'timeline': record, 'form': form})
        form.save()

        event = EUpdateTimeline.objects.create(
        organization=self.me.default, timeline=record, user=self.me)
        event.dispatch(*record.users.all())

        return redirect('timeline_app:list-posts', 
        timeline_id=record.id)

class PastePosts(GuardianView):
    """
    Everyone who belongs to the timeline is allowed to perform
    this view.
    """

    def get(self, request, timeline_id):
        # Make sure i belong to the timeline and my default organization
        # contains it.
        timeline = self.me.timelines.get(
        id=timeline_id, organization=self.me.default)

        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)
        posts = clipboard.posts.all()

        if not posts.exists():
            return HttpResponse("There is no post on \
                the clipboard.", status=403)

        posts.update(ancestor=timeline)
        event = EPastePost(organization=self.me.default, 
        timeline=timeline, user=self.me)

        event.save(hcache=False)
        event.posts.add(*posts)

        users = timeline.users.all()
        event.dispatch(*users)
        event.save()

        clipboard.posts.clear()
        return redirect('timeline_app:list-posts', 
        timeline_id=timeline.id)

class BindTimelineUser(GuardianView):
    """
    Everyone in the timeline can perform this view but its default organization
    has to contain the timeline and the user has to be in the organization of the
    timeline as well.
    """

    def get(self, request, timeline_id, user_id):
        user     = User.objects.get(id=user_id, organizations=self.me.default)
        timeline = self.me.timelines.get(id=timeline_id, 
        organization=self.me.default)

        timeline.users.add(user)
        timeline.save()

        event = EBindTimelineUser.objects.create(organization=self.me.default,
        timeline=timeline, user=self.me, peer=user)
        event.dispatch(*timeline.users.all())

        return HttpResponse(status=200)

class ManageUserTimelines(GuardianView):
    """
    Make sure the logged user can view the timelines that he belongs to.
    It also makes sure the listed timelines belong to his default organization.
    """

    def get(self, request, user_id):
        # Make sure the user belongs to my default organization.
        user      = User.objects.get(id=user_id, organizations=self.me.default)
        timelines = self.me.timelines.filter(organization=self.me.default)
        total     = timelines.count()
        excluded  = timelines.exclude(users=user)
        included  = timelines.filter(users=user)

        env = {'user': user, 'included': included, 
        'excluded': excluded,  'count': total, 'total': total, 'me': self.me, 
        'organization': self.me.default, 'form':forms.TimelineSearchForm()}

        return render(request, 'timeline_app/manage-user-timelines.html', env)

    def post(self, request, user_id):
        # Make sure the user belongs to my default organization.
        user      = User.objects.get(id=user_id, organizations=self.me.default)
        sqlike    = Timeline.from_sqlike()
        form      = forms.TimelineSearchForm(request.POST, sqlike=sqlike)
        timelines = self.me.timelines.filter(organization=self.me.default)
        total     = timelines.count()

        if not form.is_valid():
            return render(request, 'timeline_app/manage-user-timelines.html', 
                {'user': user, 'me': self.me, 'organization': self.me.default, 
                    'count': 0,'form':form, 'total': total,}, status=400)

        excluded  = timelines.exclude(users=user)
        included  = timelines.filter(users=user)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)
        count    = included.count() + excluded.count()
        env      = {'user': user, 'included': included, 'excluded': excluded, 
        'total': total, 'me': self.me, 'organization': self.me.default, 
        'form':form, 'count': count}

        return render(request, 'timeline_app/manage-user-timelines.html', env)

class ManageTimelineUsers(GuardianView):
    """
    The listed users are supposed to belong to the logged user default
    organization. It also checks if the user belongs to the timeline
    in order to list its users.
    """

    def get(self, request, timeline_id):
        timeline = self.me.timelines.get(id=timeline_id, 
        organization=self.me.default)

        included = timeline.users.all()
        users    = self.me.default.users.all()
        excluded = users.exclude(timelines=timeline)
        total    = included.count() + excluded.count()

        return render(request, 'timeline_app/manage-timeline-users.html', 
        {'included': included, 'excluded': excluded, 'timeline': timeline,
        'me': self.me, 'organization': self.me.default,'form':forms.UserSearchForm(), 
        'count': total, 'total': total,})

    def post(self, request, timeline_id):
        sqlike   = User.from_sqlike()
        form     = forms.UserSearchForm(request.POST, sqlike=sqlike)

        timeline = self.me.timelines.get(id=timeline_id, 
        organization=self.me.default)

        included = timeline.users.all()
        users    = self.me.default.users.all()
        excluded = users.exclude(timelines=timeline)

        total = included.count() + excluded.count()
        
        if not form.is_valid():
            return render(request, 'timeline_app/manage-timeline-users.html', 
                {'me': self.me, 'timeline': timeline, 'count': 0, 'total': total,
                        'form':form}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)
        count = included.count() + excluded.count()

        return render(request, 'timeline_app/manage-timeline-users.html', 
        {'included': included, 'excluded': excluded, 'timeline': timeline,
        'me': self.me, 'organization': self.me.default,'form':form, 
        'count': count, 'total': total,})

class TimelineLink(GuardianView):
    """
    The user is supposed to belong to the timeline and his
    default organization has to contain the timeline as well.
    """

    def get(self, request, timeline_id):
        record = self.me.timelines.get(id=timeline_id,
        organization=self.me.default)

        boardpins    = self.me.boardpin_set.filter(organization=self.me.default)
        listpins     = self.me.listpin_set.filter(organization=self.me.default)
        cardpins     = self.me.cardpin_set.filter(organization=self.me.default)
        timelinepins = self.me.timelinepin_set.filter(
            organization=self.me.default)

        organizations = self.me.organizations.exclude(id=self.me.default.id)
        env = {'timeline': record, 'user': self.me, 'boardpins': boardpins, 
        'default': self.me.default, 'listpins': listpins, 'cardpins': cardpins, 
        'timelinepins': timelinepins, 'organization': self.me.default, 
        'organizations': organizations, 'settings': settings}

        return render(request, 'timeline_app/timeline-link.html', env)

class PinTimeline(GuardianView):
    """
    Just performed if the logged user default organization
    contains the timeline and the user belongs to such a timeline.
    """

    def get(self, request, timeline_id):
        timeline = self.me.timelines.get(id=timeline_id, 
        organization=self.me.default)

        pin   = TimelinePin.objects.create(user=self.me, 
        organization=self.me.default, timeline=timeline)
        return redirect('board_app:list-pins')

class Unpin(GuardianView):
    """
    Just performed if the pin is mine and its organization is my default
    organization.
    """

    def get(self, request, pin_id):
        pin = self.me.timelinepin_set.get(id=pin_id)
        pin.delete()
        return redirect('board_app:list-pins')




