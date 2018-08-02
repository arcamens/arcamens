from core_app.models import Organization, User, \
UserFilter, Tag, EDeleteTag, ECreateTag, EUnbindUserTag, EBindUserTag, \
Invite, EInviteUser, EJoinOrganization,  Clipboard, Event, EShout, \
EUpdateOrganization, ERemoveOrganizationUser, Node, NodeFilter, \
EventFilter, EDisabledAccount
from django.core.paginator import Paginator, EmptyPage
from django.utils.dateparse import parse_datetime
from card_app.models import Card, GlobalCardFilter
from django.shortcuts import render, redirect
from slock.forms import UpdatePasswordForm
from core_app.forms import SignupForm
from django.views.generic import View
from django.core.mail import send_mail
from django.http import HttpResponse
from post_app.models import Post
from django.db.models import Q
from datetime import date
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
        return render(request, 'core_app/index.html', 
        {'user': self.me, 'default': self.me.default, 
        'organization': self.me.default, 'organizations': organizations,
         'settings': settings})

    def set_default_organization(self):
        self.me.default = self.me.organizanitions.first()
        self.me.save()

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
        form = forms.OrganizationForm(request.POST)

        if not form.is_valid():
            return render(request, 'core_ap/create-organization.html',
                        {'form': form, 'user': self.me}, status=400)

        organization = Organization.objects.create(
        name=form.cleaned_data['name'], owner=self.me) 

        self.me.organizations.add(organization)
        organization.admins.add(self.me)

        # self.me.default = organization
        # self.me.save()
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
        form = forms.OrganizationForm(request.POST)

        if not form.is_valid():
            return render(request, 'core_ap/no-organization.html',
                        {'form': form, 'user': self.me}, status=400)

        organization = Organization.objects.create(
        name=form.cleaned_data['name'], owner=self.me) 

        self.me.organizations.add(organization)
        self.me.default = organization
        organization.admins.add(self.me)
        self.me.save()
        return redirect('core_app:index')

class UpdateOrganization(GuardianView):
    def get(self, request):
        return render(request, 
        'core_app/update-organization.html',{'organization': self.me.default, 
        'form': forms.UpdateOrganizationForm(instance=self.me.default)})

    def post(self, request):
        if not self.me.default.owner == self.me:
            return HttpResponse('Just owner can \
               update the organization!', status=403)

        form = forms.UpdateOrganizationForm(
            request.POST, instance=self.me.default)

        if not form.is_valid():
            return render(request, 'core_app/update-organization.html',
                {'organization': self.me, 'form': form}, status=400)

        form.save()
        event = EUpdateOrganization.objects.create(
        organization=self.me.default, user=self.me)
        event.dispatch(*self.me.default.users.all())

        # user.ws_sound(record)

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

        users = User.collect_users(users, filter.pattern)
        count = users.count()

        form  = forms.UserFilterForm(instance=filter)

        return render(request, 'core_app/list-users.html', 
        {'users': users, 'owner': self.me.default.owner, 'total': total, 
        'form': form, 'count': count, 'organization': self.me.default})

    def post(self, request):
        filter, _    = UserFilter.objects.get_or_create(
        user=self.me, organization=self.me.default)

        users = self.me.default.users.all()
        total = users.count()
        sqlike = User.from_sqlike()
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

