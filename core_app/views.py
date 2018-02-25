from django.views.generic import View
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage
from core_app.utils import search_tokens
from card_app.models import Card
from post_app.models import Post
from functools import reduce
import operator
from django.core.mail import send_mail
from django.http import HttpResponse
from django.db.models import Q
from core_app.models import OrganizationService, Organization
from slock.views import AuthenticatedView
from django.urls import reverse
from board_app.models import Organization
from . import models
from . import forms
from core_app.models import User
import timeline_app
import json
from django.conf import settings
from traceback import print_exc
from core_app import ws
import random

# Create your views here.

class GuardianView(AuthenticatedView):
    def delegate(self, request, *args, **kwargs):
        user = models.User.objects.get(id=self.user_id)

        if not user.default.owner.enabled:
            return redirect('core_app:disabled-organization', user_id=user.id)

        return super(GuardianView, self).delegate(
            request, *args, **kwargs)

class Index(GuardianView):
    """
    """

    def get(self, request):
        user = models.User.objects.get(id=self.user_id)
        organizations = user.organizations.exclude(id=user.default.id)
    
        # can be improved.
        queues = list(map(lambda ind: 'timeline%s' % ind, 
        user.timelines.values_list('id')))

        queues.extend(map(lambda ind: 'board%s' % ind, 
        user.boards.values_list('id')))

        return render(request, 'core_app/index.html', 
        {'user': user, 'default': user.default, 'organization': user.default,
        'organizations': organizations, 'queues': json.dumps(queues),
         'settings': settings})

class SwitchOrganization(GuardianView):
    def get(self, request, organization_id):
        user = models.User.objects.get(id=self.user_id)

        ws.client.publish('user%s' % user.id, 
            'unsubscribe organization%s' % user.default.id, 0, False)

        user.default = models.Organization.objects.get(
        id=organization_id)

        ws.client.publish('user%s' % user.id, 
            'subscribe organization%s' % user.default.id, 0, False)

        user.save()
        return redirect('core_app:index')

class UpdateUserInformation(GuardianView):
    def get(self, request):
        user = models.User.objects.get(id=self.user_id)
        form = forms.UserForm(instance=user)

        return render(request, 'core_app/update-user-information.html', 
        {'user': user, 'form': form})

    def post(self, request):
        user = models.User.objects.get(id=self.user_id)
        form = forms.UserForm(request.POST, request.FILES, instance=user)

        if not form.is_valid():
            print(form.errors)

            return render(request, 
                'core_app/update-user-information.html', 
                    {'user': user, 'form': form}, status=400)

        form.save()
        return HttpResponse(status=200)

class CreateOrganization(GuardianView):
    """
    """

    def get(self, request, user_id):
        user = models.User.objects.get(id=self.user_id)
        form = forms.OrganizationForm()
        return render(request, 'core_app/create-organization.html', 
        {'form':form, 'user': user})

    def post(self, request, user_id):
        user = models.User.objects.get(id=self.user_id)
        form = forms.OrganizationForm(request.POST)

        if not form.is_valid():
            return render(request, 'core_ap/create-organization.html',
                        {'form': form, 'user': user}, status=400)

        organization = Organization.objects.create(
        name=form.cleaned_data['name'], owner=user) 

        user.organizations.add(organization)
        user.default = organization
        user.save()
        return redirect('core_app:index')

class UpdateOrganization(GuardianView):
    def get(self, request, organization_id):
        organization = models.Organization.objects.get(id=organization_id)
        return render(request, 'core_app/update-organization.html',
        {'organization': organization, 'form': forms.UpdateOrganizationForm(instance=organization)})

    def post(self, request, organization_id):
        record  = models.Organization.objects.get(id=organization_id)
        form    = forms.UpdateOrganizationForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'core_app/update-organization.html',
                {'organization': record, 'form': form})

        form.save()
        return redirect('core_app:index')

class DeleteOrganization(GuardianView):
    def get(self, request,  organization_id):
        organization = models.Organization.objects.get(id = organization_id)
        user         = models.User.objects.get(id=self.user_id)

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
        me           = models.User.objects.get(id=self.user_id)
        organization = models.Organization.objects.get(id=organization_id)
        total        = organization.users.all()
        filter, _    = models.UserFilter.objects.get_or_create(
        user=me, organization=me.default)

        total = organization.users.all()

        users = total.filter(Q(
        name__contains=filter.pattern) | Q(
        email__contains=filter.pattern))

        form  = forms.UserFilterForm(instance=filter)

        return render(request, 'core_app/list-users.html', 
        {'users': users, 'owner': organization.owner, 'total': total, 'form': form,
        'organization': organization})

    def post(self, request, organization_id):
        me           = models.User.objects.get(id=self.user_id)
        organization = models.Organization.objects.get(id=organization_id)

        total        = organization.users.all()
        filter, _    = models.UserFilter.objects.get_or_create(
        user=me, organization=me.default)

        total = organization.users.all()
        form  = forms.UserFilterForm(request.POST, instance=filter)

        if not form.is_valid():
            return render(request, 'core_app/list-users.html', 
                {'users': total, 'owner': organization.owner, 
                    'total': total, 'form': form,
                        'organization': organization}, status=400)
  
        form.save()

        users = total.filter(Q(
        name__contains=filter.pattern) | Q(
        email__contains=filter.pattern))

        return render(request, 'core_app/list-users.html', 
        {'users': users, 'owner': organization.owner, 
        'total': total, 'form': form, 'organization': organization})

