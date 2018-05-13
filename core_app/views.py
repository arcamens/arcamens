from core_app.models import Organization, User, \
UserFilter, Tag, EDeleteTag, ECreateTag, EUnbindUserTag, EBindUserTag, \
Invite, EInviteUser, EJoinOrganization,  Clipboard, Event, EShout, \
EUpdateOrganization, ERemoveOrganizationUser, Node, NodeFilter, EDisabledAccount
from django.core.paginator import Paginator, EmptyPage
from django.utils.dateparse import parse_datetime
from card_app.models import Card, GlobalCardFilter, GlobalTaskFilter
from django.shortcuts import render, redirect
from slock.views import AuthenticatedView
from slock.forms import UpdatePasswordForm
from core_app.forms import SignupForm
from django.views.generic import View
from django.core.mail import send_mail
from django.http import HttpResponse
from post_app.models import Post
from django.db.models import Q
from datetime import date
from jsim.jscroll import JScroll
from django.urls import reverse
from django.conf import settings
from traceback import print_exc
from itertools import chain
from . import models
from . import forms
import core_app.export
import random
import json

# Create your views here.

class GuardianView(AuthenticatedView):
    def delegate(self, request, *args, **kwargs):
        user = User.objects.get(id=self.user_id)

        # Allow just the owner of the account to perform operations.
        if not user.default.owner.enabled and user != user.default.owner:
            return HttpResponse("Disabled organization \
                account!", status=403)

        return super(GuardianView, self).delegate(
            request, *args, **kwargs)

class Index(AuthenticatedView):
    """
    """

    def get(self, request):
        user = User.objects.get(id=self.user_id)
        organizations = user.organizations.exclude(id=user.default.id)
    
        if hasattr(user, 'register_process'):
            return render(request, 
                'site_app/confirm-email.html', {'user': user})

        if not user.default.owner.enabled:
            if user.default.owner != user:
                return redirect('core_app:disabled-account')

        return render(request, 'core_app/index.html', 
        {'user': user, 'default': user.default, 'organization': user.default,
        'organizations': organizations,
         'settings': settings})

class DisabledAccount(AuthenticatedView):
    def get(self, request):
        user = User.objects.get(id=self.user_id)
        other = user.owned_organizations.first()

        return render(request, 'core_app/disabled-account.html', 
        {'user': user, 'other': other})

class SwitchOrganization(AuthenticatedView):
    def get(self, request, organization_id):
        user = User.objects.get(id=self.user_id)

        user.ws_unsubscribe(user.default)

        user.default = Organization.objects.get(
        id=organization_id)

        user.ws_subscribe(user.default)

        user.save()
        # When user updates organization, it tells all the other
        # tabs to restart the UI.
        user.ws_restart(user.default)

        return redirect('core_app:index')

class UpdateUserInformation(GuardianView):
    def get(self, request):
        user = User.objects.get(id=self.user_id)
        form = forms.UserForm(instance=user)

        return render(request, 'core_app/update-user-information.html', 
        {'user': user, 'form': form})

    def post(self, request):
        user = User.objects.get(id=self.user_id)
        form = forms.UserForm(request.POST, request.FILES, instance=user)

        if not form.is_valid():
            return render(request, 
                'core_app/update-user-information.html', 
                    {'user': user, 'form': form}, status=400)

        form.save()
        return HttpResponse(status=200)

class CreateOrganization(AuthenticatedView):
    """
    """

    def get(self, request, user_id):
        user = User.objects.get(id=self.user_id)
        form = forms.OrganizationForm()
        return render(request, 'core_app/create-organization.html', 
        {'form':form, 'user': user})

    def post(self, request, user_id):
        user = User.objects.get(id=self.user_id)
        form = forms.OrganizationForm(request.POST)

        if not form.is_valid():
            return render(request, 'core_ap/create-organization.html',
                        {'form': form, 'user': user}, status=400)

        organization = Organization.objects.create(
        name=form.cleaned_data['name'], owner=user) 

        user.organizations.add(organization)
        user.default = organization
        organization.admins.add(user)
        user.save()
        return redirect('core_app:index')

