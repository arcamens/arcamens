from django.views.generic import View
from list_app.models import ListFilter, EDeleteList, List, ECreateList, \
EUpdateList, EPasteCard, ECutList, ECopyList
from core_app.models import Clipboard, User
from board_app.models import Board, EPasteList
from list_app.models import ListPin
from django.shortcuts import render, redirect
from core_app.views import GuardianView
from django.http import HttpResponse
from django.conf import settings
from django.db.models import Q, F
from card_app.models import Card
import board_app.models
import board_app.models
import list_app.models
from . import models
from . import forms
import core_app.models
import json

# Create your views here.

class ListLists(GuardianView):
    """
    """

    def get(self, request, board_id):
        board = self.me.boards.get(id=board_id, organization=self.me.default)
        total = board.lists.all()

        boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        listpins = self.me.listpin_set.filter(organization=self.me.default)
        cardpins = self.me.cardpin_set.filter(organization=self.me.default)
        grouppins = self.me.grouppin_set.filter(organization=self.me.default)

        filter, _ = ListFilter.objects.get_or_create(
        user=self.me, organization=self.me.default, board=board)

        lists = total.filter((Q(name__icontains=filter.pattern) | \
        Q(description__icontains=filter.pattern))) if filter.status else \
        total

        return render(request, 'list_app/list-lists.html', 
        {'lists': lists, 'user': self.me, 'board': board, 'organization': self.me.default,
        'total': total, 'filter': filter, 'boardpins': boardpins,
        'listpins': listpins, 'cardpins': cardpins, 'grouppins': grouppins})

class CreateList(GuardianView):
    """
    """

    def get(self, request, board_id):
        board = self.me.boards.get(id=board_id, organization=self.me.default)

        form = forms.ListForm()
        return render(request, 'list_app/create-list.html', 
        {'form':form, 'board': board})

    def post(self, request, board_id):
        form = forms.ListForm(request.POST)
        board = self.me.boards.get(id=board_id, organization=self.me.default)

        if not form.is_valid():
            return render(request, 'list_app/create-list.html',
                        {'form': form, 'board': board}, status=400)


        list          = form.save(commit=False)
        board         = Board.objects.get(id=board_id)
        list.owner    = self.me
        list.ancestor = board
        list.save()

        event = ECreateList.objects.create(organization=self.me.default,
        ancestor=list.ancestor, child=list, user=self.me)
        event.dispatch(*list.ancestor.members.all())

        return redirect('list_app:list-lists', board_id=board_id)

