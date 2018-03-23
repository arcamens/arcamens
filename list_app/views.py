from django.views.generic import View
from list_app.models import ListFilter, EDeleteList, List, ECreateList, \
EUpdateList, EPasteCard, ECutList, ECopyList
from core_app.models import Clipboard, User
from board_app.models import Board, Pin, EPasteList
from django.shortcuts import render, redirect
from core_app.views import GuardianView
from django.http import HttpResponse
from django.conf import settings
from django.db.models import Q
import board_app.models
import card_app.models
import board_app.models
import list_app.models
from . import models
from . import forms
import core_app.models
from core_app import ws
import json

# Create your views here.

class ListLists(GuardianView):
    """
    """

    def get(self, request, board_id):
        user = User.objects.get(id=self.user_id)
        board = Board.objects.get(id=board_id)
        total = board.lists.all()
        pins  = user.pin_set.filter(organization=user.default)

        filter, _ = ListFilter.objects.get_or_create(
        user=user, organization=user.default, board=board)

        lists = total.filter((Q(name__icontains=filter.pattern) | \
        Q(description__icontains=filter.pattern))) if filter.status else \
        total

        return render(request, 'list_app/list-lists.html', 
        {'lists': lists, 'user': user, 'board': board, 'organization': user.default,
        'total': total, 'pins': pins, 'filter': filter})

class CreateList(GuardianView):
    """
    """

    def get(self, request, board_id):
        user  = User.objects.get(id=self.user_id)
        board = Board.objects.get(id=board_id)

        # list  = models.List.objects.create(owner=user, ancestor=board)
        form = forms.ListForm()
        return render(request, 'list_app/create-list.html', 
        {'form':form, 'board': board})

    def post(self, request, board_id):
        form = forms.ListForm(request.POST)
        board = Board.objects.get(id=board_id)

        if not form.is_valid():
            return render(request, 'list_app/create-list.html',
                        {'form': form, 'board': board}, status=400)


        list          = form.save(commit=False)
        user          = User.objects.get(id=self.user_id)
        board         = Board.objects.get(id=board_id)
        list.owner    = user
        list.ancestor = board
        list.save()

        event = ECreateList.objects.create(organization=user.default,
        ancestor=list.ancestor, child=list, user=user)
        event.users.add(*list.ancestor.members.all())

        ws.client.publish('board%s' % list.ancestor.id, 
            'sound', 0, False)

        return redirect('list_app:list-lists', board_id=board.id)

class DeleteList(GuardianView):
    def get(self, request, list_id):
        list = List.objects.get(id=list_id)
        user = User.objects.get(id=self.user_id)

        event = EDeleteList.objects.create(organization=user.default,
        ancestor=list.ancestor, child_name=list.name, user=user)
        event.users.add(*list.ancestor.members.all())

        list.delete()


        # Missing event.
        ws.client.publish('board%s' % list.ancestor.id, 
            'sound', 0, False)

        return redirect('list_app:list-lists',
        board_id=list.ancestor.id)

class PinList(GuardianView):
    def get(self, request, list_id):
        user = User.objects.get(id=self.user_id)
        list = List.objects.get(id=list_id)
        pin  = Pin.objects.create(user=user, 
        organization=user.default, list=list)
        return redirect('board_app:list-pins')

class UpdateList(GuardianView):
    def get(self, request, list_id):
        list = List.objects.get(id=list_id)
        return render(request, 'list_app/update-list.html',
        {'list': list, 'form': forms.ListForm(instance=list)})

    def post(self, request, list_id):
        record  = List.objects.get(id=list_id)
        form    = forms.ListForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'list_app/update-list.html',
                        {'form': form, 'list':record, }, status=400)

        record.save()
        user = User.objects.get(id=self.user_id)

        event = EUpdateList.objects.create(organization=user.default,
        ancestor=record.ancestor, child=record, user=user)
        event.users.add(*record.ancestor.members.all())

        # Missing event.
        ws.client.publish('board%s' % record.ancestor.id, 
            'sound', 0, False)

        return redirect('card_app:list-cards', 
        list_id=record.id)

