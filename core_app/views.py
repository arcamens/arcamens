from django.views.generic import View
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import HttpResponse
from django.db.models import Q
from timeline_app.models import Organization
from board_app.models import Organization
from . import models
from . import forms
import timeline_app
import json

# Create your views here.
class AuthenticatedView(View):
    def dispatch(self, request, *args, **kwargs):
        try:
            self.user_id = request.session['user_id']
        except Exception:
            return self.error(request, *args, **kwargs)
        return self.delegate(request, *args, **kwargs)

    def delegate(self, request, *args, **kwargs):
        return super(AuthenticatedView, self).dispatch(
            request, *args, **kwargs)

    def error(self, request, *args, **kwargs):
        return redirect('site_app:index')

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
        'organizations': organizations, 'queues': json.dumps(queues)})

class SwitchOrganization(GuardianView):
    def get(self, request, organization_id):
        user = models.User.objects.get(id=self.user_id)
        user.default = models.Organization.objects.get(
        id=organization_id)
        user.save()
        return redirect('core_app:index')

class UpdateUserInformation(GuardianView):
    def get(self, request):
        return render(request, 'core_app/update-user-information.html', {})

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
        user = models.User.objects.get(id=self.user_id)
        organization = models.Organization.objects.get(id=organization_id)
        total = organization.users.all()

        form = forms.UserSearchForm()
        return render(request, 'core_app/list-users.html', 
        {'users': total, 'owner': organization.owner, 'total': total, 'form': form,
        'organization': organization})

    def post(self, request, organization_id):
        user = models.User.objects.get(id=self.user_id)
        organization = models.Organization.objects.get(id=organization_id)

        total = organization.users.all()
        form = forms.UserSearchForm(request.POST)

        if not form.is_valid():
            return render(request, 'core_app/list-users.html', 
                {'users': total, 'owner': organization.owner, 
                    'total': total, 'form': form,
                        'organization': organization}, status=400)
  
        total = organization.users.all()
        users = total.filter(Q(
        name__contains=form.cleaned_data['pattern'])| Q(
        email__contains=form.cleaned_data['pattern']))

        return render(request, 'core_app/list-users.html', 
        {'users': users, 'owner': organization.owner, 
        'total': total, 'form': form, 'organization': organization})

class ManageUserTags(GuardianView):
    def get(self, request, user_id):
        me = models.User.objects.get(id=self.user_id)
        user = models.User.objects.get(id=user_id)

        included = user.tags.all()
        excluded = models.Tag.objects.exclude(users=user)

        return render(request, 'core_app/manage-user-tags.html', 
        {'included': included, 'excluded': excluded, 'user': user,
        'organization': me.default,'form':forms.TagSearchForm()})

    def post(self, request, user_id):
        form = forms.TagSearchForm(request.POST)

        me = models.User.objects.get(id=self.user_id)
        user = models.User.objects.get(id=user_id)
        included = user.tags.all()
        excluded = models.Tag.objects.exclude(users=user)

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

class ListEvents(GuardianView):
    """
    """

    def get(self, request):
        user   = models.User.objects.get(id=self.user_id)
        events = user.default.events.all().order_by('-created')
        form   = forms.EventSearchForm()
        return render(request, 'core_app/list-events.html', 
        {'events': events, 'user': user, 
        'form': form, 'organization': user.default})

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

        return HttpResponse(status=200)

class BindUserTag(GuardianView):
    def get(self, request, user_id, tag_id):
        user = models.User.objects.get(id=user_id)
        tag = models.Tag.objects.get(id=tag_id)
        user.tags.add(tag)
        user.save()

        return HttpResponse(status=200)

class EventQueues(GuardianView):
    def get(self, request):
        user = models.User.objects.get(id=user_id)
        queues = user.timelines.values_list('id')
        data = simplejson.dumps(some_data_to_dump)
        return HttpResponse(data, content_type='application/json')




