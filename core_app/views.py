from core_app.models import Organization, User, UserTagship, Membership,\
UserFilter, Tag, EDeleteTag, ECreateTag, EUnbindTagUser, EBindTagUser, \
Invite, EInviteUser, EJoinOrganization,  Clipboard, Event, EShout, \
EUpdateOrganization, ERemoveOrganizationUser, Node, NodeFilter, \
EventFilter, EDisabledAccount
from core_app.sqlikes import SqUser, SqTag
from cash_app.models import Period
from django.core.paginator import Paginator, EmptyPage
from django.utils.dateparse import parse_datetime
from card_app.models import Card, CardSearch
from django.shortcuts import render, redirect
from slock.forms import UpdatePasswordForm
from core_app.forms import SignupForm
from board_app.models import Board, Boardship
from group_app.models import Group, Groupship
from django.views.generic import View
from django.core.mail import send_mail
from django.http import HttpResponse
from post_app.models import Post
from django.db.models import Q
from datetime import date, timedelta
from jscroll.wrappers import JScroll
from django.urls import reverse
from django.conf import settings
from traceback import print_exc
from itertools import chain
import slock.views
from . import models
from . import forms
import random
import json
import pytz

# Create your views here.

class AuthenticatedView(slock.views.AuthenticatedView):
    """
    A shorthand to save the logged user instance and avoid having
    to instantiate it again all over the code.
    """

    def on_auth(self, request, *args, **kwargs):
        # Save the user instance to avoid prolixity when checking
        # for permissions. I should have done it before.
        self.me = User.objects.get(id=self.user_id)

class GuardianView(AuthenticatedView):
    def delegate(self, request, *args, **kwargs):
        if not self.me.default:
            return HttpResponse('No default organization,\
                restart the UI!', status=403)

        # Allow just the owner of the account to perform operations.
        # I can perform actions if i'm the owner and it is disabled.
        not_owner = self.me != self.me.default.owner

        if not self.me.default.owner.enabled and not_owner:
            return HttpResponse("Disabled organization \
                account!", status=403)

        return super(GuardianView, self).delegate(
            request, *args, **kwargs)

class Index(AuthenticatedView):
    """
    """

    def get(self, request):
        if hasattr(self.me, 'register_process'):
            return render(request, 
                'site_app/confirm-email.html', {'user': self.me})

        organizations = self.me.organizations.all()
        if not organizations.exists():
            return redirect('core_app:no-organization')

        if not self.me.default:
            return redirect('core_app:no-default')

        if not self.me.default.owner.enabled:
            if self.me.default.owner != self.me:
                return redirect('core_app:disabled-account')

        if not request.session.get('django_timezone'):
            return redirect('core_app:set-timezone')

        organizations = organizations.exclude(id=self.me.default.id)
        return render(request, 'core_app/index.html', {'user': self.me, 
        'default': self.me.default, 'organization': self.me.default, 
        'organizations': organizations, 'settings': settings})

class ResendEmailConfirmation(AuthenticatedView):
    """
    """

    def get(self, request):
        # Just generates another token link
        # but the record remains with the same id.
        self.me.register_process.save()
        return render(request, 
            'site_app/confirm-email.html', {'user': self.me})

class SelectOrganization(AuthenticatedView):
    def get(self, request):
        organizations = self.me.organizations.all()

        return render(request, 'core_app/select-organization.html', 
        {'user': self.me, 'organizations': organizations})

class DisabledAccount(AuthenticatedView):
    def get(self, request):
        return render(request, 'core_app/disabled-account.html', 
        {'user': self.me})

class NoDefault(AuthenticatedView):
    def get(self, request):
        return render(request, 'core_app/no-default.html', 
        {'user': self.me})

class SwitchOrganization(AuthenticatedView):
    def get(self, request, organization_id):
        self.me.default = Organization.objects.get(id=organization_id)
        self.me.save()
        self.me.reload_ui()
        # return HttpResponse(status=200)
        return redirect('core_app:index')

class UpdateUserInformation(GuardianView):
    def get(self, request):
        form = forms.UserForm(instance=self.me)

        return render(request, 'core_app/update-user-information.html', 
        {'user': self.me, 'form': form})

    def post(self, request):
        form = forms.UserForm(request.POST, request.FILES, instance=self.me)

        if not form.is_valid():
            return render(request, 
                'core_app/update-user-information.html', 
                    {'user': self.me, 'form': form}, status=400)

        form.save()
        return HttpResponse(status=200)