class ManageUserTags(GuardianView):
    def get(self, request, user_id):
        me = models.User.objects.get(id=self.user_id)
        user = models.User.objects.get(id=user_id)

        included = user.tags.filter(organization=me.default)
        excluded = me.default.tags.all()
        excluded = excluded.exclude(users=user)

        return render(request, 'core_app/manage-user-tags.html', 
        {'included': included, 'excluded': excluded, 'user': user,
        'organization': me.default,'form':forms.TagSearchForm()})

    def post(self, request, user_id):
        form = forms.TagSearchForm(request.POST)

        me = models.User.objects.get(id=self.user_id)
        user = models.User.objects.get(id=user_id)

        included = me.tags.filter(organization=me.default)
        excluded = me.default.tags.all()
        excluded = excluded.exclude(users=user)

        if not form.is_valid():
            return render(request, 'core_app/manage-user-tags.html', 
                {'included': included, 'excluded': excluded,
                    'organization': me.default, 'user': user,
                        'form':form}, status=400)

        included = included.filter(
        name__contains=form.cleaned_data['name'])

        excluded = excluded.filter(
        name__contains=form.cleaned_data['name'])

        return render(request, 'core_app/manage-user-tags.html', 
        {'included': included, 'excluded': excluded, 'user': user,
        'me': me, 'organization': me.default,'form':form})

class EventPaginator(GuardianView):
    def get(self, request):
        user      = models.User.objects.get(id=self.user_id)
        events    = user.default.events.all().order_by('-created')[10:]

        page      = request.GET.get('page', 1)
        paginator = Paginator(events, 4)

        try:
            events = paginator.page(page)
        except EmptyPage:
            return HttpResponse('')

        return render(request, 'core_app/event-paginator.html', 
        {'events': events, 'user': user,})


class ListEvents(GuardianView):
    """
    """

    def get(self, request):
        user   = models.User.objects.get(id=self.user_id)
        events = user.default.events.all().order_by('-created')
        count = events.count()
        return render(request, 'core_app/list-events.html', 
        {'events': events[:10], 'user': user, 
         'organization': user.default, 'count': count})

class ListTags(GuardianView):
    def get(self, request):
        user      = models.User.objects.get(id=self.user_id)
        tags = user.default.tags.all()
        form = forms.TagSearchForm()

        return render(request, 'core_app/list-tags.html', 
        {'tags': tags, 'form': form, 'user': user, 
        'organization': user.default})

    def post(self, request):
        user = models.User.objects.get(id=self.user_id)
        form = forms.TagSearchForm(request.POST)
        tags = user.default.tags.all()

        if not form.is_valid():
            return render(request, 'core_app/list-tags.html', 
                {'tags': tags, 'form': form, 'user': user, 
                    'organization': user.default})

        tags = tags.filter(
        name__contains=form.cleaned_data['name'])

        return render(request, 'core_app/list-tags.html', 
        {'tags': tags, 'form': form, 'user': user, 
        'organization': user.default})

class DeleteTag(GuardianView):
    def get(self, request, tag_id):
        tag = models.Tag.objects.get(id=tag_id)
        tag.delete()
        return HttpResponse(status=200)

class CreateTag(GuardianView):
    def get(self, request):
        user     = models.User.objects.get(id=self.user_id)
        form = forms.TagForm()

        return render(request, 'core_app/create-tag.html', 
        {'form':form})

    def post(self, request):
        user = models.User.objects.get(id=self.user_id)
        form = forms.TagForm(request.POST)

        if not form.is_valid():
            return render(request, 'core_app/create-tag.html',
                        {'form': form, 'user': user}, status=400)
        record       = form.save(commit=False)
        record.organization = user.default
        record.save()
        return redirect('core_app:list-tags')