class PasteCards(GuardianView):
    def get(self, request, list_id):
        list         = List.objects.get(id=list_id)
        user         = User.objects.get(id=self.user_id)
        clipboard, _ = Clipboard.objects.get_or_create(
        user=user, organization=user.default)

        cards = clipboard.cards.all()

        if not cards.exists():
            return HttpResponse("There is no card on \
                the clipboard.", status=403)

        cards.update(ancestor=list)

        event = EPasteCard(
        organization=user.default, ancestor=list, user=user)
        event.save(hcache=False)

        event.cards.add(*cards)
    
        # Workers of the card dont need to be notified of this event
        # because them may not belong to the board at all.
        event.users.add(*list.ancestor.members.all())
        event.save()

        clipboard.cards.clear()

        # missing event.
        ws.client.publish('board%s' % list.ancestor.id, 
            'sound', 0, False)

        return redirect('card_app:list-cards', 
        list_id=list.id)

class CutList(GuardianView):
    def get(self, request, list_id):
        list  = List.objects.get(id=list_id)
        user  = User.objects.get(id=self.user_id)
        board = list.ancestor

        ws.client.publish('board%s' % list.ancestor.id, 
            'sound', 0, False)

        list.ancestor = None
        list.save()

        clipboard, _ = Clipboard.objects.get_or_create(
        user=user, organization=user.default)
        clipboard.lists.add(list)

        event = ECutList.objects.create(organization=user.default,
        ancestor=board, child=list, user=user)
        event.users.add(*board.members.all())

        return redirect('list_app:list-lists', 
        board_id=board.id)

class CopyList(GuardianView):
    def get(self, request, list_id):
        list = List.objects.get(id=list_id)
        user = User.objects.get(id=self.user_id)
        copy = list.duplicate()

        clipboard, _    = Clipboard.objects.get_or_create(
        user=user, organization=user.default)
        clipboard.lists.add(copy)

        event = ECopyList.objects.create(organization=user.default,
        ancestor=list.ancestor, child=list, user=user)
        event.users.add(*list.ancestor.members.all())

        ws.client.publish('board%s' % list.ancestor.id, 
            'sound', 0, False)

        return redirect('list_app:list-lists', 
        board_id=list.ancestor.id)

class SetupListFilter(GuardianView):
    def get(self, request, board_id):
        user = User.objects.get(id=self.user_id)

        filter = ListFilter.objects.get(
        user__id=self.user_id, organization__id=user.default.id,
        board__id=board_id)

        return render(request, 'list_app/setup-list-filter.html', 
        {'form': forms.ListFilterForm(instance=filter), 
        'board': filter.board})

    def post(self, request, board_id):
        user   = User.objects.get(id=self.user_id)
        record = ListFilter.objects.get(
        organization__id=user.default.id, 
        user__id=self.user_id, board__id=board_id)

        form   = forms.ListFilterForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'list_app/setup-list-filter.html',
                   {'list': record, 'form': form, 
                        'board': record.board}, status=400)
        form.save()
        return redirect('list_app:list-lists', board_id=board_id)

class UndoClipboard(GuardianView):
    def get(self, request, list_id):
        list = List.objects.get(id=list_id)
        user = User.objects.get(id=self.user_id)
        event0 = list.e_copy_list1.last()
        event1 = list.e_cut_list1.last()

        # Then it is a copy because there is no event
        # mapped to it. A copy contains no e_copy_list1 nor
        # e_cut_list1.
        if not (event0 and event1):
            list.delete()
        else:
            self.undo_cut(event1)

        return redirect('core_app:list-clipboard')

    def undo_cut(self, event):
        user = User.objects.get(id=self.user_id)

        event.child.ancestor = event.ancestor
        event.child.save()

        event1 = EPasteList(
        organization=user.default, board=event.ancestor, user=user)
        event1.save(hcache=False)
        event1.lists.add(event.child)
        event1.users.add(*event.ancestor.members.all())
        event1.save()
        
        clipboard, _ = Clipboard.objects.get_or_create(
        user=user, organization=user.default)

        clipboard.lists.remove(event.child)
        event.ancestor.ws_sound()

class ListLink(GuardianView):
    """
    """

    def get(self, request, list_id):
        record = List.objects.get(id=list_id)

        user = core_app.models.User.objects.get(id=self.user_id)
        pins = user.pin_set.all()
        organizations = user.organizations.exclude(id=user.default.id)

        queues = list(map(lambda ind: 'timeline%s' % ind, 
        user.timelines.values_list('id')))

        queues.extend(map(lambda ind: 'board%s' % ind, 
        user.boards.values_list('id')))

        return render(request, 'list_app/list-link.html', 
        {'list': record, 'user': user, 'pins': pins,
        'default': user.default, 'organizations': organizations, 
        'queues': json.dumps(queues), 'settings': settings})