class CreateOrganization(AuthenticatedView):
    """
    """

    def get(self, request):
        form = forms.OrganizationForm()
        return render(request, 'core_app/create-organization.html', 
        {'form':form, 'user': self.me})

    def post(self, request):
        form = forms.OrganizationForm(request.POST, me=self.me)

        if not form.is_valid():
            return render(request, 'core_app/create-organization.html',
                        {'form': form, 'user': self.me}, status=400)

        organization       = form.save(commit = False)
        organization.owner = self.me
        organization.save()

        # organization = Organization.objects.create(
        # name=form.cleaned_data['name'], owner=self.me) 

        Membership.objects.create(user=self.me, status='0',
        organization=organization, inviter=self.me)

        # Redirect the user so the ui will be reloaded over all tabs.
        return redirect('core_app:switch-organization', 
            organization_id=organization.id)

class NoOrganization(AuthenticatedView):
    """
    """

    def get(self, request):
        form = forms.OrganizationForm()
        return render(request, 'core_app/no-organization.html', 
        {'form':form, 'user': self.me})

    def post(self, request):
        form = forms.OrganizationForm(request.POST, me=self.me)

        if not form.is_valid():
            return render(request, 'core_app/no-organization.html',
                        {'form': form, 'user': self.me}, status=400)

        organization       = form.save(commit = False)
        organization.owner = self.me
        organization.save()

        # organization = Organization.objects.create(
        # name=form.cleaned_data['name'], owner=self.me) 

        Membership.objects.create(user=self.me, status='0',
        organization=organization, inviter=self.me)

        self.me.default = organization
        self.me.save()
        return redirect('core_app:index')

class UpdateOrganization(GuardianView):
    def get(self, request):
        link = '%s%s' % (settings.LOCAL_ADDR, 
        reverse('core_app:join-from-link', kwargs={
        'organization_id': self.me.default.id}))

        return render(request, 
        'core_app/update-organization.html',{'organization': self.me.default, 
        'form': forms.OrganizationForm(instance=self.me.default), 'link': link})

    def post(self, request):
        if not self.me.default.owner == self.me:
            return HttpResponse('Just owner can \
               update the organization!', status=403)

        form = forms.OrganizationForm(
            request.POST, instance=self.me.default, me=self.me)

        if not form.is_valid():
            return render(request, 'core_app/update-organization.html',
                {'organization': self.me, 'form': form}, status=400)

        form.save()
        event = EUpdateOrganization.objects.create(
        organization=self.me.default, user=self.me)
        event.dispatch(*self.me.default.users.all())

        return redirect('core_app:index')

class DeleteOrganization(GuardianView):
    def get(self, request):
        form = forms.ConfirmOrganizationDeletionForm()

        return render(request, 
            'core_app/delete-organization.html', 
                {'organization': self.me.default, 'form': form})

    def post(self, request):
        if not self.me.default.owner == self.me:
            return HttpResponse('Just owner can \
                    delete the organization!', status=403)

        form = forms.ConfirmOrganizationDeletionForm(request.POST, 
        confirm_token=self.me.default.name)

        if not form.is_valid():
            return render(request, 'core_app/delete-organization.html', 
                {'organization': self.me.default, 'form': form}, status=400)

        self.me.default.delete()
        return redirect('core_app:index')

class ListUsers(GuardianView):
    def get(self, request):
        filter, _ = UserFilter.objects.get_or_create(
        user=self.me, organization=self.me.default)

        users = self.me.default.users.all()
        total = users.count()

        sqlike = SqUser()
        sqlike.feed(filter.pattern)

        users = sqlike.run(users)
        count = users.count()
        form  = forms.UserFilterForm(instance=filter)

        return render(request, 'core_app/list-users.html', 
        {'users': users, 'owner': self.me.default.owner, 'total': total, 
        'form': form, 'count': count, 'organization': self.me.default})

    def post(self, request):
        filter, _= UserFilter.objects.get_or_create(
        user=self.me, organization=self.me.default)

        users  = self.me.default.users.all()
        total  = users.count()
        sqlike = SqUser()

        form  = forms.UserFilterForm(request.POST, sqlike=sqlike, instance=filter)

        if not form.is_valid():
            return render(request, 'core_app/list-users.html', 
                {'count': 0, 'owner': self.me.default.owner, 
                    'total': total, 'form': form,
                        'organization': self.me.default}, status=400)
  
        form.save()

        users = sqlike.run(users)
        count = users.count()

        return render(request, 'core_app/list-users.html', 
        {'users': users, 'owner': self.me.default.owner, 'count': count,
        'total': total, 'form': form, 'organization': self.me.default})