class UpdateOrganization(GuardianView):
    def get(self, request, organization_id):
        user = User.objects.get(id=self.user_id)

        organization = Organization.objects.get(id=organization_id)
        return render(request, 
        'core_app/update-organization.html',{'organization': organization, 
        'form': forms.UpdateOrganizationForm(instance=organization)})

    def post(self, request, organization_id):
        user = User.objects.get(id=self.user_id)

        record  = Organization.objects.get(id=organization_id)
        form    = forms.UpdateOrganizationForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'core_app/update-organization.html',
                {'organization': record, 'form': form}, status=400)

        form.save()

        event = EUpdateOrganization.objects.create(
        organization=user.default, user=user)
        event.dispatch(*record.users.all())

        user.ws_sound(record)

        return redirect('core_app:index')

class DeleteOrganization(GuardianView):
    def get(self, request,  organization_id):
        organization = Organization.objects.get(id = organization_id)
        user         = User.objects.get(id=self.user_id)
        form = forms.ConfirmOrganizationDeletionForm()

        return render(request, 
            'core_app/delete-organization.html', 
                {'organization': organization, 'form': form})

    def post(self, request, organization_id):
        organization = Organization.objects.get(id = organization_id)

        form = forms.ConfirmOrganizationDeletionForm(request.POST, 
        confirm_token=organization.name)

        if not form.is_valid():
            return render(request, 
                'core_app/delete-organization.html', 
                    {'organization': organization, 'form': form}, status=400)

        user     = User.objects.get(id=self.user_id)
        # event    = EDeleteOrganization.objects.create(organization=user.default,
        # organization_name=organization.name, user=user)
# 
        # user.ws_unsubscribe_organization(organization.id)
        # user.ws_sound()

        # should tell users to unsubscribe here.
        # it may hide bugs.
        # event.dispatch(*organization.users.all())
        # organization.delete()

        if user.owned_organizations.count() == 1:
            return HttpResponse("You can't delete \
                this organization..", status=403)

        # First remove the reference otherwise
        # the user gets deleted in cascade due to the
        # user.default field.
        user.organizations.remove(organization)
        user.default = user.organizations.first()
        user.save()
        organization.delete()

        return redirect('core_app:index')

class ListUsers(GuardianView):
    def get(self, request, organization_id):
        me           = User.objects.get(id=self.user_id)
        organization = Organization.objects.get(id=organization_id)
        filter, _    = UserFilter.objects.get_or_create(
        user=me, organization=me.default)

        users = organization.users.all()
        total = users.count()

        users = User.collect_users(users, filter.pattern)
        count = users.count()

        form  = forms.UserFilterForm(instance=filter)

        return render(request, 'core_app/list-users.html', 
        {'users': users, 'owner': organization.owner, 'total': total, 
        'form': form, 'count': count, 'organization': organization})

    def post(self, request, organization_id):
        me           = User.objects.get(id=self.user_id)
        organization = Organization.objects.get(id=organization_id)

        filter, _    = UserFilter.objects.get_or_create(
        user=me, organization=me.default)

        users = organization.users.all()
        total = users.count()
        sqlike = User.from_sqlike()
        form  = forms.UserFilterForm(request.POST, sqlike=sqlike, instance=filter)

        if not form.is_valid():
            return render(request, 'core_app/list-users.html', 
                {'count': 0, 'owner': organization.owner, 
                    'total': total, 'form': form,
                        'organization': organization}, status=400)
  
        form.save()

        users = sqlike.run(users)
        count = users.count()

        return render(request, 'core_app/list-users.html', 
        {'users': users, 'owner': organization.owner, 'count': count,
        'total': total, 'form': form, 'organization': organization})

