from group_app.models import Group, ECreateGroup, EDeleteGroup, Groupship,\
EUnbindGroupUser, EUpdateGroup, EPastePost, EBindGroupUser, GroupPin
from post_app.models import Post, PostFilter, PostSearch
from core_app.models import Organization, User, Clipboard, Membership
from core_app.views import GuardianView
from core_app.sqlikes import SqUser
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import View
from django.conf import settings
from jscroll.wrappers import JScroll
from django.db.models import Q, F, Exists, OuterRef
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

        posts = group.posts.all()
        total = posts.count()

        listpins  = self.me.listpin_set.filter(organization=self.me.default)
        cardpins  = self.me.cardpin_set.filter(organization=self.me.default)
        postpins  = self.me.postpin_set.filter(organization=self.me.default)
        boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        grouppins = self.me.grouppin_set.filter(organization=self.me.default)

        posts = posts.filter(done=False)
        posts = filter.from_sqpost(posts) if filter.status else posts

        posts = posts.order_by('-priority')

        likers = User.objects.filter(id=self.me.pk, post_likes=OuterRef('id'))
        posts = posts.annotate(in_likers=Exists(likers))

        count = posts.count()
    
        # I'm having to evaluate the whole queryset into a list so it can be 
        # cached with jscroll. I'm not sure about the implications of it at all.
        elems = JScroll(self.me.id, 'group_app/list-posts-scroll.html', list(posts.all()))

        env = {'group':group, 'count': count, 'total': total, 
        'grouppins': grouppins, 'elems':elems.as_window(), 'postpins': postpins,
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
        membership = Membership.objects.get(
        user=self.me, organization=self.me.default)

        if membership.status == '2':
            return HttpResponse("Contributors can't create groups!", status=403)

        form = forms.GroupForm(request.POST, me=self.me)
        if not form.is_valid():
            return render(request, 'group_app/create-group.html',
                        {'form': form, 'user_id':self.user_id, 
                                'organization_id': organization_id}, status=400)

        organization = Organization.objects.get(id=organization_id)
        record       = form.save(commit=False)
        record.owner = self.me
        record.organization  = organization
        form.save()

        users = self.me.default.users.all() if record.public else (self.me, )

        groupships = (Groupship(user=ind, group=record, 
        binder=self.me) for ind in users)
        Groupship.objects.bulk_create(groupships)
        groupship = self.me.user_groupship.get(group=record)
        groupship.status = '0'
        groupship.save()

        # Groupship.objects.create(user=self.me, group=record, 
        # binder=self.me, status='0')

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

        if not group.owner == self.me: 
            return HttpResponse("Just the owner can do that!", status=403)

        form = forms.ConfirmGroupDeletionForm(
            request.POST, confirm_token=group.name)

        if not form.is_valid():
            return render(request, 
                'group_app/delete-group.html', 
                    {'group': group, 'form': form}, status=400)

        event    = EDeleteGroup.objects.create(organization=self.me.default,
        group_name=group.name, user=self.me)

        event.dispatch(*group.users.all())
        group.delete()

        return redirect('core_app:list-nodes')

class UpdateGroup(GuardianView):
    """
    Just the owner is supposed to perform this view.
    But for viewing the dialog it is necessary to belong to the group.
    """

    def get(self, request, group_id):
        group = self.me.groups.get(id=group_id, 
        organization=self.me.default)

        return render(request, 'group_app/update-group.html',
        {'group': group, 'form': forms.GroupForm(instance=group)})

    def post(self, request, group_id):
        record = self.me.groups.get(id=group_id, 
        organization=self.me.default)

        if not record.owner == self.me: 
            return HttpResponse("Just the owner can do that!", status=403)

        form = forms.GroupForm(request.POST, instance=record, me=self.me)
        if not form.is_valid():
            return render(request, 
                'group_app/update-group.html',
                     {'group': record, 'form': form}, status=400)
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
        post.done     = False

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

        posts.update(ancestor=group, done=False, 
        priority=F('priority') + priority)

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

class GroupLink(GuardianView):
    """
    The user is supposed to belong to the group and his
    default organization has to contain the group as well.
    """

    def get(self, request, group_id):
        record = self.me.groups.get(id=group_id,
        organization=self.me.default)

        boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        listpins  = self.me.listpin_set.filter(organization=self.me.default)
        cardpins  = self.me.cardpin_set.filter(organization=self.me.default)
        grouppins = self.me.grouppin_set.filter(organization=self.me.default)

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
        group = self.me.groups.get(id=group_id, organization=self.me.default)
        pin   = GroupPin.objects.create(user=self.me, 
        organization=self.me.default, group=group)
        return redirect('board_app:list-pins')

class Unpin(GuardianView):
    """
    Just performed if the pin is mine and its organization is my default
    organization.
    """

    def get(self, request, pin_id):
        pin = self.me.grouppin_set.get(id=pin_id, organization=self.me.default)
        pin.delete()
        return redirect('board_app:list-pins')


class UnbindGroupUsers(GuardianView):
    """
    The listed users are supposed to belong to the logged user default
    organization. It also checks if the user belongs to the group
    in order to list its users.
    """

    def get(self, request, group_id):
        group = self.me.groups.get(id=group_id, organization=self.me.default)

        included = group.users.all()
        users    = self.me.default.users.all()
        total    = included.count() 

        return render(request, 'group_app/unbind-group-users.html', {
        'included': included, 'group': group, 'organization': self.me.default,
        'form':forms.UserSearchForm(), 'me': self.me, 
        'count': total, 'total': total,})

    def post(self, request, group_id):
        sqlike = SqUser()
        form   = forms.UserSearchForm(request.POST, sqlike=sqlike)
        group  = self.me.groups.get(id=group_id, organization=self.me.default)

        included = group.users.all()
        users    = self.me.default.users.all()
        total    = included.count() 
        
        if not form.is_valid():
            return render(request, 'group_app/manage-group-users.html', 
                {'me': self.me, 'group': group, 'count': 0, 'total': total,
                        'form':form}, status=400)

        included = sqlike.run(included)
        count = included.count() 

        return render(request, 'group_app/unbind-group-users.html', 
        {'included': included, 'group': group, 'me': self.me, 
        'organization': self.me.default,'form':form, 
        'count': count, 'total': total,})

class BindGroupUsers(GuardianView):
    """
    The listed users are supposed to belong to the logged user default
    organization. It also checks if the user belongs to the group
    in order to list its users.
    """

    def get(self, request, group_id):
        group = self.me.groups.get(id=group_id, 
        organization=self.me.default)

        users    = self.me.default.users.all()
        excluded = users.exclude(groups=group)
        total    = excluded.count()

        return render(request, 'group_app/bind-group-users.html', 
        {'excluded': excluded, 'group': group, 'me': self.me, 
        'organization': self.me.default,'form':forms.UserSearchForm(), 
        'count': total, 'total': total,})

    def post(self, request, group_id):
        sqlike = SqUser()
        form   = forms.UserSearchForm(request.POST, sqlike=sqlike)
        group  = self.me.groups.get(id=group_id, organization=self.me.default)

        users    = self.me.default.users.all()
        excluded = users.exclude(groups=group)

        total = excluded.count()
        
        if not form.is_valid():
            return render(request, 'group_app/bind-group-users.html', 
                {'me': self.me, 'group': group, 'count': 0, 'total': total,
                        'form':form}, status=400)

        excluded = sqlike.run(excluded)
        count = excluded.count()

        return render(request, 'group_app/bind-group-users.html', 
        {'excluded': excluded, 'group': group, 'me': self.me, 
        'organization': self.me.default,'form':form, 
        'count': count, 'total': total,})

class UnbindUserGroups(GuardianView):
    """
    Make sure the logged user can view the groups that he belongs to.
    It also makes sure the listed groups belong to his default organization.
    """

    def get(self, request, user_id):
        # Make sure the user belongs to my default organization.
        user      = User.objects.get(id=user_id, organizations=self.me.default)
        groups = self.me.groups.filter(organization=self.me.default)
        total     = groups.count()

        included  = groups.filter(users=user)
        count = included.count()

        env = {'user': user, 'included': included, 
        'count': count, 'total': total, 'me': self.me, 
        'organization': self.me.default, 'form':forms.GroupSearchForm()}

        return render(request, 'group_app/unbind-user-groups.html', env)

    def post(self, request, user_id):
        # Make sure the user belongs to my default organization.
        user      = User.objects.get(id=user_id, organizations=self.me.default)
        sqlike    = Group.from_sqlike()
        form      = forms.GroupSearchForm(request.POST, sqlike=sqlike)
        groups = self.me.groups.filter(organization=self.me.default)
        total     = groups.count()

        if not form.is_valid():
            return render(request, 'group_app/unbind-user-groups.html', 
                {'user': user, 'me': self.me, 'organization': self.me.default, 
                    'count': 0,'form':form, 'total': total,}, status=400)

        included  = groups.filter(users=user)
        included = sqlike.run(included)
        count    = included.count() 
        env      = {'user': user, 'included': included, 
        'total': total, 'me': self.me, 'organization': self.me.default, 
        'form':form, 'count': count}

        return render(request, 'group_app/unbind-user-groups.html', env)

class BindUserGroups(GuardianView):
    """
    Make sure the logged user can view the groups that he belongs to.
    It also makes sure the listed groups belong to his default organization.
    """

    def get(self, request, user_id):
        # Make sure the user belongs to my default organization.
        user      = User.objects.get(id=user_id, organizations=self.me.default)
        groups = self.me.groups.filter(organization=self.me.default)
        total     = groups.count()

        excluded = groups.exclude(users=user)
        count    = excluded.count()

        env      = {'user': user, 'excluded': excluded,  'count': count, 
        'total': total, 'me': self.me,  'organization': self.me.default, 
        'form':forms.GroupSearchForm()}

        return render(request, 'group_app/bind-user-groups.html', env)

    def post(self, request, user_id):
        # Make sure the user belongs to my default organization.
        user      = User.objects.get(id=user_id, organizations=self.me.default)
        sqlike    = Group.from_sqlike()
        form      = forms.GroupSearchForm(request.POST, sqlike=sqlike)
        groups = self.me.groups.filter(organization=self.me.default)
        total     = groups.count()

        if not form.is_valid():
            return render(request, 'group_app/bind-user-groups.html', 
                {'user': user, 'me': self.me, 'organization': self.me.default, 
                    'count': 0,'form':form, 'total': total,}, status=400)

        excluded  = groups.exclude(users=user)
        count    = excluded.count()
        env      = {'user': user, 'excluded': excluded, 
        'total': total, 'me': self.me, 'organization': self.me.default, 
        'form':form, 'count': count}

        return render(request, 'group_app/bind-user-groups.html', env)

class CreateGroupshipUser(GuardianView):
    """
    """

    def get(self, request, group_id, user_id):
        user  = User.objects.get(id=user_id, organizations=self.me.default)
        group = self.me.groups.get(id=group_id, organization=self.me.default)
        form  = forms.GroupshipForm()

        return render(request, 'group_app/create-groupship-user.html', {
        'user': user, 'group': group, 'form': form})

    def post(self, request, group_id, user_id):
        user  = User.objects.get(id=user_id, organizations=self.me.default)
        group = self.me.groups.get(id=group_id, organization=self.me.default)

        form = forms.GroupshipForm(request.POST)
        if not form.is_valid():
            return render(request, 'group_app/create-groupship-user.html', {
                'user': user, 'group': group, 'form': form})

        groupship = Groupship.objects.get(user=self.me, group=group)
        if groupship.status != '0':
            return HttpResponse("No permissions for that!", status=403)

        membership = Membership.objects.get(
        user=user_id, organization=self.me.default)

        if membership.status == '2' and form.cleaned_data['status'] != '2':
            return HttpResponse("User is a contributor! Contributors\
                can only be group guests.", status=403)

        record        = form.save(commit=False)
        record.user   = user
        record.binder = self.me
        record.group  = group
        record.save()

        event = EBindGroupUser.objects.create(organization=self.me.default,
        group=group, user=self.me, peer=user, status=record.status)
        event.dispatch(*group.users.all())

        return redirect('group_app:bind-group-users', group_id=group.id)

class SetGroupshipUser(GuardianView):
    """
    """

    def get(self, request, group_id, user_id):
        user  = User.objects.get(id=user_id, organizations=self.me.default)
        group = self.me.groups.get(id=group_id, organization=self.me.default)
        groupship = Groupship.objects.get(user=user, group=group)
        form      = forms.GroupshipForm(instance=groupship)

        return render(request, 'group_app/set-groupship-user.html', {
        'user': user, 'group': group, 'me': self.me, 'form': form})

    def post(self, request, group_id, user_id):
        user     = User.objects.get(id=user_id, organizations=self.me.default)
        group = self.me.groups.get(id=group_id, organization=self.me.default)

        groupship0 = Groupship.objects.get(user=user, group=group)
        form      = forms.GroupshipForm(request.POST, instance=groupship0)
        if not form.is_valid():
            return render(request, 'group_app/set-groupship-user.html', {
                'user': user, 'group': group, 'form': form})

        if user == group.owner:
            return HttpResponse("Can't change owner status!", status=403)

        groupship1 = Groupship.objects.get(user=self.me, group=group)
        if groupship1.status != '0':
            return HttpResponse("No permissions for that!", status=403)

        membership = Membership.objects.get(
        user=user_id, organization=self.me.default)

        if membership.status == '2' and form.cleaned_data['status'] != '2':
            return HttpResponse("User is a contributor! Contributors\
                can only be group guests.", status=403)

        record = form.save()

        event = EBindGroupUser.objects.create(organization=self.me.default,
        group=group, user=self.me, peer=user, status=record.status)
        event.dispatch(*group.users.all())
        return redirect('group_app:unbind-group-users', group_id=group.id)

class CreateUserGroupship(GuardianView):
    """
    """

    def get(self, request, group_id, user_id):
        user  = User.objects.get(id=user_id, organizations=self.me.default)
        group = self.me.groups.get(id=group_id, organization=self.me.default)
        form  = forms.GroupshipForm()

        return render(request, 'group_app/create-user-groupship.html', {
        'user': user, 'group': group, 'form': form})

    def post(self, request, group_id, user_id):
        user  = User.objects.get(id=user_id, organizations=self.me.default)
        group = self.me.groups.get(id=group_id, organization=self.me.default)

        form = forms.GroupshipForm(request.POST)
        if not form.is_valid():
            return render(request, 'group_app/create-user-groupship.html', {
                'user': user, 'group': group, 'form': form})

        groupship = Groupship.objects.get(user=self.me, group=group)
        if groupship.status != '0':
            return HttpResponse("No permissions for that!", status=403)

        membership = Membership.objects.get(
        user=user_id, organization=self.me.default)

        if membership.status == '2' and form.cleaned_data['status'] != '2':
            return HttpResponse("User is a contributor! Contributors\
                can only be group guests.", status=403)

        record        = form.save(commit=False)
        record.user   = user
        record.binder = self.me
        record.group  = group
        record.save()


        event = EBindGroupUser.objects.create(organization=self.me.default,
        group=group, user=self.me, peer=user, status=record.status)
        event.dispatch(*group.users.all())

        return redirect('group_app:bind-user-groups', user_id=user.id)


class SetUserGroupship(GuardianView):
    """
    """
    def get(self, request, group_id, user_id):
        user  = User.objects.get(id=user_id, organizations=self.me.default)
        group = self.me.groups.get(id=group_id, organization=self.me.default)
        groupship = Groupship.objects.get(user=user, group=group)
        form      = forms.GroupshipForm(instance=groupship)

        return render(request, 'group_app/set-user-groupship.html', {
        'user': user, 'group': group, 'me': self.me, 'form': form})

    def post(self, request, group_id, user_id):
        user  = User.objects.get(id=user_id, organizations=self.me.default)
        group = self.me.groups.get(id=group_id, organization=self.me.default)

        groupship = Groupship.objects.get(user=user, group=group)
        form      = forms.GroupshipForm(request.POST, instance=groupship)
        if not form.is_valid():
            return render(request, 'group_app/set-user-groupship.html', {
                'user': user, 'group': group, 'form': form})

        if user == group.owner:
            return HttpResponse("Can't change owner status!", status=403)

        groupship = Groupship.objects.get(user=self.me, group=group)
        if groupship.status != '0':
            return HttpResponse("No permissions for that!", status=403)

        membership = Membership.objects.get(
        user=user_id, organization=self.me.default)

        if membership.status == '2' and form.cleaned_data['status'] != '2':
            return HttpResponse("User is a contributor! Contributors\
                can only be group guests.", status=403)

        record=form.save()

        event = EBindGroupUser.objects.create(organization=self.me.default,
        group=group, user=self.me, peer=user, status=record.status)
        event.dispatch(*group.users.all())
        return redirect('group_app:unbind-user-groups', user_id=user.id)

class DeleteGroupshipUser(GuardianView):
    """
    """

    def get(self, request, group_id, user_id):
        user = User.objects.get(id=user_id, organizations=self.me.default)
        group  = self.me.groups.get(id=group_id, organization=self.me.default)

        groupship = Groupship.objects.get(user=user, group=group)

        return render(request, 'group_app/delete-groupship-user.html', {
        'user': user, 'group': group})

    def post(self, request, group_id, user_id):
        user     = User.objects.get(id=user_id, organizations=self.me.default)
        group = self.me.groups.get(id=group_id, organization=self.me.default)

        if user == group.owner:
            return HttpResponse("Can't change owner status!", status=403)

        groupship0 = Groupship.objects.get(user=user, group=group)
        groupship1 = Groupship.objects.get(user=self.me, group=group)
        if groupship1.status != '0':
            return HttpResponse("No permissions for that!", status=403)

        event = EUnbindGroupUser.objects.create(organization=self.me.default,
        group=group, user=self.me, peer=user)
        event.dispatch(*group.users.all())

        groupship0.delete()
        return redirect('group_app:unbind-group-users', group_id=group.id)

class DeleteUserGroupship(GuardianView):
    """
    """

    def get(self, request, group_id, user_id):
        user = User.objects.get(id=user_id, organizations=self.me.default)
        group  = self.me.groups.get(id=group_id, organization=self.me.default)

        groupship = Groupship.objects.get(user=user, group=group)

        return render(request, 'group_app/delete-user-groupship.html', {
        'user': user, 'group': group})

    def post(self, request, group_id, user_id):
        user     = User.objects.get(id=user_id, organizations=self.me.default)
        group = self.me.groups.get(id=group_id, organization=self.me.default)

        if user == group.owner:
            return HttpResponse("Can't change owner status!", status=403)

        groupship0 = Groupship.objects.get(user=user, group=group)
        groupship1 = Groupship.objects.get(user=self.me, group=group)
        if groupship1.status != '0':
            return HttpResponse("No permissions for that!", status=403)

        event = EUnbindGroupUser.objects.create(organization=self.me.default,
        group=group, user=self.me, peer=user)
        event.dispatch(*group.users.all())

        groupship0.delete()
        return redirect('group_app:unbind-user-groups', user_id=user.id)


class JoinPublicGroup(GuardianView):
    """
    """

    def post(self, request, group_id):
        group = models.Group.objects.get(id=group_id, organization=self.me.default)
        organization = Organization.objects.get(id=organization_id)

        Groupship.objects.create(user=self.me, status='2',
        organization=organization, group=group, binder=self.me)

        event = EBindGroupUser.objects.create(organization=self.me.default,
        group=group, user=self.me, peer=self.me, status='2')
        event.dispatch(*group.users.all())

        return redirect('core_app:index')

class LeaveGroup(GuardianView):
    """
    """
    def get(self, request, group_id):
        group = self.me.groups.get(id=group_id, organization=self.me.default)

        return render(request, 'group_app/leave-group.html', {'group': group})

    def post(self, request, group_id):
        group = self.me.groups.get(id=group_id, organization=self.me.default)

        if group.owner == self.me: 
            return HttpResponse("Owner can't leave the group!", status=403)

        groupship = Groupship.objects.get(user=self.me, group=group)
        groupship.delete()

        event = EUnbindGroupUser.objects.create(organization=self.me.default,
        group=group, user=self.me, peer=self.me)
        event.dispatch(*group.users.all())

        return redirect('core_app:list-nodes')