class ListEvents(GuardianView):
    """
    """

    def get(self, request):
        events = self.me.events.filter(organization=self.me.default)
        count = events.count()
        events = events.values('html', 'id').order_by('-created')

        elems = JScroll(self.me.id, 'core_app/list-events-scroll.html', events)

        return render(request, 'core_app/list-events.html', 
        {'elems': elems.as_div(), 'user': self.me, 
         'organization': self.me.default, 'count': count})

class ListTags(GuardianView):
    def get(self, request):
        tags = self.me.default.tags.all()
        form = forms.TagSearchForm()
        total = tags.count()
        return render(request, 'core_app/list-tags.html', 
        {'tags': tags, 'form': form, 'user': self.me, 'total': total,
        'count': total, 'organization': self.me.default})

    def post(self, request):
        sqlike = SqTag()
        form   = forms.TagSearchForm(request.POST, sqlike=sqlike)
        tags   = self.me.default.tags.all()
        total  = tags.count()
    
        if not form.is_valid():
            return render(request, 'core_app/list-tags.html', 
                {'tags': tags, 'form': form, 'user': self.me, 'total': total,
                    'count': 0, 'organization': self.me.default})

        tags  = sqlike.run(tags)
        count = tags.count()

        return render(request, 'core_app/list-tags.html', 
        {'tags': tags, 'form': form, 'user': self.me, 
        'organization': self.me.default, 'total': total, 'count': count})

class DeleteTag(GuardianView):
    """
    The view can be performed only by users who belong
    to the tag organization. 

    If an user attempts to call this view with a tag id that doesn't
    belong to his default organization he will get an exception thrown
    then an error message.
    """

    def post(self, request, tag_id):
        query = Q(user=self.me, organization=self.me.default)
        membership = Membership.objects.get(query)

        ERROR1 = "Contributors can't delete tags!"
        if membership.status == '2':
            return HttpResponse(ERROR1, status=403)

        # Make sure the tag belongs to my default orgnization.
        tag   = Tag.objects.get(id=tag_id, organization=self.me.default)
        event = EDeleteTag.objects.create(
        organization=self.me.default, user=self.me, tag_name=tag.name)
        tag.delete()

        users = self.me.default.users.all()
        event.dispatch(*users)
        return ListTags.as_view()(request)

class CreateTag(GuardianView):
    def get(self, request):
        form = forms.TagForm()

        return render(request, 'core_app/create-tag.html', 
        {'form':form})

    def post(self, request):
        form      = forms.TagForm(request.POST)
        is_valid  = form.is_valid() 
        name      = form.cleaned_data.get('name')
        is_unique = self.me.default.tags.filter(name__iexact=name).exists()

        ERROR0 = 'There already exist a tag with this name'
        if is_unique: form.add_error('name', ERROR0)

        query = Q(user=self.me, organization=self.me.default)
        membership = Membership.objects.get(query)

        ERROR1 = "Contributors can't create tags!"
        if membership.status == '2':
            return HttpResponse(ERROR1, status=403)

        if not is_valid or is_unique:
            return render(request, 'core_app/create-tag.html',
                        {'form': form, 'user': self.me}, status=400)

        record = form.save(commit=False)
        record.organization = self.me.default
        record.save()

        event = ECreateTag.objects.create(
        organization=self.me.default, user=self.me, tag=record)

        users = self.me.default.users.all()
        event.dispatch(*users)

        return redirect('core_app:list-tags')

class InviteOrganizationUser(GuardianView):
    def get(self, request):
        return render(request, 'core_app/invite-organization-user.html', 
        {'form': forms.InviteForm(), 'user': self.me})

    def post(self, request):
        membership = Membership.objects.get(
        user=self.me, organization=self.me.default)

        # It should return 403 while the checkings regarding
        # values should be http 400.
        if membership.status != '0':
            return HttpResponse("Only staffs can send invites!", status=403)

        form = forms.InviteForm(request.POST, me=self.me)
        if not form.is_valid():
            return render(request, 'core_app/invite-organization-user.html',
                  {'form': form, 'user': self.me}, status=400)

        record = form.save()
        record.send_email()

        event = EInviteUser.objects.create(
        organization=self.me.default, user=self.me, peer=record.user)
        event.dispatch(*self.me.default.users.all())

        return redirect('core_app:list-users')

