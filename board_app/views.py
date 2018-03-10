from core_app.views import GuardianView, CashierView
from board_app.models import BoardFilter, ECreateBoard, Board, Pin, \
EPasteList, EUpdateBoard, EDeleteBoard, EBindBoardUser, EUnbindBoardUser
from django.shortcuts import render, redirect
from core_app.models import Clipboard, User, Organization
from django.http import HttpResponse
from django.views.generic import View
from django.db.models import Q
import core_app.models
import board_app.models
from core_app import ws
import card_app.models
from . import models
from . import forms
from . import models
from . import forms
import re

# Create your views here.

class ListBoards(CashierView):
    """
    """

    def get(self, request):
        user  = User.objects.get(id=self.user_id)

        total = user.boards.filter(
        organization__id=user.default.id)
        pins = user.pin_set.filter(organization=user.default)

        filter, _ = BoardFilter.objects.get_or_create(
        user=user, organization=user.default)

        boards = total.filter((Q(name__icontains=filter.pattern) | \
        Q(description__icontains=filter.pattern))) if filter.status else \
        total

        return render(request, 'board_app/list-boards.html', 
        {'boards': boards, 'total': total, 'user': user, 'pins': pins, 'filter': filter,
        'organization': user.default})

class CreateBoard(GuardianView):
    """
    """

    def get(self, request):
        form = forms.BoardForm()
        return render(request, 'board_app/create-board.html', 
        {'form':form})

    def post(self, request):
        form = forms.BoardForm(request.POST)

        if not form.is_valid():
            return render(request, 'board_app/create-board.html',
                        {'form': form, }, status=400)

        board       = form.save()
        user        = User.objects.get(id=self.user_id)
        board.owner = user

        board.members.add(user)
        board.organization = user.default
        board.save()

        event = ECreateBoard.objects.create(organization=user.default,
        board=board, user=user)

        # Organization admins should be notified?
        event.users.add(user)
        event.save()

        ws.client.publish('user%s' % user.id, 
            'subscribe board%s' % board.id, 0, False)

        ws.client.publish('user%s' % user.id, 
            'sound', 0, False)

        return redirect('board_app:list-boards')


class PinBoard(GuardianView):
    def get(self, request, board_id):
        user  = User.objects.get(id=self.user_id)
        board = Board.objects.get(id=board_id)
        pin   = Pin.objects.create(user=user, 
        organization=user.default, board=board)
        return redirect('board_app:list-pins')

class ManageUserBoards(GuardianView):
    def get(self, request, user_id):
        me   = User.objects.get(id=self.user_id)
        user = User.objects.get(id=user_id)

        boards = me.boards.filter(organization=me.default)
        excluded = boards.exclude(members=user)
        included = boards.filter(members=user)

        return render(request, 'board_app/manage-user-boards.html', 
        {'user': user, 'included': included, 'excluded': excluded,
        'me': me, 'organization': me.default,'form':forms.BoardSearchForm()})

    def post(self, request, user_id):
        user = User.objects.get(id=user_id)
        form = forms.BoardSearchForm(request.POST)

        me = User.objects.get(id=self.user_id)
        boards = me.boards.filter(organization=me.default)

        if not form.is_valid():
            return render(request, 'board_app/manage-user-boards.html', 
                {'user': user, 'included': included, 'excluded': excluded,
                    'me': me, 'organization': me.default, 
                        'form':forms.BoardSearchForm()}, status=400)

        boards = boards.filter(Q(
        name__contains=form.cleaned_data['name']) | Q(
        description__contains=form.cleaned_data['name']))

        # board.users.add(user)
        # board.save()

        # return redirect('board_app:list-user-tags', 
        # user_id=user.id)
        excluded = boards.exclude(members=user)
        included = boards.filter(members=user)

        return render(request, 'board_app/manage-user-boards.html', 
        {'user': user, 'included': included, 'excluded': excluded,
        'me': me, 'organization': me.default,'form':forms.BoardSearchForm()})

class ManageBoardUsers(GuardianView):
    def get(self, request, board_id):
        me = User.objects.get(id=self.user_id)
        board = Board.objects.get(id=board_id)

        included = board.members.all()

        users = me.default.users.all()
        excluded = users.exclude(boards=board)

        return render(request, 'board_app/manage-board-users.html', 
        {'included': included, 'excluded': excluded, 'board': board,
        'me': me, 'organization': me.default,'form':forms.UserSearchForm()})

    def post(self, request, board_id):
        form = forms.UserSearchForm(request.POST)

        me = User.objects.get(id=self.user_id)
        board = Board.objects.get(id=board_id)
        included = board.members.all()

        users = me.default.users.all()
        excluded = users.exclude(boards=board)

        if not form.is_valid():
            return render(request, 'board_app/manage-board-users.html', 
                {'included': included, 'excluded': excluded,
                    'me': me, 'organization': me.default, 'board': board,
                        'form':forms.UserSearchForm()}, status=400)

        included = included.filter(
        name__contains=form.cleaned_data['name'])

        excluded = excluded.filter(
        name__contains=form.cleaned_data['name'])

        return render(request, 'board_app/manage-board-users.html', 
        {'included': included, 'excluded': excluded, 'board': board,
        'me': me, 'organization': me.default,'form':forms.UserSearchForm()})