class ManageUserTags(GuardianView):
    """
    This view workings rely on the logged user default organization.
    So it is already secured by default.
    """

    def get(self, request, user_id):
        # Make sure the user belongs to the user default organization.
        # Otherwise it may arise misbehaviors or security issues.
        user = User.objects.get(id=user_id, organizations=self.me.default)

        # Filter the existing user tags by using my default orgnization.
        included = user.tags.filter(organization=self.me.default)
        excluded = self.me.default.tags.all()
        excluded = excluded.exclude(users=user)
        total    = included.count() + excluded.count()

        return render(request, 'core_app/manage-user-tags.html', 
        {'included': included, 'excluded': excluded, 'user': user, 'me': self.me,
        'form':forms.TagSearchForm(), 'total': total, 'count': total})

    def post(self, request, user_id):
        sqlike = Tag.from_sqlike()
        form = forms.TagSearchForm(request.POST, sqlike=sqlike)

        # Again make sure the user belongs to my default organization.
        user = User.objects.get(id=user_id, organizations=self.me.default)

        included = user.tags.filter(organization=self.me.default)
        excluded = self.me.default.tags.all()
        excluded = excluded.exclude(users=user)
        total    = included.count() + excluded.count()

        if not form.is_valid():
            return render(request, 'core_app/manage-user-tags.html', 
                {'included': included, 'excluded': excluded, 'total': total,
                    'organization': self.me.default, 'user': user, 'count': 0,
                        'form':form, 'me': self.me}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)
        count = included.count() + excluded.count()

        return render(request, 'core_app/manage-user-tags.html', 
        {'included': included, 'excluded': excluded, 'user': user,
        'me': self.me, 'organization': self.me.default, 'total': total, 
        'count': count, 'form':form})

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
        sqlike = Tag.from_sqlike()
        form = forms.TagSearchForm(request.POST, sqlike=sqlike)
        tags = self.me.default.tags.all()

        total = tags.count()
    
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

    def get(self, request, tag_id):
        # Make sure the tag belongs to my default orgnization.
        tag   = Tag.objects.get(id=tag_id, organization=self.me.default)
        event = EDeleteTag.objects.create(
        organization=self.me.default, user=self.me, tag_name=tag.name)
        tag.delete()

        users = self.me.default.users.all()
        event.dispatch(*users)

        return HttpResponse(status=200)

class CreateTag(GuardianView):
    def get(self, request):
        form = forms.TagForm()

        return render(request, 'core_app/create-tag.html', 
        {'form':form})

    def post(self, request):
        form      = forms.TagForm(request.POST)
        is_valid  = form.is_valid() 
        name      = form.cleaned_data.get('name')
        is_unique = self.me.default.tags.filter(name=name).exists()

        if is_unique: form.add_error('name', 
            'There already exist a tag with this name')

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

class UnbindUserTag(GuardianView):
    def get(self, request, user_id, tag_id):
        # Make sure the user belongs to my default organization.
        # This is necessary otherwise he can drop an user_id and tag_id
        # and unbind all tags from all users(hacking).
        user = User.objects.get(id=user_id, organizations=self.me.default)
        tag  = Tag.objects.get(id=tag_id, organization=self.me.default)
        user.tags.remove(tag)
        user.save()

        event = EUnbindUserTag.objects.create(
        organization=self.me.default, user=self.me, peer=user, tag=tag)

        users = self.me.default.users.all()
        event.dispatch(*users)

        return HttpResponse(status=200)

class BindUserTag(GuardianView):
    def get(self, request, user_id, tag_id):
        # Make sure the user/tag belongs are related to my default organization.
        user = User.objects.get(id=user_id, organizations=self.me.default)
        tag  = Tag.objects.get(id=tag_id, organization=self.me.default)

        user.tags.add(tag)
        user.save()

        event = EBindUserTag.objects.create(
        organization=self.me.default, user=self.me, peer=user, tag=tag)
        users = self.me.default.users.all()
        event.dispatch(*users)

        return HttpResponse(status=200)