class ResendInvite(GuardianView):
    def get(self, request, invite_id):
        invite = Invite.objects.get(id=invite_id)
        invite.send_email()

        return redirect('core_app:list-users')

class JoinOrganization(View):
    def get(self, request, organization_id, token):
        invite = Invite.objects.get(token=token)

        if not invite.user.enabled:
            return redirect('core_app:signup-from-invite', 
                organization_id=organization_id, token=token)

        organization = Organization.objects.get(id=organization_id)

        # Create the membership with the same status of the invite.
        Membership.objects.create(user=invite.user, status=invite.status,
        organization=invite.organization, inviter=invite.peer)

        invite.user.default = organization
        invite.user.save()

        # Add the user to the public boards.
        boards = organization.boards.filter(public=True)
        boards = boards.only('id', 'owner')

        boardships = (Boardship(member=invite.user, board=ind, 
        binder=ind.owner, status='2') for ind in boards)
        Boardship.objects.bulk_create(boardships)

        # Add the user to the public groups.
        groups = organization.groups.filter(public=True)
        groups = groups.only('id', 'owner')

        groupships = (Groupship(user=invite.user, group=ind, 
        binder=ind.owner, status='2') for ind in groups)

        Groupship.objects.bulk_create(groupships)

        # The user should be Arcamens Service(thinking about it later).
        event = EJoinOrganization.objects.create(organization=organization, 
        peer=invite.user, user=invite.user)
        event.dispatch(*organization.users.all())

        # Authenticate the user.
        request.session['user_id'] = invite.user.id

        # validates the invite.
        invite.delete()

        # Maybe just redirect the user to a page telling he joined the org.
        return redirect('core_app:index')

class SignupFromInvite(View):
    def get(self, request, organization_id, token):
        invite = Invite.objects.get(    
        organization__id=organization_id, token=token)

        form = SignupForm(instance=invite.user)
        return render(request, 'core_app/signup-from-invite.html', 
        {'form': form, 'organization': invite.organization, 'token': token})

    def post(self, request, organization_id, token):
        invite = Invite.objects.get(    
        organization__id=organization_id, token=token)
        form = SignupForm(request.POST, request.FILES, instance=invite.user)

        if not form.is_valid():
            return render(request, 'core_app/signup-from-invite.html', 
                {'form': form, 'organization': invite.organization, 
                    'token': token}, status=400)

        record = form.save(commit=False)
        record.enabled = True
        record.save()

        # Create the free period record for the user.
        period = Period.objects.create(paid=False, total=0, user=record)

        return redirect('core_app:join-organization', 
        organization_id=organization_id, token=token)

class ListClipboard(GuardianView):
    def get(self, request):
        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)

        cards = clipboard.cards.all()
        lists = clipboard.lists.all()
        posts = clipboard.posts.all()

        total = cards.count() + lists.count() + posts.count()

        return render(request, 'core_app/list-clipboard.html', 
        {'user': self.me, 'cards': cards , 'posts': posts, 
        'lists': lists, 'total': total})

class SeenEvent(GuardianView):
    def get(self, request, event_id):
        # Make sure the event is related to the user default organization
        # otherwise it entails in security risk. The user could run a script
        # that allows him to view all existing events through list-logs view.
        # It happens because after event.seen(self.me) then the event is put
        # in user.signers which is listed in list-logs.
        event = self.me.events.get(id=event_id, organization=self.me.default)
        event.seen(self.me)
        return redirect('core_app:list-events')

