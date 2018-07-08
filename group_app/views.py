from group_app.models import Group, ECreateGroup, EDeleteGroup, \
EUnbindGroupUser, EUpdateGroup, EPastePost, EBindGroupUser, GroupPin
from post_app.models import Post, PostFilter, GlobalPostFilter
from core_app.models import Organization, User, Clipboard
from core_app.views import GuardianView
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import View
from django.conf import settings
from jscroll.wrappers import JScroll
from django.db.models import Q, F
import post_app.models
import operator
from . import forms
from . import models
import json
# Create your views here.

class ListPosts(GuardianView):
    """
    This view is performed to be executed just if the logged user
    in fact belongs to the group. 

    It also checks if the logged user organization contains the group.
    """

    def get(self, request, group_id):
        # Make sure i belong to the group and my default
        # organization contains the group.
        group = self.me.groups.get(
            id=group_id, organization=self.me.default)

        filter, _ = PostFilter.objects.get_or_create(
        user=self.me, group=group)

        posts     = group.posts.all()
        total     = posts.count()
        boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        listpins  = self.me.listpin_set.filter(organization=self.me.default)
        cardpins  = self.me.cardpin_set.filter(organization=self.me.default)

        grouppins = self.me.grouppin_set.filter(
        organization=self.me.default)

        posts = filter.collect(posts)
        posts = posts.order_by('-priority')
        count = posts.count()
        elems = JScroll(self.me.id, 'group_app/list-posts-scroll.html', posts)

        env = {'group':group, 'count': count, 'total': total, 
        'grouppins': grouppins, 'elems':elems.as_window(), 
        'filter': filter, 'boardpins': boardpins, 'listpins': listpins, 
        'cardpins': cardpins}

        return render(request, 'group_app/list-posts.html', env)

class CreateGroup(GuardianView):
    """
    As every user has its own workspace everyone can create groups.
    """

    def get(self, request, organization_id):
        form = forms.GroupForm()
        return render(request, 'group_app/create-group.html', 
        {'form':form, 'user_id': self.user_id, 'organization_id':organization_id})

    def post(self, request, organization_id):
        form = forms.GroupForm(request.POST)

        if not form.is_valid():
            return render(request, 'group_app/create-group.html',
                        {'form': form, 'user_id':self.user_id, 
                                'organization_id': organization_id}, status=400)

        organization = Organization.objects.get(id=organization_id)
        record       = form.save()
        record.owner = self.me
        record.organization  = organization
        form.save()

        users = self.me.default.users.all() if record.open else (self.me, )
        record.users.add(*users)
        record.save()

        event = ECreateGroup.objects.create(organization=self.me.default,
        group=record, user=self.me)

        event.dispatch(*users)

        return redirect('core_app:list-nodes')

class DeleteGroup(GuardianView):
    """
    Just the owner of the group is supposed to delete the group.
    The group also has to be in the logged user default organization.
    """

    def get(self, request,  group_id):
        # Make sure i belong to the organization.
        group = self.me.groups.get(id = group_id,
        organization=self.me.default)

        form = forms.ConfirmGroupDeletionForm()

        return render(request, 'group_app/delete-group.html', 
        {'group': group, 'form': form})

    def post(self, request, group_id):
        group = self.me.groups.get(id = group_id,
        organization=self.me.default)

        if group.owner != self.me:
            return HttpResponse('Just owner can do that!', status=403)

        form = forms.ConfirmGroupDeletionForm(request.POST, 
        confirm_token=group.name)

        if not form.is_valid():
            return render(request, 
                'group_app/delete-group.html', 
                    {'group': group, 'form': form}, status=400)

        event    = EDeleteGroup.objects.create(organization=self.me.default,
        group_name=group.name, user=self.me)

        event.dispatch(*group.users.all())
        group.delete()

        return redirect('core_app:list-nodes')

class UnbindGroupUser(GuardianView):
    """
    Just users whose default organization matches the group organization
    can perform this view. Everyone in group is supposed to add/remove members.
    """

    def get(self, request, group_id, user_id):
        user = User.objects.get(id=user_id, organizations=self.me.default)

        # Make sure i belong to the group.
        group = self.me.groups.get(id=group_id, 
        organization=self.me.default)

        if group.owner == user:
            return HttpResponse("You can't remove \
                the group owner!", status=403)

        event = EUnbindGroupUser.objects.create(organization=self.me.default,
        group=group, user=self.me, peer=user)
        event.dispatch(*group.users.all())

        group.users.remove(user)
        return HttpResponse(status=200)

