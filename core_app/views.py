from core_app.models import OrganizationService, Organization, User, \
UserFilter, Tag, EDeleteTag, ECreateTag, EUnbindUserTag, EBindUserTag, \
Invite, EInviteUser, EJoinOrganization, GlobalTaskFilter, \
GlobalFilter, Clipboard, Event
from django.core.paginator import Paginator, EmptyPage
from django.utils.dateparse import parse_datetime
from django.shortcuts import render, redirect
from slock.views import AuthenticatedView
from django.views.generic import View
from django.core.mail import send_mail
from django.http import HttpResponse
from card_app.models import Card
from post_app.models import Post
from django.db.models import Q
from django.urls import reverse
from django.conf import settings
from traceback import print_exc
from itertools import chain
from core_app import ws
from . import models
from . import forms
import core_app.export
import random
import json

# Create your views here.

class GuardianView(AuthenticatedView):
    def delegate(self, request, *args, **kwargs):
        user = User.objects.get(id=self.user_id)

        if not user.default.owner.enabled:
            return HttpResponse("Disabled organization \
                account!", status=400)

        return super(GuardianView, self).delegate(
            request, *args, **kwargs)

class DisabledAccount(View):
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
            

class CashierView(AuthenticatedView):
    def delegate(self, request, *args, **kwargs):
        user = User.objects.get(id=self.user_id)

        if not user.default.owner.enabled:
            return render(request, 'core_app/disabled-account.html', 
                {'user': user, 'organizations': user.default})

        return super(CashierView, self).delegate(
            request, *args, **kwargs)
        
class Index(AuthenticatedView):
    """
    """

    def get(self, request):
        user = User.objects.get(id=self.user_id)
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

class SwitchOrganization(AuthenticatedView):
    def get(self, request, organization_id):
        user = User.objects.get(id=self.user_id)

        ws.client.publish('user%s' % user.id, 
            'unsubscribe organization%s' % user.default.id, 0, False)

        user.default = Organization.objects.get(
        id=organization_id)

        ws.client.publish('user%s' % user.id, 
            'subscribe organization%s' % user.default.id, 0, False)

        user.save()
        # When user updates organization, it tells all the other
        # tabs to restart the UI.
        ws.client.publish('user%s' % user.id, 
            'restart', 0, False)

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
        user.save()
        return redirect('core_app:index')

class UpdateOrganization(GuardianView):
    def get(self, request, organization_id):
        organization = Organization.objects.get(id=organization_id)
        return render(request, 
        'core_app/update-organization.html',{'organization': organization, 
        'form': forms.UpdateOrganizationForm(instance=organization)})

    def post(self, request, organization_id):
        record  = Organization.objects.get(id=organization_id)
        form    = forms.UpdateOrganizationForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'core_app/update-organization.html',
                {'organization': record, 'form': form})

        form.save()

        return redirect('core_app:index')

class DeleteOrganization(GuardianView):
    def get(self, request,  organization_id):
        organization = Organization.objects.get(id = organization_id)
        user         = User.objects.get(id=self.user_id)

        if user.owned_organizations.count() == 1:
            return HttpResponse("You can't delete \
                this organization..", status=400)

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

        form  = forms.UserFilterForm(request.POST, instance=filter)

        if not form.is_valid():
            return render(request, 'core_app/list-users.html', 
                {'count': 0, 'owner': organization.owner, 
                    'total': total, 'form': form,
                        'organization': organization}, status=400)
  
        form.save()
        users = User.collect_users(users, filter.pattern)
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

        return render(request, 'core_app/manage-user-tags.html', 
        {'included': included, 'excluded': excluded, 'user': user,
        'me': me,'form':forms.TagSearchForm()})

    def post(self, request, user_id):
        form = forms.TagSearchForm(request.POST)

        me = User.objects.get(id=self.user_id)
        user = User.objects.get(id=user_id)

        included = user.tags.filter(organization=me.default)
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
        user      = User.objects.get(id=self.user_id)
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
        user   = User.objects.get(id=self.user_id)
        events = user.events.filter(organization=user.default)
        events = events.order_by('-created')
        count = events.count()
        events = events.values('html', 'id')

        return render(request, 'core_app/list-events.html', 
        {'events': events, 'user': user, 
         'organization': user.default, 'count': count})