class ListLogs(GuardianView):
    """
    """

    def get(self, request):
        filter, _= EventFilter.objects.get_or_create(user=self.me, 
        organization=self.me.default)

        form   = forms.EventFilterForm(instance=filter)

        events = self.me.seen_events.filter(organization=self.me.default)
        total = events.count()

        events = events.filter(created__lt=filter.end + timedelta(days=1),
        created__gte=filter.start)

        # events = events.filter(created__date__lte=filter.end,
        # created__date__gte=filter.start)

        count  = events.count()
        events = events.values('html').order_by('-created')

        events = JScroll(self.me.id, 'core_app/list-logs-scroll.html', events)

        return render(request, 'core_app/list-logs.html', 
        {'user': self.me, 'form': form, 'events':events.as_div(), 
        'events': events.as_div(), 'count': count, 'total': total, 
        'organization': self.me.default})

    def post(self, request):
        filter = EventFilter.objects.get(user=self.me, 
        organization=self.me.default)

        form   = forms.EventFilterForm(request.POST, instance=filter)
        events = self.me.seen_events.filter(organization=self.me.default)
        total  = events.count()

        if not form.is_valid():
            return render(request, 'core_app/list-logs.html', 
                {'user': self.me, 'form': form, 'count': 0, 'total': total,
                     'organization': self.me.default})
        form.save()

        events = events.filter(created__lt=filter.end + timedelta(days=1),
        created__gte=filter.start)

        # events = events.filter(created__date__lte=filter.end,
        # created__date__gte=filter.start)

        count  = events.count()
        events = events.values('html').order_by('-created')
        events = JScroll(self.me.id, 'core_app/list-logs-scroll.html', events)

        return render(request, 'core_app/list-logs.html', 
        {'user': self.me, 'form': form, 'events':events.as_div(), 
        'count': count,'organization': self.me.default, 'total': total})

class AllSeen(GuardianView):
    """
    Secured.
    """

    def get(self, request):
        events = self.me.events.filter(organization=self.me.default)

        for ind in events:
            ind.seen(self.me)
        return redirect('core_app:list-events')

class ConfirmClipboardDeletion(GuardianView):
    def get(self, request):
        return render(request, 'core_app/confirm-clipboard-deletion.html')

class DeleteAllClipboard(GuardianView):
    def get(self, request):
        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)

        cards = clipboard.cards.all()
        lists = clipboard.lists.all()
        posts = clipboard.posts.all()
        cards.delete()
        lists.delete()
        posts.delete()

        return redirect('core_app:list-clipboard')

class Shout(GuardianView):
    def get(self, request):
        form = forms.ShoutForm()

        return render(request, 'core_app/shout.html', 
        {'form': form, 'me': self.me})

    def post(self, request):
        form = forms.ShoutForm(request.POST)

        if not form.is_valid():
            return render(request, 'core_app/list-users.html', 
                {'form': form, 'me': self.me}, status=400)

        event = EShout.objects.create(organization=self.me.default, 
        user=self.me, msg=form.cleaned_data['msg'])

        users = self.me.default.users.all()
        event.dispatch(*users)

        return redirect('core_app:list-events')

class UpdatePassword(GuardianView):
    def get(self, request):
        form = UpdatePasswordForm()

        return render(request, 
            'core_app/update-password.html', 
                {'user': self.me, 'form': form})

    def post(self, request):
        form = UpdatePasswordForm(request.POST, instance=self.me)

        if not form.is_valid():
            return render(request, 'core_app/update-password.html', 
                    {'user': self.me, 'form': form}, status=400)
    
        form.save()

        return redirect('core_app:update-user-information')

