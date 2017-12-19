from django.views.generic import View
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import HttpResponse
from django.db.models import Q
from timeline_app.models import Opus
from board_app.models import Labor
from . import models
from . import forms
import timeline_app

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

        try:
            user.default.labor
        except Exception as e:
            return redirect('timeline_app:index')
        else:
            return redirect('board_app:index')

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

        organization = Opus.objects.create(
        name=form.cleaned_data['name'], type='Opus', owner=user) \
        if form.cleaned_data['type'] == '1' else \
        Labor.objects.create(name=form.cleaned_data['name'], 
        type='Labor', owner=user)

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

class ListUserTags(GuardianView):
    def get(self, request, user_id):
        user      = models.User.objects.get(id=user_id)
        me        = models.User.objects.get(id=self.user_id)
        timelines = user.timelines.filter(organization=me.default)

        return render(request, 'core_app/list-user-tags.html', 
        {'timelines': timelines, 'user': user, 'me': me,
        'organization': me.default, 'tags': user.tags.all()})