class UnbindUserTag(GuardianView):
    def get(self, request, user_id, tag_id):
        user = models.User.objects.get(id=user_id)
        tag = models.Tag.objects.get(id=tag_id)
        user.tags.remove(tag)
        user.save()

        me = models.User.objects.get(id=self.user_id)
        event = models.EUnbindUserTag.objects.create(
        organization=me.default, user=me, peer=user, tag=tag)
        users = me.default.users.all()
        event.users.add(*users)

        ws.client.publish('organization%s' % me.default.id, 
            'sound', 0, False)

        return HttpResponse(status=200)

class EBindUserTag(GuardianView):
    def get(self, request, event_id):
        event = models.EBindUserTag.objects.get(id=event_id)
        return render(request, 'core_app/e-bind-user-tag.html', 
        {'event':event})

class EUnbindUserTag(GuardianView):
    def get(self, request, event_id):
        event = models.EUnbindUserTag.objects.get(id=event_id)
        return render(request, 'core_app/e-unbind-user-tag.html', 
        {'event':event})

class BindUserTag(GuardianView):
    def get(self, request, user_id, tag_id):
        user = models.User.objects.get(id=user_id)
        tag = models.Tag.objects.get(id=tag_id)
        user.tags.add(tag)
        user.save()

        me = models.User.objects.get(id=self.user_id)
        event = models.EBindUserTag.objects.create(
        organization=me.default, user=me, peer=user, tag=tag)
        users = me.default.users.all()
        event.users.add(*users)

        ws.client.publish('organization%s' % me.default.id, 
            'sound', 0, False)

        return HttpResponse(status=200)

class EventQueues(GuardianView):
    def get(self, request):
        user = models.User.objects.get(id=user_id)
        queues = user.timelines.values_list('id')
        data = simplejson.dumps(some_data_to_dump)
        return HttpResponse(data, content_type='application/json')

class InviteOrganizationUser(GuardianView):
    def get(self, request, organization_id):
        user = models.User.objects.get(id=self.user_id)

        organization = models.Organization.objects.get(id=organization_id)

        return render(request, 'core_app/invite-organization-user.html', 
        {'form': forms.OrganizationInviteForm(), 'user': user, 'organization': organization})

    def post(self, request, organization_id):
        organization = models.Organization.objects.get(id=organization_id)
        form         = forms.OrganizationInviteForm(request.POST)

        if not form.is_valid():
            return render(request, 'core_app/invite-organization-user.html',
                  {'form': form, 'organization': organization}, status=400)

        email = form.cleaned_data['email']

        # If the user doesn't exist
        # we send him an email invite.
        me = models.User.objects.get(id=self.user_id)

        # Create the user anyway, but make it disabled
        # the user need to fill information first.
        user, _  = models.User.objects.get_or_create(email=email)
        
        # need to be improved.
        token = 'invite%s' % random.randint(1000, 10000)
        invite = models.Invite.objects.create(organization=organization, user=user, token=token)

        event = models.EInviteUser.objects.create(organization=organization, user=me, peer=user)
        event.users.add(me, user)

        url = reverse('core_app:join-organization', kwargs={
        'organization_id': organization.id, 'token': token})

        url = '%s%s' % (settings.LOCAL_ADDR, url)
        send_mail('You were invited to %s by %s.' % (organization.name, me.name),
        '%s %s' % (organization.name, url), settings.EMAIL_HOST_USER, [email],
        fail_silently=False)

        ws.client.publish('organization%s' % organization.id, 
            'sound', 0, False)

        return redirect('core_app:list-users', 
        organization_id=organization_id)

class JoinOrganization(View):
    def get(self, request, organization_id, token):
        # need some kind of token to be sent
        # for validating the invitation.

        invite = models.Invite.objects.get(token=token)

        if not invite.user.enabled:
            return redirect('core_app:signup-from-invite', 
                organization_id=organization_id, token=token)


        # Delete all the invites for this user.
        organization = models.Organization.objects.get(id=organization_id)

        invite.user.organizations.add(organization)
        invite.user.default = organization
        invite.user.save()

        # validates the invite.
        invite.delete()

        invites = models.Invite.objects.filter(
        organization=organization, user=invite.user)
        invites.delete()

        event = models.EJoinOrganization.objects.create(organization=organization, 
        peer=invite.user)
        event.users.add(*organization.users.all())

        ws.client.publish('organization%s' % organization.id, 
            'sound', 0, False)

        # Authenticate the user.
        request.session['user_id'] = invite.user.id

        # Maybe just redirect the user to a page telling he joined the org.
        return redirect('core_app:index')

