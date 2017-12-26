from django.views.generic import View
from django.shortcuts import render, redirect
from core_app.views import GuardianView
from django.db.models import Q
import board_app.models
import card_app.models
import board_app.models
import list_app.models
from . import models
from . import forms
import core_app.models
from core_app import ws

# Create your views here.

class ListLists(GuardianView):
    """
    """

    def get(self, request, board_id):
        user = core_app.models.User.objects.get(id=self.user_id)
        board = board_app.models.Board.objects.get(id=board_id)
        total = board.lists.all()
        pins  = user.pin_set.all()

        filter, _ = models.ListFilter.objects.get_or_create(
        user=user, organization=user.default, board=board)

        lists = total.filter((Q(name__icontains=filter.pattern) | \
        Q(description__icontains=filter.pattern))) if filter.status else total

        return render(request, 'list_app/list-lists.html', 
        {'lists': lists, 'user': user, 'board': board, 'organization': user.default,
        'total': total, 'pins': pins, 'filter': filter})

class List(GuardianView):
    def get(self, request, list_id):
        list = models.List.objects.get(id=list_id)
        return render(request, 'list_app/list.html', 
        {'list':list})

class CreateList(GuardianView):
    """
    """

    def get(self, request, board_id):
        user  = core_app.models.User.objects.get(id=self.user_id)
        board = board_app.models.Board.objects.get(id=board_id)

        # list  = models.List.objects.create(owner=user, ancestor=board)
        form = forms.ListForm()
        return render(request, 'list_app/create-list.html', 
        {'form':form, 'board': board})

    def post(self, request, board_id):
        form = forms.ListForm(request.POST)

        if not form.is_valid():
            return render(request, 'list_app/create-list.html',
                        {'form': form, }, status=400)


        list          = form.save(commit=False)
        user          = core_app.models.User.objects.get(id=self.user_id)
        board         = board_app.models.Board.objects.get(id=board_id)
        list.owner    = user
        list.ancestor = board
        list.save()

        event = models.ECreateList.objects.create(organization=user.default,
        ancestor=list.ancestor, child=list, user=user)
        event.users.add(*list.ancestor.members.all())

        ws.client.publish('board%s' % list.ancestor.id, 
            'Card on: %s!' % list.ancestor.id, 0, False)

        return redirect('list_app:list-lists', board_id=board.id)

class DeleteList(GuardianView):
    def get(self, request, list_id):
        list = list_app.models.List.objects.get(id=list_id)

        user = core_app.models.User.objects.get(id=self.user_id)

        event = models.EDeleteList.objects.create(organization=user.default,
        ancestor=list.ancestor, child_name=list.name, user=user)
        event.users.add(*list.ancestor.members.all())

        list.delete()


        # Missing event.
        ws.client.publish('board%s' % list.ancestor.id, 
            'Card on: %s!' % list.ancestor.id, 0, False)

        return redirect('list_app:list-lists',
        board_id=list.ancestor.id)

class PinList(GuardianView):
    def get(self, request, list_id):
        user = core_app.models.User.objects.get(id=self.user_id)
        list = models.List.objects.get(id=list_id)
        pin  = board_app.models.Pin.objects.create(user=user, list=list)
        return redirect('board_app:list-pins')

class UpdateList(GuardianView):
    def get(self, request, list_id):
        list = models.List.objects.get(id=list_id)
        return render(request, 'list_app/update-list.html',
        {'list': list, 'form': forms.ListForm(instance=list)})

    def post(self, request, list_id):
        record  = models.List.objects.get(id=list_id)
        form    = forms.ListForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'list_app/update-list.html',
                        {'form': form, 'list':record, }, status=400)

        record.save()
        user = core_app.models.User.objects.get(id=self.user_id)

        event = models.EUpdateList.objects.create(organization=user.default,
        ancestor=record.ancestor, child=record, user=user)
        event.users.add(*record.ancestor.members.all())

        # Missing event.
        ws.client.publish('board%s' % record.ancestor.id, 
            'Card on: %s!' % record.ancestor.id, 0, False)

        return redirect('card_app:list-cards', 
        list_id=record.id)