class ManageUserTags(GuardianView):
    def get(self, request, user_id):
        me       = User.objects.get(id=self.user_id)
        user     = User.objects.get(id=user_id)

        included = user.tags.filter(organization=me.default)
        excluded = me.default.tags.all()
        excluded = excluded.exclude(users=user)
        total    = included.count() + excluded.count()

        return render(request, 'core_app/manage-user-tags.html', 
        {'included': included, 'excluded': excluded, 'user': user, 'me': me,
        'form':forms.TagSearchForm(), 'total': total, 'count': total})

    def post(self, request, user_id):
        sqlike = Tag.from_sqlike()
        form = forms.TagSearchForm(request.POST, sqlike=sqlike)

        me = User.objects.get(id=self.user_id)
        user = User.objects.get(id=user_id)

        included = user.tags.filter(organization=me.default)
        excluded = me.default.tags.all()
        excluded = excluded.exclude(users=user)
        total    = included.count() + excluded.count()

        if not form.is_valid():
            return render(request, 'core_app/manage-user-tags.html', 
                {'included': included, 'excluded': excluded, 'total': total,
                    'organization': me.default, 'user': user, 'count': 0,
                        'form':form, 'me': me}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)
        count = included.count() + excluded.count()

        return render(request, 'core_app/manage-user-tags.html', 
        {'included': included, 'excluded': excluded, 'user': user,
        'me': me, 'organization': me.default, 'total': total, 
        'count': count, 'form':form})

class ListEvents(GuardianView):
    """
    """

    def get(self, request):
        user   = User.objects.get(id=self.user_id)
        events = user.events.filter(organization=user.default)
        count = events.count()
        events = events.values('html', 'id').order_by('-created')

        elems = JScroll(user.id, 'core_app/list-events-scroll.html', events)

        return render(request, 'core_app/list-events.html', 
        {'elems': elems.as_div(), 'user': user, 
         'organization': user.default, 'count': count})

class ListTags(GuardianView):
    def get(self, request):
        user      = User.objects.get(id=self.user_id)
        tags = user.default.tags.all()
        form = forms.TagSearchForm()
        total = tags.count()
        return render(request, 'core_app/list-tags.html', 
        {'tags': tags, 'form': form, 'user': user, 'total': total,
        'count': total, 'organization': user.default})

    def post(self, request):
        user = User.objects.get(id=self.user_id)
        sqlike = Tag.from_sqlike()
        form = forms.TagSearchForm(request.POST, sqlike=sqlike)
        tags = user.default.tags.all()

        total = tags.count()
    
        if not form.is_valid():
            return render(request, 'core_app/list-tags.html', 
                {'tags': tags, 'form': form, 'user': user, 'total': total,
                    'count': 0, 'organization': user.default})

        tags  = sqlike.run(tags)
        count = tags.count()

        return render(request, 'core_app/list-tags.html', 
        {'tags': tags, 'form': form, 'user': user, 
        'organization': user.default, 'total': total, 'count': count})

class DeleteTag(GuardianView):
    def get(self, request, tag_id):
        user  = User.objects.get(id=self.user_id)
        tag   = Tag.objects.get(id=tag_id)

        event = EDeleteTag.objects.create(
        organization=user.default, user=user, tag_name=tag.name)
        tag.delete()

        users = user.default.users.all()
        event.dispatch(*users)

        user.ws_sound(user.default)

        return HttpResponse(status=200)

class CreateTag(GuardianView):
    def get(self, request):
        user = User.objects.get(id=self.user_id)
        form = forms.TagForm()

        return render(request, 'core_app/create-tag.html', 
        {'form':form})

    def post(self, request):
        user = User.objects.get(id=self.user_id)
        form = forms.TagForm(request.POST)

        if not form.is_valid():
            return render(request, 'core_app/create-tag.html',
                        {'form': form, 'user': user}, status=400)
        record       = form.save(commit=False)
        record.organization = user.default
        record.save()

        event = ECreateTag.objects.create(
        organization=user.default, user=user, tag=record)

        users = user.default.users.all()
        event.dispatch(*users)

        user.ws_sound(user.default)

        return redirect('core_app:list-tags')

class UnbindUserTag(GuardianView):
    def get(self, request, user_id, tag_id):
        user = User.objects.get(id=user_id)
        tag  = Tag.objects.get(id=tag_id)
        user.tags.remove(tag)
        user.save()

        me = User.objects.get(id=self.user_id)
        event = EUnbindUserTag.objects.create(
        organization=me.default, user=me, peer=user, tag=tag)

        users = me.default.users.all()
        event.dispatch(*users)

        user.ws_sound(me.default)

        return HttpResponse(status=200)