class UpdateGroup(GuardianView):
    """
    Just the owner is supposed to perform this view.
    But for viewing the dialog it is necessary to belong to the group.
    """

    def get(self, request, group_id):
        group = self.me.groups.get(id=group_id, 
        organization=self.me.default)

        return render(request, 'group_app/update-group.html',
        {'group': group, 'form': forms.UpdateGroupForm(instance=group)})

    def post(self, request, group_id):
        record = self.me.groups.get(id=group_id, 
        organization=self.me.default)

        if record.owner != self.me:
            return HttpResponse('Just owner can do that!', status=403)

        form = forms.UpdateGroupForm(request.POST, instance=record)
        if not form.is_valid():
            return render(request, 
                'group_app/update-group.html',
                     {'group': record, 'form': form})
        form.save()

        event = EUpdateGroup.objects.create(
        organization=self.me.default, group=record, user=self.me)
        event.dispatch(*record.users.all())

        return redirect('group_app:list-posts', 
        group_id=record.id)

class SelectDestinGroup(GuardianView):
    def get(self, request, group_id):
        group = models.Group.objects.get(id=group_id, 
        organization=self.me.default, users=self.me)

        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)

        posts = clipboard.posts.all()
        total = posts.count() 

        return render(request, 'group_app/select-destin-group.html', 
        {'user': self.me, 'group': group, 'posts': posts,  'total': total})

class PastePost(GuardianView):
    def get(self, request, group_id, post_id):
        group = models.Group.objects.get(id=group_id, 
        organization=self.me.default, users=self.me)

        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)

        # Make sure the post is on the user clipboard.
        post = clipboard.posts.get(id=post_id)
        head = group.posts.order_by('-priority').first()

        priority      = head.priority if head else 0
        post.ancestor = group

        # Maybe not necessary just +1.
        post.priority = post.priority + priority
        post.save()

        event = EPastePost(organization=self.me.default, 
        group=group, user=self.me)

        event.save(hcache=False)
        event.posts.add(post)
    
        # Workers of the post dont need to be notified of this event
        # because them may not belong to the board at all.
        event.dispatch(*group.users.all())
        event.save()

        clipboard.posts.remove(post)
        return redirect('group_app:select-destin-group', group_id=group.id)

class PasteAllPosts(GuardianView):
    """
    Everyone who belongs to the group is allowed to perform
    this view.
    """

    def get(self, request, group_id):
        # Make sure i belong to the group and my default organization
        # contains it.
        group = self.me.groups.get(
        id=group_id, organization=self.me.default)

        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)
        posts = clipboard.posts.all()

        if not posts.exists():
            return HttpResponse("There is no post on \
                the clipboard.", status=403)

        post = group.posts.order_by('-priority').first()
        priority = post.priority if post else 0
        posts.update(ancestor=group, priority=F('priority') + priority)

        posts.update(ancestor=group, priority=priority)
        event = EPastePost(organization=self.me.default, 
        group=group, user=self.me)

        event.save(hcache=False)
        event.posts.add(*posts)

        users = group.users.all()
        event.dispatch(*users)
        event.save()

        clipboard.posts.clear()
        return redirect('group_app:list-posts', 
        group_id=group.id)

class BindGroupUser(GuardianView):
    """
    Everyone in the group can perform this view but its default organization
    has to contain the group and the user has to be in the organization of the
    group as well.
    """

    def get(self, request, group_id, user_id):
        user     = User.objects.get(id=user_id, organizations=self.me.default)
        group = self.me.groups.get(id=group_id, 
        organization=self.me.default)

        group.users.add(user)
        group.save()

        event = EBindGroupUser.objects.create(organization=self.me.default,
        group=group, user=self.me, peer=user)
        event.dispatch(*group.users.all())

        return HttpResponse(status=200)