class RemoveOrganizationUser(GuardianView):
    """
    Secured.
    """

    def get(self, request, user_id):
        # We need to make sure the user who is being removed belongs
        # to our default organization otherwise it may allow misbehaviors.
        user = User.objects.get(id=user_id, organizations=self.me.default)

        form = forms.RemoveUserForm()
        groups = user.owned_groups.filter(organization=self.me.default)
        boards = user.owned_boards.filter(organization=self.me.default)

        return render(request, 'core_app/remove-organization-user.html', 
        {'user': user, 'form': form, 'groups': groups, 'boards': boards})

    def post(self, request, user_id):
        user = User.objects.get(id=user_id, organizations=self.me.default)

        if self.me.default.owner == user:
            return HttpResponse('No permission for that!', status=403)

        membership0 = Membership.objects.get(user=user, 
        organization=self.me.default)

        membership1 = Membership.objects.get(user=self.me, 
        organization=self.me.default)

        if membership1.status != '0':
            return HttpResponse('No permission for that!', status=403)

        form = forms.RemoveUserForm(request.POST)
        if not form.is_valid():
            return render(request, 
                'core_app/remove-organization-user.html', 
                    {'user': user, 'form': form})

        # First remove me from all boards/groups the user owns.
        boardships = Boardship.objects.filter(member=self.me, 
        board__owner=user, board__organization=self.me.default)
        boardships.delete()

        groupships = Groupship.objects.filter(user=self.me, 
        group__owner=user, group__organization=self.me.default)
        groupships.delete()

        # Turn me admin of all boards/groups that the user owns and i'm a member.
        # The binder is changed too.
        boardships = Boardship.objects.filter(member=user,
        board__owner=user, board__organization=self.me.default)
        boardships.update(member=self.me, binder=self.me, status='0')

        boards = user.owned_boards.filter(organization=self.me.default)
        boards.update(owner=self.me)

        groupships = Groupship.objects.filter(user=user,
        group__owner=user, group__organization=self.me.default)
        groupships.update(user=self.me, binder=self.me, status='0')

        groups = user.owned_groups.filter(organization=self.me.default)
        groups.update(owner=self.me)

        # Remove the user from boards/groups he is not an owner.
        Groupship.objects.filter(Q(user=user), 
        group__organization=self.me.default).delete()

        Boardship.objects.filter(Q(member=user), 
        board__organization=self.me.default).delete()

        clipboard0, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)

        clipboard1, _ = Clipboard.objects.get_or_create(
        user=user, organization=self.me.default)

        clipboard0.posts.add(*clipboard1.posts.all())
        clipboard0.cards.add(*clipboard1.cards.all())
        clipboard0.lists.add(*clipboard1.lists.all())

        clipboard1.posts.clear()
        clipboard1.cards.clear()
        clipboard1.lists.clear()

        user.user_membership.filter(organization=self.me.default).delete()
        user.default = None
        user.save()

        # The user tasks will remain so the staff can just reassign it
        # to other user.
        event = ERemoveOrganizationUser.objects.create(
        organization=self.me.default, user=self.me, peer=user, 
        reason=form.cleaned_data['reason'])
        event.dispatch(*self.me.default.users.all())

        msg = 'You no longer belong to %s!\n\n%s' % (self.me.default.name, 
        form.cleaned_data['reason'])

        send_mail('%s notification!' % self.me.default.name, msg, 
        'noreply@arcamens.com', [user.email], fail_silently=False)

        # Should restart the user UI now (TO IMPLEMENT).
        return redirect('core_app:list-users')

class ListInvites(GuardianView):
    def get(self, request):
        invites = self.me.default.invites.all()

        return render(request, 'core_app/list-invites.html', 
        {'organization': self.me.default, 'invites': invites})

class CancelInvite(GuardianView):
    def get(self, request, invite_id):
        # We need to make sure the invite belongs to our self.me.default
        # organization otherwise a hacker can just cancel all invites
        # by running a simple script.
        invite = Invite.objects.get(id=invite_id, organization=self.me.default)

        # If there is no more invites sent to this user
        # and his default org is null then he is not an existing
        # user.
        invite.delete()

        # If there is no more invites just delete the user.
        if not invite.user.invites.exists() and not invite.user.enabled:
            invite.user.delete()
        return redirect('core_app:list-invites')

class ListNodes(GuardianView):
    """
    """

    def get(self, request):
        nodes = Node.objects.filter(Q(board__organization=self.me.default) 
        | Q(group__organization=self.me.default)) 

        nodes = nodes.filter(Q(board__members=self.me) | Q(group__users=self.me))
        nodes = nodes.distinct().order_by('-indexer')
        total = nodes.count()

        boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        listpins  = self.me.listpin_set.filter(organization=self.me.default)
        cardpins  = self.me.cardpin_set.filter(organization=self.me.default)
        grouppins = self.me.grouppin_set.filter(organization=self.me.default)
        postpins  = self.me.postpin_set.filter(organization=self.me.default)

        filter, _ = NodeFilter.objects.get_or_create(user=self.me, 
        organization=self.me.default)

        q0 = Q(board__name__icontains=filter.pattern)
        q1 = Q(board__description__icontains=filter.pattern)
        q2 = Q(group__name__icontains=filter.pattern)
        q3 = Q(group__description__icontains=filter.pattern)

        query = q0 | q1 | q2 | q3        
        nodes = nodes.filter(query) if filter.status else nodes
        count = nodes.count()

        return render(request, 'core_app/list-nodes.html', 
        {'nodes': nodes, 'boardpins': boardpins, 'listpins': listpins, 
        'user': self.me, 'total': total, 'count': count, 
        'organization': self.me.default, 'filter': filter, 
        'cardpins': cardpins, 'grouppins': grouppins, 'postpins': postpins})