class BindUserTag(GuardianView):
    def get(self, request, user_id, tag_id):
        user = User.objects.get(id=user_id)
        tag  = Tag.objects.get(id=tag_id)
        user.tags.add(tag)
        user.save()

        me    = User.objects.get(id=self.user_id)
        event = EBindUserTag.objects.create(
        organization=me.default, user=me, peer=user, tag=tag)
        users = me.default.users.all()
        event.dispatch(*users)

        me.ws_sound(me.default)

        return HttpResponse(status=200)

class InviteOrganizationUser(GuardianView):
    def get(self, request, organization_id):
        user = User.objects.get(id=self.user_id)

        return render(request, 'core_app/invite-organization-user.html', 
        {'form': forms.OrganizationInviteForm(), 'user': user})

    def post(self, request, organization_id):
        me = User.objects.get(id=self.user_id)

        if not me.default.admins.filter(id=me.id).exists():
            return HttpResponse("Only admins can do that!", status=403)

        if me.default.owner.is_max_users():
            return HttpResponse("Max users limit was arrived!\
                You need to upgrade your plan!", status=403)

        form = forms.OrganizationInviteForm(request.POST)

        if not form.is_valid():
            return render(request, 'core_app/invite-organization-user.html',
                  {'form': form, 'organization': organization}, status=400)

        email = form.cleaned_data['email']

        # Create the user anyway, but make it disabled
        # the user need to fill information first.
        user, _  = User.objects.get_or_create(email=email)

        if user.organizations.filter(id=me.default.id).exists():
            return HttpResponse("The user is already a member!", status=403)

        # If there is already an invite just tell him it was sent.
        is_member = user.invites.filter(
            organization=me.default).exists()

        if is_member:
            return HttpResponse("The user was already invited!", status=403)

        invite = Invite.objects.create(
            organization=me.default, peer=me, user=user)

        invite.send_email()

        event = EInviteUser.objects.create(
        organization=me.default, user=me, peer=user)
        event.dispatch(*me.default.users.all())

        me.ws_sound(me.default)

        return redirect('core_app:list-users', 
        organization_id=me.default.id)

class ResendInvite(GuardianView):
    def get(self, request, invite_id):
        me = User.objects.get(id=self.user_id)

        if not me.default.admins.filter(id=me.id).exists():
            return HttpResponse("Only admins can do that!", status=403)

        invite = Invite.objects.get(id=invite_id)
        invite.send_email()

        return redirect('core_app:list-users', 
        organization_id=invite.organization.id)

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

        main = Organization.objects.create(name='Main', 
        owner=invite.user)
        invite.user.organizations.add(main)

        invite.user.save()

        # validates the invite.
        invite.delete()

        invites = Invite.objects.filter(
        organization=organization, user=invite.user)
        invites.delete()

        # The user should be Arcamens Service(thinking about it later).
        event = EJoinOrganization.objects.create(organization=organization, 
        peer=invite.user, user=invite.user)
        event.dispatch(*organization.users.all())

        invite.user.ws_sound(organization)

        # Authenticate the user.
        request.session['user_id'] = invite.user.id

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
        form = SignupForm(request.POST, instance=invite.user)

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
        user         = User.objects.get(id=self.user_id)
        clipboard, _ = Clipboard.objects.get_or_create(
        user=user, organization=user.default)

        cards = clipboard.cards.all()
        lists = clipboard.lists.all()
        posts = clipboard.posts.all()

        total = cards.count() + lists.count() + posts.count()

        return render(request, 'core_app/list-clipboard.html', 
        {'user': user, 'cards': cards , 'posts': posts, 'lists': lists, 'total': total})

class SeenEvent(GuardianView):
    def get(self, request, event_id):
        user  = User.objects.get(id=self.user_id)
        event = Event.objects.get(id=event_id)
        event.seen(user)
        return redirect('core_app:list-events')