class PasteCards(GuardianView):
    def get(self, request, list_id):
        list = models.List.objects.get(id=list_id)
        user = core_app.models.User.objects.get(id=self.user_id)

        for ind in user.card_clipboard.all():
            ind.ancestor = list
            ind.save()

        user.card_clipboard.clear()

        # missing event.
        ws.client.publish('board%s' % list.ancestor.id, 
            'Card on: %s!' % list.ancestor.id, 0, False)

        return redirect('card_app:list-cards', 
        list_id=list.id)

class CutList(GuardianView):
    def get(self, request, list_id):
        list          = models.List.objects.get(id=list_id)
        user          = core_app.models.User.objects.get(id=self.user_id)
        board         = list.ancestor

        ws.client.publish('board%s' % list.ancestor.id, 
            'Card on: %s!' % list.ancestor.id, 0, False)

        list.ancestor = None
        list.save()
        user.list_clipboard.add(list)

        # missing event.

        return redirect('list_app:list-lists', 
        board_id=board.id)

class CopyList(GuardianView):
    def get(self, request, list_id):
        list = models.List.objects.get(id=list_id)
        user = core_app.models.User.objects.get(id=self.user_id)
        copy = list.duplicate()
        user.list_clipboard.add(copy)

        # missing event.
        ws.client.publish('board%s' % list.ancestor.id, 
            'Card on: %s!' % list.ancestor.id, 0, False)

        return redirect('list_app:list-lists', 
        board_id=list.ancestor.id)

class ECreateList(GuardianView):
    def get(self, request, event_id):
        event = models.ECreateList.objects.get(id=event_id)
        return render(request, 'list_app/e-create-list.html', 
        {'event':event})

class EUpdateList(GuardianView):
    def get(self, request, event_id):
        event = models.EUpdateList.objects.get(id=event_id)
        return render(request, 'list_app/e-update-list.html', 
        {'event':event})

class EDeleteList(GuardianView):
    def get(self, request, event_id):
        event = models.EDeleteList.objects.get(id=event_id)
        return render(request, 'list_app/e-delete-list.html', 
        {'event':event})

class SetupListFilter(GuardianView):
    def get(self, request, board_id):
        user   = core_app.models.User.objects.get(id=self.user_id)

        filter = models.ListFilter.objects.get(
        user__id=self.user_id, organization__id=user.default.id,
        board__id=board_id)

        return render(request, 'list_app/setup-list-filter.html', 
        {'form': forms.ListFilterForm(instance=filter), 
        'board': filter.board})

    def post(self, request, board_id):
        user = core_app.models.User.objects.get(id=self.user_id)

        record = models.ListFilter.objects.get(
        organization__id=user.default.id, 
        user__id=self.user_id, board__id=board_id)

        form   = forms.ListFilterForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'list_app/setup-list-filter.html',
                   {'list': record, 'form': form, 
                        'board': record.board}, status=400)
        form.save()
        return redirect('list_app:list-lists', board_id=board_id)


class Done(GuardianView):
    def get(self, request, list_id):
        list      = models.List.objects.get(id=list_id)
        list.done = True
        list.save()

        user = core_app.models.User.objects.get(id=self.user_id)

        # lists in the clipboard cant be archived.
        event    = models.EArchiveList.objects.create(organization=user.default,
        ancestor=list.ancestor, child=list, user=user)

        users = list.ancestor.members.all()
        event.users.add(*users)

        # Missing event.
        ws.client.publish('board%s' % list.ancestor.id, 
            'List done on: %s!' % list.ancestor.id, 0, False)

        return redirect('list_app:list-lists', board_id=list.ancestor.id)

class EArchiveList(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.EArchiveList.objects.get(id=event_id)
        return render(request, 'list_app/e-archive-list.html', 
        {'event':event})