class InviteOrganizationUser(GuardianView):
    def get(self, request):
        return render(request, 'core_app/invite-organization-user.html', 
        {'form': forms.OrganizationInviteForm(), 'user': self.me})

    def post(self, request):
        # I can send invite just if i'm admin of the organization.
        me_admin = self.me.default.admins.filter(id=self.me.id).exists()
        msg0     = "Only admins can do that!"

        if not me_admin:
            return HttpResponse(msg0, status=403)

        msg1 = 'Max users limit was arrived!\
        You need to upgrade your plan!'

        # Calculate the amount of users + invites
        # the actual default organization owner has.
        users = User.objects.filter(
        organizations__owner__id=self.me.default.owner.id)

        users   = users.distinct()
        n_users = users.count()

        invites = Invite.objects.filter(
            organization__owner__id=self.me.default.owner.id)

        # Not sure if necessary at all.
        invites = invites.distinct()
        n_invites = invites.count()
        
        max_users = n_users + n_invites
        if self.me.default.owner.max_users <= max_users:
            return HttpResponse(msg1, status=403)

        form = forms.OrganizationInviteForm(request.POST)
        if not form.is_valid():
            return render(request, 'core_app/invite-organization-user.html',
                  {'form': form, 'user': self.me}, status=400)

        email = form.cleaned_data['email']
        # Create the user anyway, but make it disabled
        # the user need to fill information first.
        user, _  = User.objects.get_or_create(email=email)

        # If the user is not a member then notify with an error.
        is_member = user.organizations.filter(id=self.me.default.id).exists()
        msg2      = "The user is already a member!"
        if is_member:
            return HttpResponse(msg2, status=403)

        # If there is already an invite just tell him it was sent.
        is_sent = user.invites.filter(organization=self.me.default).exists()
        msg3 = "The user was already invited!"

        if is_sent:
            return HttpResponse(msg3, status=403)

        invite = Invite.objects.create(
            organization=self.me.default, peer=self.me, user=user)

        invite.send_email()

        event = EInviteUser.objects.create(
        organization=self.me.default, user=self.me, peer=user)
        event.dispatch(*self.me.default.users.all())

        return redirect('core_app:list-users')

class ResendInvite(GuardianView):
    def get(self, request, invite_id):
        if not self.me.default.admins.filter(id=self.me.id).exists():
            return HttpResponse("Only admins can do that!", status=403)

        invite = Invite.objects.get(id=invite_id)
        invite.send_email()

        return redirect('core_app:list-users')

        # return render(request, 
            # 'core_app/resend-invite.html', {'invite': invite})

class JoinOrganization(View):
    def get(self, request, organization_id, token):
        # need some kind of token to be sent
        # for validating the invitation.

        invite = Invite.objects.get(token=token)

        if not invite.user.enabled:
            return redirect('core_app:signup-from-invite', 
                organization_id=organization_id, token=token)

        # Delete all the invites for this user.
        organization = Organization.objects.get(id=organization_id)

        invite.user.organizations.add(organization)
        invite.user.default = organization
        invite.user.save()
    
        # Create the free period record for the user.
        period = Period.objects.create(paid=False, total=0, user=invite.user)

        # The user should be Arcamens Service(thinking about it later).
        event = EJoinOrganization.objects.create(organization=organization, 
        peer=invite.user, user=invite.user)
        event.dispatch(*organization.users.all())

        organization.set_open_boards(invite.user)
        organization.set_open_groups(invite.user)

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

        events = events.filter(created__lte=filter.end,
        created__gte=filter.start)

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

        events = events.filter(created__lte=filter.end,
        created__gte=filter.start)

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
        form = forms.RemoveUserForm(request.POST)
        user = User.objects.get(id=user_id, organizations=self.me.default)

        # If i'm the owner then i can't remove myself.
        # I should delete the organization.

        if self.me.default.owner == user:
            return HttpResponse("You can't remove the owner!", status=403)

        is_admin = self.me.default.admins.filter(id=user.id).exists()
        me_owner = self.me.default.owner == self.me
        me_admin = self.me.default.admins.filter(id=self.me.id).exists()

        # If the user is an admin and i'm not the owner.
        if is_admin and not me_owner:
            return HttpResponse("Only owner can do that!", status=403)

        # If i'm not admin and the user is regular.
        if not me_admin:
            return HttpResponse("Only admins can do that!", status=403)

        if not form.is_valid():
            return render(request, 
                'core_app/remove-organization-user.html', 
                    {'user': user, 'form': form})

        self.me.default.revoke_access(self.me, user)
        clipboard0, _    = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)

        clipboard1, _    = Clipboard.objects.get_or_create(
        user=user, organization=self.me.default)

        clipboard0.posts.add(*clipboard1.posts.all())
        clipboard0.cards.add(*clipboard1.cards.all())
        clipboard0.lists.add(*clipboard1.lists.all())

        clipboard1.posts.clear()
        clipboard1.cards.clear()
        clipboard1.lists.clear()

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
        if not self.me.default.admins.filter(id=self.me.id).exists():
            return HttpResponse("Only admins can cancel invites!", status=403)

        # We need to make sure the invite belongs to our self.me.default
        # organization otherwise a hacker can just cancel all invites
        # by running a simple script.
        invite = Invite.objects.get(id=invite_id, organization=self.me.default)

        # If there is no more invites sent to this user
        # and his default org is null then he is not an existing
        # user.
        cond = invite.user.invites.exists() and invite.user.default
        if not cond:
            invite.user.delete()
        invite.delete()
        return redirect('core_app:list-invites')