class ListLogs(GuardianView):
    """
    """

    def get(self, request):
        user = User.objects.get(id=self.user_id)
        form = forms.EventFilterForm()
        return render(request, 'core_app/list-logs.html', 
        {'user': user, 'form': form,
         'organization': user.default})

    def post(self, request):
        user  = User.objects.get(id=self.user_id)
        form  = forms.EventFilterForm(request.POST)

        if not form.is_valid():
            return render(request, 'core_app/list-logs.html', 
                {'user': user, 'form': form,
                     'organization': user.default})

        end    = form.cleaned_data['end']
        start  = form.cleaned_data['start']

        events = user.seen_events.filter(created__lte=end,
        created__gte=start, organization=user.default)

        count  = events.count()
        events = events.values('html').order_by('-created')

        events = JScroll(user.id, 'core_app/list-logs-scroll.html', events)

        return render(request, 'core_app/list-logs.html', 
        {'user': user, 'form': form, 'events':events.as_div(), 
        'count': count,'organization': user.default})

class AllSeen(GuardianView):
    def get(self, request):
        user  = User.objects.get(id=self.user_id)
        events = user.events.filter(organization=user.default)

        for ind in events:
            ind.seen(user)
        return redirect('core_app:list-events')

class Export(GuardianView):
    def get(self, request):
        if request.GET.get('kind') == 'timelines':
            user = User.objects.get(id=self.user_id)
            data = core_app.export.export_timelines(user)
            response = HttpResponse(data, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=timelines.json'
            return response
        elif request.GET.get('kind') == 'boards':
            user = User.objects.get(id=self.user_id)
            data = core_app.export.export_boards(user)
            response = HttpResponse(data, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=boards.json'
            return response
        else:
            return render(request, 'core_app/export.html')

class Import(GuardianView):
    def post(self, request):
        user = User.objects.get(id=self.user_id)
        file = request.FILES['file'].read()
        if request.POST.get('kind') == 'timelines':
            core_app.export.import_timelines(user, file)
            return HttpResponse('OK')
        elif request.POST.get('kind') == 'boards':
            core_app.export.import_boards(user, file)
            return HttpResponse('OK')
        return HttpResponse('Fail')

class ConfirmClipboardDeletion(GuardianView):
    def get(self, request):
        return render(request, 'core_app/confirm-clipboard-deletion.html')

class DeleteAllClipboard(GuardianView):
    def get(self, request):
        user         = User.objects.get(id=self.user_id)
        clipboard, _ = Clipboard.objects.get_or_create(
        user=user, organization=user.default)

        cards = clipboard.cards.all()
        lists = clipboard.lists.all()
        posts = clipboard.posts.all()
        cards.delete()
        lists.delete()
        posts.delete()

        return redirect('core_app:list-clipboard')

class Shout(GuardianView):
    def get(self, request):
        me = User.objects.get(id=self.user_id)
        form = forms.ShoutForm()

        return render(request, 'core_app/shout.html', {'form': form, 'me': me})

    def post(self, request):
        me   = User.objects.get(id=self.user_id)
        form = forms.ShoutForm(request.POST)

        if not form.is_valid():
            return render(request, 'core_app/list-users.html', 
                {'form': form, 'me': me}, status=400)

        event = EShout.objects.create(organization=me.default, 
        user=me, msg=form.cleaned_data['msg'])

        users = me.default.users.all()
        event.dispatch(*users)

        me.ws_sound(me.default)
        return redirect('core_app:list-events')

class UpdatePassword(GuardianView):
    def get(self, request):
        user = User.objects.get(id=self.user_id)
        form = UpdatePasswordForm()

        return render(request, 
            'core_app/update-password.html', 
                {'user': user, 'form': form})

    def post(self, request):
        user = User.objects.get(id=self.user_id)
        form = UpdatePasswordForm(request.POST, instance=user)

        if not form.is_valid():
            return render(request, 'core_app/update-password.html', 
                    {'user': user, 'form': form}, status=400)
    
        form.save()

        return redirect('core_app:update-user-information')

class RemoveOrganizationUser(GuardianView):
    def get(self, request, user_id):
        me   = User.objects.get(id=self.user_id)
        user = User.objects.get(id=user_id)

        form = forms.RemoveUserForm()
        timelines = user.owned_timelines.filter(organization=me.default)
        boards = user.owned_boards.filter(organization=me.default)

        return render(request, 'core_app/remove-organization-user.html', 
        {'user': user, 'form': form, 'timelines': timelines, 'boards': boards})

    def post(self, request, user_id):
        form = forms.RemoveUserForm(request.POST)
        user = User.objects.get(id=user_id)
        me   = User.objects.get(id=self.user_id)

        # If i'm the owner then i can't remove myself.
        # I should delete the organization.

        if me.default.owner == user:
            return HttpResponse("You can't remove the owner!", status=403)

        is_admin = me.default.admins.filter(id=user.id).exists()
        me_owner = me.default.owner == me
        me_admin = me.default.admins.filter(id=me.id).exists()

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

        # Remove user from all posts/cards he is assigned to.
        user.assignments.through.objects.filter(
            post__ancestor__organization=me.default).delete()

        user.tasks.through.objects.filter(
            card__ancestor__ancestor__organization=me.default).delete()

        # Remove as an worker from all timelines.
        user.timelines.through.objects.filter(
        timeline__organization=me.default, timeline__users=user).delete()

        user.boards.through.objects.filter(
        board__organization=me.default, board__members=user).delete()

        timelines = user.owned_timelines.filter(organization=me.default)

        for ind in timelines:
            ind.owner = me
            ind.users.add(me)
            ind.save()

        boards = user.owned_boards.filter(organization=me.default)

        for ind in boards:
            ind.owner = me
            ind.members.add(me)
            ind.save()

        user.organizations.remove(me.default)

        if user.default == me.default:
            user.default = user.organizations.first()
        user.save()

        event = ERemoveOrganizationUser.objects.create(organization=me.default, user=me, 
        peer=user, reason=form.cleaned_data['reason'])

        event.dispatch(*me.default.users.all())

        msg = 'You no longer belong to %s!\n\n%s' % (me.default.name, 
        form.cleaned_data['reason'])

        send_mail('%s notification!' % me.default.name, msg, 
        'noreply@arcamens.com', [user.email], fail_silently=False)

        return redirect('core_app:list-users', organization_id=me.default.id)

class ListInvites(GuardianView):
    def get(self, request):
        me = User.objects.get(id=self.user_id)
        invites = me.default.invites.all()

        return render(request, 'core_app/list-invites.html', 
        {'organization': me.default, 'invites': invites})

class CancelInvite(GuardianView):
    def get(self, request, invite_id):
        invite = Invite.objects.get(id=invite_id)

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
        me = User.objects.get(id=self.user_id)

        included = me.default.admins.all()
        users    = me.default.users.all()
        excluded = users.exclude(id__in=included)
        total    = included.count() + excluded.count()

        return render(request, 'core_app/manage-organization-admins.html', 
        {'included': included, 'excluded': excluded,
        'me': me, 'organization': me.default,'form':forms.UserSearchForm(), 
        'count': total, 'total': total,})

    def post(self, request):
        sqlike = User.from_sqlike()
        form = forms.UserSearchForm(request.POST, sqlike=sqlike)
        me   = User.objects.get(id=self.user_id)

        included = me.default.admins.all()
        users    = me.default.users.all()
        excluded = users.exclude(id__in=included)
        total    = included.count() + excluded.count()
        
        if not form.is_valid():
            return render(request, 'core_app/manage-organization-admins.html', 
                {'me': me, 'count': 0, 'total': total, 'organization': me.default,
                        'form':form}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)
        count = included.count() + excluded.count()

        return render(request, 'core_app/manage-organization-admins.html', 
        {'included': included, 'excluded': excluded, 
        'me': me, 'organization': me.default,'form':form, 
        'count': count, 'total': total,})

class BindOrganizationAdmin(GuardianView):
    def get(self, request, organization_id, user_id):
        user = User.objects.get(id=user_id)
        me    = User.objects.get(id=self.user_id)
        organization = Organization.objects.get(id=organization_id)

        if organization.owner != me:
            return HttpResponse("Just owner can do that!", status=403)

        organization.admins.add(user)
        organization.save()

        # me    = User.objects.get(id=self.user_id)
        # event = EBindOrganizationUser.objects.create(organization=me.default,
        # organization=organization, user=me, peer=user)
# 
        # event.dispatch(*organization.users.all())
# 
        # me.ws_sound(organization)
        # me.ws_subscribe(organization, target=user)

        # it seems i cant warrant the order the events will be dispatched
        # to the queue, if it is userid queue or organizationid queue
        # then i have to just send again the sound event to the 
        # user queue to warrant the event sound being dispatched.
        # obs: if i'll abandon sound when user interacts it is not
        # necessary.
        # me.ws_sound(user)

        return HttpResponse(status=200)

class UnbindOrganizationAdmin(GuardianView):
    def get(self, request, organization_id, user_id):
        user = User.objects.get(id=user_id)
        me = User.objects.get(id=self.user_id)

        organization = Organization.objects.get(id=organization_id)

        if organization.owner == user:
            return HttpResponse("You can't remove the owner!", status=403)

        if organization.owner != me:
            return HttpResponse("No permission for that!", status=403)


        organization.admins.remove(user)
        organization.save()

        # me    = User.objects.get(id=self.user_id)
        # event = EUnbindOrganizationUser.objects.create(organization=me.default,
        # organization=organization, user=me, peer=user)
# 
        # event.dispatch(*organization.users.all())
# 
        # me.ws_sound(organization)

        # When user is removed from timline then it
        # gets unsubscribed from the organization.
        # The logged user is sending the event
        # to the user queue that is going to receive
        # the unsubscribe evvent.
        # me.ws_unsubscribe(organization, target=user)

        # As said before, order of events cant be determined
        # when dispatched towards two queues. It might
        # happen of sound event being dispatched before subscribe event.
        # So, we warrant sound to happen.
        # me.ws_sound(user)

        return HttpResponse(status=200)

class ListNodes(GuardianView):
    """
    """

    def get(self, request):
        user  = User.objects.get(id=self.user_id)
        nodes = Node.objects.filter(Q(board__organization=user.default) 
        | Q(timeline__organization=user.default)) 

        nodes = nodes.filter(Q(board__members=user) | Q(timeline__users=user))

        nodes = nodes.order_by('-indexer')
        total = nodes.count()

        boardpins = user.boardpin_set.filter(organization=user.default)
        listpins = user.listpin_set.filter(organization=user.default)
        cardpins = user.cardpin_set.filter(organization=user.default)
        timelinepins = user.timelinepin_set.filter(organization=user.default)

        filter, _ = NodeFilter.objects.get_or_create(
        user=user, organization=user.default)

        query = Q(board__name__icontains=filter.pattern) | \
        Q(board__description__icontains=filter.pattern) | \
        Q(timeline__name__icontains=filter.pattern) | \
        Q(timeline__description__icontains=filter.pattern)

        nodes = nodes.filter(query) if filter.status else nodes
        count = nodes.count()

        return render(request, 'core_app/list-nodes.html', 
        {'nodes': nodes, 'boardpins': boardpins, 'listpins': listpins, 'user': user, 'total': total, 
        'count': count, 'organization': user.default, 'filter': filter, 
        'cardpins': cardpins, 'timelinepins': timelinepins})

class SetupNodeFilter(GuardianView):
    def get(self, request, organization_id):
        filter = NodeFilter.objects.get(user__id=self.user_id, 
        organization__id=organization_id)

        organization = Organization.objects.get(id=organization_id)

        return render(request, 'core_app/setup-node-filter.html', 
        {'form': forms.NodeFilterForm(instance=filter), 
        'organization': organization})

    def post(self, request, organization_id):
        record = NodeFilter.objects.get(
        organization__id=organization_id, user__id=self.user_id)

        form         = forms.NodeFilterForm(request.POST, instance=record)
        organization = Organization.objects.get(id=organization_id)

        if not form.is_valid():
            return render(request, 'core_app/setup-node-filter.html',
                   {'node': record, 'form': form, 
                        'organization': organization}, status=400)
        form.save()
        return redirect('core_app:list-nodes')