class ConfirmListDeletion(GuardianView):
    def get(self, request, list_id):
        list = models.List.objects.get(id=list_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        return render(request, 'list_app/confirm-list-deletion.html', 
        {'list': list})

class DeleteList(GuardianView):
    def get(self, request, list_id):
        list = models.List.objects.get(id=list_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        event = EDeleteList.objects.create(organization=self.me.default,
        ancestor=list.ancestor, child_name=list.name, user=self.me)
        event.dispatch(*list.ancestor.members.all())

        list.delete()

        return redirect('list_app:list-lists',
        board_id=list.ancestor.id)

class PinList(GuardianView):
    def get(self, request, list_id):
        list = models.List.objects.get(id=list_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        pin  = ListPin.objects.create(user=self.me, 
        organization=self.me.default, list=list)
        return redirect('board_app:list-pins')

class UpdateList(GuardianView):
    def get(self, request, list_id):
        list = models.List.objects.get(id=list_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        return render(request, 'list_app/update-list.html',
        {'list': list, 'form': forms.ListForm(instance=list)})

    def post(self, request, list_id):
        record  = List.objects.get(id=list_id)
        form    = forms.ListForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'list_app/update-list.html',
                        {'form': form, 'list':record, }, status=400)

        record.save()

        event = EUpdateList.objects.create(organization=self.me.default,
        ancestor=record.ancestor, child=record, user=self.me)
        event.dispatch(*record.ancestor.members.all())

        return redirect('card_app:list-cards', 
        list_id=record.id)

class SelectDestinList(GuardianView):
    def get(self, request, list_id):
        list = models.List.objects.get(id=list_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)

        cards = clipboard.cards.all()
        total = cards.count() 

        return render(request, 'list_app/select-destin-list.html', 
        {'user': self.me, 'list': list, 'cards': cards,  'total': total})

class PasteCard(GuardianView):
    def get(self, request, list_id, card_id):
        list = models.List.objects.get(id=list_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)

        # Make sure the card is on the user clipboard.
        card = clipboard.cards.get(id=card_id)
        head = list.cards.order_by('-priority').first()

        priority      = head.priority if head else 0
        card.ancestor = list

        # Maybe not necessary just +1.
        card.priority = card.priority + priority
        card.save()

        event = EPasteCard(organization=self.me.default, 
        ancestor=list, user=self.me)

        event.save(hcache=False)
        event.cards.add(card)
    
        # Workers of the card dont need to be notified of this event
        # because them may not belong to the board at all.
        event.dispatch(*list.ancestor.members.all())
        event.save()

        clipboard.cards.remove(card)

        return redirect('list_app:select-destin-list', list_id=list.id)

class PasteAllCards(GuardianView):
    def get(self, request, list_id):
        list = models.List.objects.get(id=list_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)

        cards = clipboard.cards.all()

        if not cards.exists():
            return HttpResponse("There is no card on \
                the clipboard.", status=403)

        card = list.cards.order_by('-priority').first()
        priority = card.priority if card else 0
        cards.update(ancestor=list, priority=F('priority') + priority)

        event = EPasteCard(
        organization=self.me.default, ancestor=list, user=self.me)
        event.save(hcache=False)

        event.cards.add(*cards)
    
        # Workers of the card dont need to be notified of this event
        # because them may not belong to the board at all.
        event.dispatch(*list.ancestor.members.all())
        event.save()

        clipboard.cards.clear()

        return redirect('card_app:list-cards', 
        list_id=list.id)

class CutList(GuardianView):
    def get(self, request, list_id):
        list = models.List.objects.get(id=list_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        board = list.ancestor


        list.ancestor = None
        list.save()

        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)
        clipboard.lists.add(list)

        event = ECutList.objects.create(organization=self.me.default,
        ancestor=board, child=list, user=self.me)
        event.dispatch(*board.members.all())

        return redirect('list_app:list-lists', 
        board_id=board.id)

class CopyList(GuardianView):
    def get(self, request, list_id):
        list = models.List.objects.get(id=list_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        copy = list.duplicate()

        clipboard, _    = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)
        clipboard.lists.add(copy)

        event = ECopyList.objects.create(organization=self.me.default,
        ancestor=list.ancestor, child=list, user=self.me)
        event.dispatch(*list.ancestor.members.all())

        return redirect('list_app:list-lists', 
        board_id=list.ancestor.id)

class SetupListFilter(GuardianView):
    def get(self, request, board_id):
        # allow to have a filter only if i belong to the board.
        filter = ListFilter.objects.get(
        user__id=self.user_id, organization__id=self.me.default.id,
        board__id=board_id, board__members=self.me)

        return render(request, 'list_app/setup-list-filter.html', 
        {'form': forms.ListFilterForm(instance=filter), 
        'board': filter.board})

    def post(self, request, board_id):
        record = ListFilter.objects.get(
        user__id=self.user_id, organization__id=self.me.default.id,
        board__id=board_id, board__members=self.me)

        form = forms.ListFilterForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'list_app/setup-list-filter.html',
                   {'list': record, 'form': form, 
                        'board': record.board}, status=400)
        form.save()
        return redirect('list_app:list-lists', board_id=board_id)

class UndoClipboard(GuardianView):
    def get(self, request, list_id):
        list = models.List.objects.get(id=list_id,
        list_clipboard_users__organization=self.me.default,
        list_clipboard_users__user=self.me)

        event0 = list.e_copy_list1.last()
        event1 = list.e_cut_list1.last()

        # Then it is a copy because there is no event
        # mapped to it. A copy contains no e_copy_list1 nor
        # e_cut_list1.
        if not (event0 or event1):
            list.delete()
        else:
            self.undo_cut(event1)

        return redirect('core_app:list-clipboard')

    def undo_cut(self, event):
        event.child.ancestor = event.ancestor
        event.child.save()

        event1 = EPasteList(organization=self.me.default, 
        board=event.ancestor, user=self.me)

        event1.save(hcache=False)
        event1.lists.add(event.child)
        event1.dispatch(*event.ancestor.members.all())
        event1.save()
        
        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)

        clipboard.lists.remove(event.child)

class ListLink(GuardianView):
    """
    """

    def get(self, request, list_id):
        record = models.List.objects.get(id=list_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        listpins = self.me.listpin_set.filter(organization=self.me.default)
        cardpins = self.me.cardpin_set.filter(organization=self.me.default)
        grouppins = self.me.grouppin_set.filter(organization=self.me.default)

        organizations = self.me.organizations.exclude(id=self.me.default.id)

        return render(request, 'list_app/list-link.html', 
        {'list': record, 'user': self.me, 'organization': self.me.default,
        'default': self.me.default, 'organizations': organizations, 'boardpins': boardpins,
        'listpins': listpins, 'cardpins': cardpins, 'grouppins': grouppins,
        'settings': settings})

class Unpin(GuardianView):
    def get(self, request, pin_id):
        pin = self.me.listpin_set.get(id=pin_id)
        pin.delete()
        return redirect('board_app:list-pins')