class ListTags(GuardianView):
    def get(self, request):
        user      = User.objects.get(id=self.user_id)
        tags = user.default.tags.all()
        form = forms.TagSearchForm()

        return render(request, 'core_app/list-tags.html', 
        {'tags': tags, 'form': form, 'user': user, 
        'organization': user.default})

    def post(self, request):
        user = User.objects.get(id=self.user_id)
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
        user  = User.objects.get(id=self.user_id)
        tag   = Tag.objects.get(id=tag_id)

        event = EDeleteTag.objects.create(
        organization=user.default, user=user, tag_name=tag.name)
        tag.delete()

        users = user.default.users.all()
        event.users.add(*users)
        ws.client.publish('organization%s' % user.default.id, 
            'sound', 0, False)

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
        event.users.add(*users)

        ws.client.publish('organization%s' % user.default.id, 
            'sound', 0, False)

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
        event.users.add(*users)

        ws.client.publish('organization%s' % me.default.id, 
            'sound', 0, False)

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
        event.users.add(*users)

        ws.client.publish('organization%s' % me.default.id, 
            'sound', 0, False)

        return HttpResponse(status=200)

class EventQueues(GuardianView):
    def get(self, request):
        user = User.objects.get(id=user_id)
        queues = user.timelines.values_list('id')
        data = simplejson.dumps(some_data_to_dump)
        return HttpResponse(data, content_type='application/json')