class SignupFromInvite(View):
    def get(self, request, organization_id, token):
        invite = models.Invite.objects.get(    
        organization__id=organization_id, token=token)

        form = forms.UserForm(instance=invite.user)
        return render(request, 'core_app/signup-from-invite.html', 
        {'form': form, 'organization': invite.organization, 'token': token})

    def post(self, request, organization_id, token):
        invite = models.Invite.objects.get(    
        organization__id=organization_id, token=token)
        form = forms.UserForm(request.POST, instance=invite.user)

        if not form.is_valid():
            return render(request, 'core_app/signup-from-invite.html', 
                {'form': form, 'organization': invite.organization, 
                    'token': token}, status=400)

        record = form.save(commit=False)
        service        = OrganizationService.objects.get(paid=False)
        record.service = service
        record.enabled = True
        record.save()

        return redirect('core_app:join-organization', 
        organization_id=organization_id, token=token)

class EInviteUser(GuardianView):
    def get(self, request, event_id):
        event = models.EInviteUser.objects.get(id=event_id)
        return render(request, 'core_app/e-invite-user.html', 
        {'event':event})

class EJoinOrganization(GuardianView):
    def get(self, request, event_id):
        event = models.EJoinOrganization.objects.get(id=event_id)
        return render(request, 'core_app/e-join-organization.html', 
        {'event':event})

class ListAllTasks(GuardianView):
    def get(self, request):
        me = models.User.objects.get(id=self.user_id)

        filter, _ = models.GlobalTaskFilter.objects.get_or_create(
        user=me, organization=me.default)
        form  = forms.GlobalTaskFilterForm(instance=filter)

        assignments = me.assignments.all()
        tasks       = me.tasks.all()

        total = assignments.count() + tasks.count()
        
        assignments = assignments.filter(
        label__contains=filter.pattern, 
        done=filter.done)

        tasks = tasks.filter(
        label__contains=filter.pattern, 
        done=filter.done)

        count = assignments.count() + tasks.count()

        return render(request, 'core_app/list-all-tasks.html', 
        {'assignments': assignments, 'total': total, 'count': total, 
        'form': form, 'tasks': tasks})

    def post(self, request):
        me = models.User.objects.get(id=self.user_id)
        assignments = me.assignments.all()
        tasks       = me.tasks.all()
        total = assignments.count() + tasks.count()

        filter, _ = models.GlobalTaskFilter.objects.get_or_create(
        user=me, organization=me.default)
        form  = forms.GlobalFilterForm(request.POST, instance=filter)

        if not form.is_valid():
            return render(request, 'core_app/list-all-tasks.html', 
                {'assignments': assignments, 'form': form, 'total': total,
                    'count': total, 'tasks': tasks}, status=400)

        form.save()
        assignments = assignments.filter(
        label__contains=filter.pattern, 
        done=filter.done)

        tasks = tasks.filter(
        label__contains=filter.pattern, 
        done=filter.done)

        count = assignments.count() + tasks.count()

        return render(request, 'core_app/list-all-tasks.html', 
        {'assignments': assignments, 'form': form, 'tasks': tasks,
        'total': total, 'count': count})

class Find(GuardianView):
    def get(self, request):
        me    = models.User.objects.get(id=self.user_id)

        filter, _ = models.GlobalFilter.objects.get_or_create(
        user=me, organization=me.default)

        form  = forms.GlobalFilterForm(instance=filter)

        cards = Card.get_allowed_cards(me)
        posts = Post.get_allowed_posts(me)

        total = cards.count() + posts.count()

        cards = Card.collect_cards(cards, filter.pattern, filter.done)
        posts = Post.collect_posts(posts, filter.pattern, filter.done)
        count = cards.count() + posts.count()

        return render(request, 'core_app/find.html', 
        {'form': form, 'cards': cards, 'posts': posts,
        'total': total, 'count': count})

    def post(self, request):
        me        = models.User.objects.get(id=self.user_id)
        filter, _ = models.GlobalFilter.objects.get_or_create(
        user=me, organization=me.default)

        form  = forms.GlobalFilterForm(request.POST, instance=filter)

        cards = Card.get_allowed_cards(me)
        posts = Post.get_allowed_posts(me)

        total = cards.count() + posts.count()

        if not form.is_valid():
            return render(request, 'core_app/find.html', 
                {'form': form, 'cards': cards, 
                    'posts': posts, 'total': total,
                            'count': count}, status=400)
        form.save()

        cards = Card.collect_cards(cards, filter.pattern, filter.done)
        posts = Post.collect_posts(posts, filter.pattern, filter.done)

        count = cards.count() + posts.count()

        return render(request, 'core_app/find.html', 
        {'form': form, 'posts': posts, 'cards': cards,
        'total': total, 'count': count})


class ListClipboard(GuardianView):
    def get(self, request):
        user   = User.objects.get(id=self.user_id)
        cards = user.card_clipboard.all()
        lists = user.list_clipboard.all()
        posts = user.post_clipboard.all()
        total = cards.count() + lists.count() + posts.count()

        return render(request, 'core_app/list-clipboard.html', 
        {'user': user, 'cards': cards , 'posts': posts, 'lists': lists, 'total': total})