class SetupNodeFilter(GuardianView):
    def get(self, request):
        filter = NodeFilter.objects.get(user=self.me, 
        organization=self.me.default)

        return render(request, 'core_app/setup-node-filter.html', 
        {'form': forms.NodeFilterForm(instance=filter), 
        'organization': self.me.default})

    def post(self, request):
        record = NodeFilter.objects.get(user=self.me, 
        organization=self.me.default)
        form = forms.NodeFilterForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'core_app/setup-node-filter.html',
                   {'node': record, 'form': form, 
                        'organization': self.me.default}, status=400)
        form.save()
        return redirect('core_app:list-nodes')

class FileDownload(GuardianView):
    def get_file_url(self, file):
        LIMIT = settings.PAID_DOWNLOAD_LIMIT\
        if self.me.paid else settings.FREE_DOWNLOAD_LIMIT

        if self.me.c_download > LIMIT:
            return HttpResponse('Download limit exceeded!', status=400)
        self.me.c_download = self.me.c_download + file.size
        self.me.save()
        return redirect(file.url)

class SetTimezone(GuardianView):
    def get(self, request):
        return render(request, 'core_app/set-timezone.html', 
            {'timezones': pytz.common_timezones})

    def post(self, request):
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('core_app:index')

class SetMembership(GuardianView):
    """
    """
    def get(self, request, organization_id, user_id):
        user = User.objects.get(id=user_id, organizations=self.me.default)
        membership = Membership.objects.get(user=user, organization=self.me.default)
        form = forms.MembershipForm(instance=membership)

        return render(request, 'core_app/set-membership.html', {
        'user': user, 'organization': self.me.default, 'form': form})

    def post(self, request, organization_id, user_id):
        user = User.objects.get(id=user_id, organizations=self.me.default)
        membership0 = Membership.objects.get(user=user, organization=self.me.default)
        form = forms.MembershipForm(request.POST, instance=membership0, me=self.me)

        membership1 = Membership.objects.get(
        user=self.me, organization=self.me.default)

        error0 = "Can't change organization owner status"
        if self.me.default.owner == user:
            return HttpResponse(error0, status=403)

        error1 = "Only staffs can change member status!"
        if membership1.status != '0':
            return HttpResponse(error1, status=403)

        if not form.is_valid():
            return render(request, 'core_app/set-membership.html', 
                {'user': user, 'organization': self.me.default,'form': form})

        form.save()
        return redirect('core_app:list-users')


class ListPublicOrganizations(GuardianView):
    """
    """

    def get(self, request):
        organizations = Organization.objects.filter(public=True)
        organizations = organizations.exclude(users=self.me)
        return render(request, 'core_app/list-public-organizations.html', 
        {'organizations': organizations})

class NotPublicOrganization(GuardianView):
    """
    """

    def get(self, request, organization_id):
        organization = Organization.objects.get(id=organization_id)

        return render(request, 'core_app/not-public-organization.html', 
        {'organization': organization})

class JoinFromLink(GuardianView):
    def get(self, request, organization_id):
        organization = Organization.objects.get(id=organization_id)

        if not organization.public:
            return redirect('core_app:not-public-organization', 
                organization_id= organization.id)

        return render(request, 'core_app/join-from-link.html',
        {'organization': organization, })

class JoinPublicOrganization(GuardianView):
    """
    """

    def post(self, request, organization_id):
        # Make sure i dont belong to the organization.
        organization = Organization.objects.get(~Q(users=self.me), 
                id=organization_id)

        # Check if the organization is public.
        if not organization.public:
            return redirect('core_app:not-public-organization', 
                organization_id= organization.id)

        Membership.objects.create(user=self.me, status='2',
        organization=organization, inviter=self.me)

        self.me.default = organization
        self.me.save()

        # Add the user to the public boards.
        boards = organization.boards.filter(public=True)
        boards = boards.only('id', 'owner')

        boardships = (Boardship(member=self.me, board=ind, 
        binder=ind.owner, status='2') for ind in boards)
        Boardship.objects.bulk_create(boardships)

        # Add the user to the public groups.
        groups = organization.groups.filter(public=True)
        groups = groups.only('id', 'owner')

        groupships = (Groupship(user=self.me, group=ind, 
        binder=ind.owner, status='2') for ind in groups)

        Groupship.objects.bulk_create(groupships)

        event = EJoinOrganization.objects.create(
        organization=organization, peer=self.me, user=self.me)

        event.dispatch(*organization.users.all())
        return redirect('core_app:index')