class InviteOrganizationUser(GuardianView):
    def get(self, request, organization_id):
        user         = User.objects.get(id=self.user_id)
        organization = Organization.objects.get(id=organization_id)

        return render(request, 'core_app/invite-organization-user.html', 
        {'form': forms.OrganizationInviteForm(), 'user': user})

    def post(self, request, organization_id):
        organization = Organization.objects.get(id=organization_id)
        form         = forms.OrganizationInviteForm(request.POST)

        if not form.is_valid():
            return render(request, 'core_app/invite-organization-user.html',
                  {'form': form, 'organization': organization}, status=400)

        email = form.cleaned_data['email']

        # If the user doesn't exist
        # we send him an email invite.
        me = User.objects.get(id=self.user_id)

        # Create the user anyway, but make it disabled
        # the user need to fill information first.
        user, _  = User.objects.get_or_create(email=email)
        
        # need to be improved.
        token  = 'invite%s' % random.randint(1000, 10000)
        invite = Invite.objects.create(
        organization=organization, user=user, token=token)

        event = EInviteUser.objects.create(
        organization=organization, user=me, peer=user)

        event.users.add(me, user)

        url = reverse('core_app:join-organization', kwargs={
        'organization_id': organization.id, 'token': token})

        url = '%s%s' % (settings.LOCAL_ADDR, url)
        msg = 'You were invited to %s by %s.' % (organization.name, me.name)

        send_mail(msg, '%s %s' % (organization.name, 
        url), settings.EMAIL_HOST_USER, [email], fail_silently=False)

        ws.client.publish('organization%s' % organization.id, 
            'sound', 0, False)

        return redirect('core_app:list-users', 
        organization_id=organization_id)

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

        # validates the invite.
        invite.delete()

        invites = Invite.objects.filter(
        organization=organization, user=invite.user)
        invites.delete()

        event = EJoinOrganization.objects.create(organization=organization, 
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
        invite = Invite.objects.get(    
        organization__id=organization_id, token=token)

        form = forms.UserForm(instance=invite.user)
        return render(request, 'core_app/signup-from-invite.html', 
        {'form': form, 'organization': invite.organization, 'token': token})

    def post(self, request, organization_id, token):
        invite = Invite.objects.get(    
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

class ListAllTasks(GuardianView):
    def get(self, request):
        me        = User.objects.get(id=self.user_id)
        filter, _ = GlobalTaskFilter.objects.get_or_create(
        user=me, organization=me.default)

        form        = forms.GlobalTaskFilterForm(instance=filter)
        posts = me.assignments.filter(
        ancestor__organization=me.default)

        cards = me.tasks.filter(
        ancestor__ancestor__organization=me.default)

        total = posts.count() + cards.count()
        
        cards = Card.collect_cards(cards, 
        filter.pattern, filter.done)

        posts = Post.collect_posts(posts, 
        filter.pattern, filter.done)

        count = posts.count() + cards.count()
        cards = cards.only('done', 'label', 'id')
        posts = posts.only('done', 'label', 'id')

        # If i instantiate the form here it stops working
        # correctly when filtering the cards/posts
        # form  = forms.GlobalTaskFilterForm(instance=filter)
        tasks = chain(cards, posts)

        return render(request, 'core_app/list-all-tasks.html', 
        {'total': total, 'count': count, 
        'form': form, 'tasks': tasks})

    def post(self, request):
        me        = User.objects.get(id=self.user_id)
        filter, _ = GlobalTaskFilter.objects.get_or_create(
        user=me, organization=me.default)

        form = forms.GlobalTaskFilterForm(request.POST, instance=filter)
        posts = me.assignments.filter(ancestor__organization=me.default)

        cards = me.tasks.filter(
        ancestor__ancestor__organization=me.default)

        total = posts.count() + cards.count()

        if not form.is_valid():
            return render(request, 'core_app/list-all-tasks.html', 
                {'form': form, 'total': total,
                    'count': 0}, status=400)

        form.save()

        cards = Card.collect_cards(cards, 
        filter.pattern, filter.done)

        posts = Post.collect_posts(posts, 
        filter.pattern, filter.done)

        count = posts.count() + cards.count()
        cards = cards.only('done', 'label', 'id')
        posts = posts.only('done', 'label', 'id')

        tasks = chain(cards, posts)

        return render(request, 'core_app/list-all-tasks.html', 
        {'form': form, 'tasks': tasks, 'total': total, 'count': count})

class Find(GuardianView):
    def get(self, request):
        me    = User.objects.get(id=self.user_id)

        filter, _ = GlobalFilter.objects.get_or_create(
        user=me, organization=me.default)
        form  = forms.GlobalFilterForm(instance=filter)

        posts = Post.get_allowed_posts(me)
        cards = Card.get_allowed_cards(me)
        total = posts.count() + cards.count()

        posts = Post.collect_posts(posts, filter.pattern, filter.done)
        cards = Card.collect_cards(cards, filter.pattern, filter.done)
        count = posts.count() + cards.count()

        cards = cards.only('done', 'label', 'id')
        posts = posts.only('done', 'label', 'id')
        elems = chain(cards, posts)

        return render(request, 'core_app/find.html', 
        {'form': form, 'elems':  elems, 'total': total, 'count': count})

    def post(self, request):
        me        = User.objects.get(id=self.user_id)
        filter, _ = GlobalFilter.objects.get_or_create(
        user=me, organization=me.default)

        form  = forms.GlobalFilterForm(request.POST, instance=filter)

        posts = Post.get_allowed_posts(me)
        cards = Card.get_allowed_cards(me)
        total = posts.count() + cards.count()

        if not form.is_valid():
            return render(request, 'core_app/find.html', 
                {'form': form, 'total': total, 'count': 0}, status=400)
        form.save()

        posts = Post.collect_posts(posts, filter.pattern, filter.done)
        cards = Card.collect_cards(cards, filter.pattern, filter.done)
        count = posts.count() + cards.count()

        cards = cards.only('done', 'label', 'id')
        posts = posts.only('done', 'label', 'id')
        elems = chain(cards, posts)

        return render(request, 'core_app/find.html', 
        {'form': form, 'elems':  elems, 'total': total, 'count': count})


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

        end    = parse_datetime(str(form.cleaned_data['end']))
        start  = parse_datetime(str(form.cleaned_data['start']))
        events = user.seen_events.filter(created__lte=end,
        created__gte=start, organization=user.default)

        events = events.order_by('-created')
        count  = events.count()
        events = events.values('html')
        return render(request, 'core_app/list-logs.html', 
        {'user': user, 'form': form, 'events':events, 
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