class ManageOrganizationAdmins(GuardianView):
    def get(self, request):
        included = self.me.default.admins.all()
        users    = self.me.default.users.all()
        excluded = users.exclude(id__in=included)
        total    = included.count() + excluded.count()

        return render(request, 'core_app/manage-organization-admins.html', 
        {'included': included, 'excluded': excluded,
        'me': self.me, 'organization': self.me.default,'form':forms.UserSearchForm(), 
        'count': total, 'total': total,})

    def post(self, request):
        sqlike = User.from_sqlike()
        form = forms.UserSearchForm(request.POST, sqlike=sqlike)

        included = self.me.default.admins.all()
        users    = self.me.default.users.all()
        excluded = users.exclude(id__in=included)
        total    = included.count() + excluded.count()
        
        if not form.is_valid():
            return render(request, 'core_app/manage-organization-admins.html', 
                {'me': self.me, 'count': 0, 'total': total, 'organization': self.me.default,
                        'form':form}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)
        count = included.count() + excluded.count()

        return render(request, 'core_app/manage-organization-admins.html', 
        {'included': included, 'excluded': excluded, 
        'me': self.me, 'organization': self.me.default,'form':form, 
        'count': count, 'total': total,})

class BindOrganizationAdmin(GuardianView):
    def get(self, request, user_id):
        # Make sure the user belongs to the organization otherwise
        # should return not existing record error.
        user = self.me.default.users.get(id=user_id)

        if self.me.default.owner != self.me:
            return HttpResponse("Just owner can do that!", status=403)

        self.me.default.admins.add(user)
        self.me.default.save()

        return HttpResponse(status=200)

class UnbindOrganizationAdmin(GuardianView):
    def get(self, request, user_id):
        # Grab the user from the organization users so it makes sure
        # he belongs to the organization. It can avoid some misbehaviors.
        user = self.me.default.users.get(id=user_id)

        if self.me.default.owner == user:
            return HttpResponse("You can't remove the owner!", status=403)

        if self.me.default.owner != self.me:
            return HttpResponse("No permission for that!", status=403)

        self.me.default.admins.remove(user)
        self.me.default.save()
        return HttpResponse(status=200)

class ListNodes(GuardianView):
    """
    """

    def get(self, request):
        nodes = Node.objects.filter(Q(board__organization=self.me.default) 
        | Q(group__organization=self.me.default)) 

        nodes = nodes.filter(Q(board__members=self.me) | Q(group__users=self.me))

        nodes = nodes.order_by('-indexer')
        total = nodes.count()

        boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        listpins = self.me.listpin_set.filter(organization=self.me.default)
        cardpins = self.me.cardpin_set.filter(organization=self.me.default)
        grouppins = self.me.grouppin_set.filter(organization=self.me.default)
        postpins = self.me.postpin_set.filter(organization=self.me.default)

        filter, _ = NodeFilter.objects.get_or_create(
        user=self.me, organization=self.me.default)

        query = Q(board__name__icontains=filter.pattern) | \
        Q(board__description__icontains=filter.pattern) | \
        Q(group__name__icontains=filter.pattern) | \
        Q(group__description__icontains=filter.pattern)

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
        print('ooooo', request.POST['timezone'])
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('core_app:index')