class UnbindUserTags(GuardianView):
    """
    """

    def get(self, request, user_id):
        user = models.User.objects.get(id=user_id)
        included = user.tags.all()
        total    = included.count() 

        return render(request, 'core_app/unbind-user-tags.html', {
        'included': included, 'user': user, 'organization': self.me.default,
        'form':forms.TagSearchForm(), 'me': self.me, 
        'count': total, 'total': total,})

    def post(self, request, user_id):
        sqlike   = SqTag()
        form     = forms.TagSearchForm(request.POST, sqlike=sqlike)

        user     = models.User.objects.get(id=user_id)
        included = user.tags.all()
        tags     = self.me.default.tags.all()
        total    = included.count() 
        
        if not form.is_valid():
            return render(request, 'core_app/unbind-user-tags.html', 
                {'me': self.me, 'user': user, 'count': 0, 'total': total,
                        'form':form}, status=400)

        included = sqlike.run(included)
        count = included.count() 

        return render(request, 'core_app/unbind-user-tags.html', 
        {'included': included, 'user': user, 'me': self.me, 
        'organization': self.me.default,'form':form, 
        'count': count, 'total': total,})

class BindUserTags(GuardianView):
    """
    The listed tags are supposed to belong to the logged tag default
    organization. It also checks if the tag belongs to the user
    in order to list its tags.
    """

    def get(self, request, user_id):
        user = models.User.objects.get(id=user_id)
        tags = self.me.default.tags.all()

        excluded = tags.exclude(users=user)
        total    = excluded.count()

        return render(request, 'core_app/bind-user-tags.html', 
        {'excluded': excluded, 'user': user, 'me': self.me, 
        'organization': self.me.default,'form':forms.TagSearchForm(), 
        'count': total, 'total': total,})

    def post(self, request, user_id):
        sqlike   = SqTag()
        form     = forms.TagSearchForm(request.POST, sqlike=sqlike)

        user     = models.User.objects.get(id=user_id)
        tags     = self.me.default.tags.all()
        excluded = tags.exclude(users=user)
        total    = excluded.count()
        
        if not form.is_valid():
            return render(request, 'core_app/bind-user-tags.html', 
                {'me': self.me, 'user': user, 'count': 0, 'total': total,
                        'form':form}, status=400)

        excluded = sqlike.run(excluded)
        count    = excluded.count()

        return render(request, 'core_app/bind-user-tags.html', 
        {'excluded': excluded, 'user': user, 'me': self.me, 
        'organization': self.me.default,'form':form, 
        'count': count, 'total': total,})

class CreateUserTagship(GuardianView):
    """
    """

    def get(self, request, user_id, tag_id):
        tag  = Tag.objects.get(id=tag_id, organization=self.me.default)
        user = models.User.objects.get(id=user_id)
        form = forms.UserTagshipForm()

        return render(request, 'core_app/create-user-tagship.html', {
        'tag': tag, 'user': user, 'form': form})

    def post(self, request, user_id, tag_id):
        tag  = Tag.objects.get(id=tag_id, organization=self.me.default)
        user = models.User.objects.get(id=user_id)

        form = forms.UserTagshipForm(request.POST)
        if not form.is_valid():
            return render(request, 'core_app/create-user-tagship.html', {
                'tag': tag, 'user': user, 'form': form})

        record        = form.save(commit=False)
        record.tag   = tag
        record.tagger = self.me
        record.user  = user
        record.save()

        event = EBindTagUser.objects.create(
        organization=self.me.default, peer=user, tag=tag, user=self.me)
        event.dispatch(*self.me.default.users.all())
        event.save()

        return redirect('core_app:bind-user-tags', user_id=user.id)

class DeleteUserTagship(GuardianView):
    def post(self, request, user_id, tag_id):
        tag   = Tag.objects.get(id=tag_id, organization=self.me.default)
        user  = models.User.objects.get(id=user_id)

        event = EUnbindTagUser.objects.create(
        organization=self.me.default, peer=user, tag=tag, user=self.me)
        event.dispatch(*self.me.default.users.all())
        event.save()

        UserTagship.objects.get(user=user, tag=tag).delete()
        return redirect('core_app:unbind-user-tags', user_id=user.id)