class PasteLists(GuardianView):
    def get(self, request, board_id):
        board        = Board.objects.get(id=board_id)
        user         = User.objects.get(id=self.user_id)
        clipboard, _ = Clipboard.objects.get_or_create(
        user=user, organization=user.default)

        lists = clipboard.lists.all()
        lists.update(ancestor=board)

        event = EPasteList.objects.create(
        organization=user.default, board=board, user=user)
        event.lists.add(*lists)
        event.users.add(*board.members.all())

        clipboard.lists.clear()

        ws.client.publish('board%s' % board.id, 
            'sound', 0, False)

        return redirect('list_app:list-lists', 
        board_id=board.id)

class UpdateBoard(GuardianView):
    def get(self, request, board_id):
        board = Board.objects.get(id=board_id)
        return render(request, 'board_app/update-board.html',
        {'board': board, 'form': forms.BoardForm(instance=board)})

    def post(self, request, board_id):
        record = Board.objects.get(id=board_id)
        form   = forms.BoardForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'board_app/update-board.html',
                        {'form': form, 'board':record, }, status=400)

        record.save()

        me    = User.objects.get(id=self.user_id)
        event = EUpdateBoard.objects.create(organization=me.default,
        board=record, user=me)
        event.users.add(*record.members.all())

        ws.client.publish('board%s' % record.id, 
            'sound', 0, False)

        return redirect('list_app:list-lists', 
        board_id=record.id)

class DeleteBoard(GuardianView):
    def get(self, request, board_id):
        board = Board.objects.get(id=board_id)
        form = forms.ConfirmBoardDeletionForm()

        return render(request, 'board_app/delete-board.html', 
        {'board': board, 'form': form})

    def post(self, request, board_id):
        board = Board.objects.get(id=board_id)

        form = forms.ConfirmBoardDeletionForm(request.POST, 
        confirm_token=board.name)

        if not form.is_valid():
            return render(request, 
                'board_app/delete-board.html', 
                    {'board': board, 'form': form}, status=400)

        user  = User.objects.get(id=self.user_id)

        event = EDeleteBoard.objects.create(organization=user.default,
        board_name=board.name, user=user)
        event.users.add(*board.members.all())

        ws.client.publish('board%s' % board.id, 
            'sound', 0, False)

        board.delete()

        return redirect('board_app:list-boards')

class SetupBoardFilter(GuardianView):
    def get(self, request, organization_id):
        filter = BoardFilter.objects.get(
        user__id=self.user_id, organization__id=organization_id)
        organization = Organization.objects.get(id=organization_id)

        return render(request, 'board_app/setup-board-filter.html', 
        {'form': forms.BoardFilterForm(instance=filter), 
        'organization': organization})

    def post(self, request, organization_id):
        record = BoardFilter.objects.get(
        organization__id=organization_id, user__id=self.user_id)

        form         = forms.BoardFilterForm(request.POST, instance=record)
        organization = Organization.objects.get(id=organization_id)

        if not form.is_valid():
            return render(request, 'board_app/setup-board-filter.html',
                   {'board': record, 'form': form, 
                        'organization': organization}, status=400)
        form.save()
        return redirect('board_app:list-boards')

class ListPins(GuardianView):
    def get(self, request):
        user = User.objects.get(id=self.user_id)
        pins = user.pin_set.filter(organization=user.default)
        return render(request, 'board_app/list-pins.html', 
        {'user': user, 'pins': pins})

class Unpin(GuardianView):
    def get(self, request, pin_id):
        pin = Pin.objects.get(id=pin_id)
        pin.delete()
        return redirect('board_app:list-pins')

class BindBoardUser(GuardianView):
    def get(self, request, board_id, user_id):
        user = User.objects.get(id=user_id)
        board = Board.objects.get(id=board_id)

        board.members.add(user)
        board.save()

        me    = User.objects.get(id=self.user_id)
        event = EBindBoardUser.objects.create(organization=me.default,
        board=board, user=me, peer=user)
        event.users.add(*board.members.all())

        ws.client.publish('board%s' % board.id, 
            'sound', 0, False)

        ws.client.publish('user%s' % user.id, 
            'subscribe board%s' % board.id, 0, False)

        ws.client.publish('user%s' % user.id, 
            'sound', 0, False)

        return HttpResponse(status=200)

class UnbindBoardUser(GuardianView):
    def get(self, request, board_id, user_id):
        # This code shows up in board_app.views?
        # something is odd.
        user = User.objects.get(id=user_id)
        board = Board.objects.get(id=board_id)
        board.members.remove(user)
        board.save()

        me = User.objects.get(id=self.user_id)
        event = EUnbindBoardUser.objects.create(organization=me.default,
        board=board, user=me, peer=user)
        event.users.add(*board.members.all())

        ws.client.publish('board%s' % board.id, 
            'sound', 0, False)

        ws.client.publish('user%s' % user.id, 
            'unsubscribe board%s' % board.id, 0, False)

        ws.client.publish('user%s' % user.id, 
            'sound', 0, False)

        return HttpResponse(status=200)