class ManageUserGroups(GuardianView):
    """
    Make sure the logged user can view the groups that he belongs to.
    It also makes sure the listed groups belong to his default organization.
    """

    def get(self, request, user_id):
        # Make sure the user belongs to my default organization.
        user      = User.objects.get(id=user_id, organizations=self.me.default)
        groups = self.me.groups.filter(organization=self.me.default)
        total     = groups.count()
        excluded  = groups.exclude(users=user)
        included  = groups.filter(users=user)

        env = {'user': user, 'included': included, 
        'excluded': excluded,  'count': total, 'total': total, 'me': self.me, 
        'organization': self.me.default, 'form':forms.GroupSearchForm()}

        return render(request, 'group_app/manage-user-groups.html', env)

    def post(self, request, user_id):
        # Make sure the user belongs to my default organization.
        user      = User.objects.get(id=user_id, organizations=self.me.default)
        sqlike    = Group.from_sqlike()
        form      = forms.GroupSearchForm(request.POST, sqlike=sqlike)
        groups = self.me.groups.filter(organization=self.me.default)
        total     = groups.count()

        if not form.is_valid():
            return render(request, 'group_app/manage-user-groups.html', 
                {'user': user, 'me': self.me, 'organization': self.me.default, 
                    'count': 0,'form':form, 'total': total,}, status=400)

        excluded  = groups.exclude(users=user)
        included  = groups.filter(users=user)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)
        count    = included.count() + excluded.count()
        env      = {'user': user, 'included': included, 'excluded': excluded, 
        'total': total, 'me': self.me, 'organization': self.me.default, 
        'form':form, 'count': count}

        return render(request, 'group_app/manage-user-groups.html', env)

class ManageGroupUsers(GuardianView):
    """
    The listed users are supposed to belong to the logged user default
    organization. It also checks if the user belongs to the group
    in order to list its users.
    """

    def get(self, request, group_id):
        group = self.me.groups.get(id=group_id, 
        organization=self.me.default)

        included = group.users.all()
        users    = self.me.default.users.all()
        excluded = users.exclude(groups=group)
        total    = included.count() + excluded.count()

        return render(request, 'group_app/manage-group-users.html', 
        {'included': included, 'excluded': excluded, 'group': group,
        'me': self.me, 'organization': self.me.default,'form':forms.UserSearchForm(), 
        'count': total, 'total': total,})

    def post(self, request, group_id):
        sqlike   = User.from_sqlike()
        form     = forms.UserSearchForm(request.POST, sqlike=sqlike)

        group = self.me.groups.get(id=group_id, 
        organization=self.me.default)

        included = group.users.all()
        users    = self.me.default.users.all()
        excluded = users.exclude(groups=group)

        total = included.count() + excluded.count()
        
        if not form.is_valid():
            return render(request, 'group_app/manage-group-users.html', 
                {'me': self.me, 'group': group, 'count': 0, 'total': total,
                        'form':form}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)
        count = included.count() + excluded.count()

        return render(request, 'group_app/manage-group-users.html', 
        {'included': included, 'excluded': excluded, 'group': group,
        'me': self.me, 'organization': self.me.default,'form':form, 
        'count': count, 'total': total,})

class GroupLink(GuardianView):
    """
    The user is supposed to belong to the group and his
    default organization has to contain the group as well.
    """

    def get(self, request, group_id):
        record = self.me.groups.get(id=group_id,
        organization=self.me.default)

        boardpins    = self.me.boardpin_set.filter(organization=self.me.default)
        listpins     = self.me.listpin_set.filter(organization=self.me.default)
        cardpins     = self.me.cardpin_set.filter(organization=self.me.default)
        grouppins = self.me.grouppin_set.filter(
            organization=self.me.default)

        organizations = self.me.organizations.exclude(id=self.me.default.id)
        env = {'group': record, 'user': self.me, 'boardpins': boardpins, 
        'default': self.me.default, 'listpins': listpins, 'cardpins': cardpins, 
        'grouppins': grouppins, 'organization': self.me.default, 
        'organizations': organizations, 'settings': settings}

        return render(request, 'group_app/group-link.html', env)

class PinGroup(GuardianView):
    """
    Just performed if the logged user default organization
    contains the group and the user belongs to such a group.
    """

    def get(self, request, group_id):
        group = self.me.groups.get(id=group_id, 
        organization=self.me.default)

        pin   = GroupPin.objects.create(user=self.me, 
        organization=self.me.default, group=group)
        return redirect('board_app:list-pins')

class Unpin(GuardianView):
    """
    Just performed if the pin is mine and its organization is my default
    organization.
    """

    def get(self, request, pin_id):
        pin = self.me.grouppin_set.get(id=pin_id)
        pin.delete()
        return redirect('board_app:list-pins')














