from core_app.views import GuardianView
from board_app.models import ECreateBoard, Board, BoardPin, \
EPasteList, EUpdateBoard, EDeleteBoard, EBindBoardUser, EUnbindBoardUser, Board
from django.shortcuts import render, redirect
from core_app.models import Clipboard, User, Organization
from django.http import HttpResponse
from django.views.generic import View
from django.conf import settings
from django.db.models import Q
import core_app.models
import board_app.models
import card_app.models
from . import models
from . import forms
import json

import re

# Create your views here.

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
        board.admins.add(user)
        board.organization = user.default
        board.save()

        event = ECreateBoard.objects.create(organization=user.default,
        board=board, user=user)

        # Organization admins should be notified?
        event.dispatch(user)
        event.save()

        # user.ws_sound()
        user.ws_subscribe(board, target=user)

        return redirect('core_app:list-nodes')


class PinBoard(GuardianView):
    def get(self, request, board_id):
        user  = User.objects.get(id=self.user_id)
        board = Board.objects.get(id=board_id)

        pin   = BoardPin.objects.create(user=user, 
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
                        'form':form}, status=400)

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
        'me': me, 'organization': me.default,'form':form})

class ManageBoardMembers(GuardianView):
    def get(self, request, board_id):
        me = User.objects.get(id=self.user_id)
        board = Board.objects.get(id=board_id)

        included = board.members.all()
        users = me.default.users.all()
        excluded = users.exclude(boards=board)

        total = included.count() + excluded.count()

        return render(request, 'board_app/manage-board-members.html', 
        {'included': included, 'excluded': excluded, 'board': board,
        'me': me, 'count': total, 'total': total, 
        'form':forms.UserSearchForm()})

    def post(self, request, board_id):
        sqlike = User.from_sqlike()
        form = forms.UserSearchForm(request.POST, sqlike=sqlike)

        me = User.objects.get(id=self.user_id)
        board = Board.objects.get(id=board_id)
        included = board.members.all()

        users = me.default.users.all()
        excluded = users.exclude(boards=board)
        total = included.count() + excluded.count()

        if not form.is_valid():
            return render(request, 'board_app/manage-board-members.html', 
                {'me': me, 'board': board, 'total': total, 'count': 0,
                        'form':form}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)
        count = included.count() + excluded.count()

        return render(request, 'board_app/manage-board-members.html', 
        {'included': included, 'excluded': excluded, 'board': board,
        'me': me, 'total': total, 'count': count, 'form':form})

class ManageBoardAdmins(GuardianView):
    def get(self, request, board_id):
        me = User.objects.get(id=self.user_id)
        board = Board.objects.get(id=board_id)

        included = board.admins.all()
        excluded = board.members.exclude(id__in=included)

        total = included.count() + excluded.count()

        return render(request, 'board_app/manage-board-admins.html', 
        {'included': included, 'excluded': excluded, 'board': board,
        'me': me, 'count': total, 'total': total, 
        'form':forms.UserSearchForm()})

    def post(self, request, board_id):
        me = User.objects.get(id=self.user_id)

        sqlike = User.from_sqlike()
        form = forms.UserSearchForm(request.POST, sqlike=sqlike)

        board = Board.objects.get(id=board_id)

        included = board.admins.all()
        excluded = board.members.exclude(id__in=included)

        total = included.count() + excluded.count()

        if not form.is_valid():
            return render(request, 'board_app/manage-board-admins.html', 
                {'me': me, 'board': board, 'total': total, 'count': 0,
                        'form':form}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)
        count = included.count() + excluded.count()

        return render(request, 'board_app/manage-board-admins.html', 
        {'included': included, 'excluded': excluded, 'board': board,
        'me': me, 'total': total, 'count': count, 'form':form})

class PasteLists(GuardianView):
    def get(self, request, board_id):
        board        = Board.objects.get(id=board_id)
        user         = User.objects.get(id=self.user_id)
        clipboard, _ = Clipboard.objects.get_or_create(
        user=user, organization=user.default)

        lists = clipboard.lists.all()

        if not lists.exists():
            return HttpResponse("There is no list on \
                the clipboard.", status=403)

        lists.update(ancestor=board)

        event = EPasteList.objects.create(
        organization=user.default, board=board, user=user)
        event.lists.add(*lists)
        event.dispatch(*board.members.all())
        event.save()

        clipboard.lists.clear()

        user.ws_sound(board)

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
        event.dispatch(*record.members.all())

        me.ws_sound(record)

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
        event.dispatch(*board.members.all())

        # Need to unsubscribe or it may misbehave.
        user.ws_sound(board)
        user.ws_unsubscribe(board, target=board)

        board.delete()

        return redirect('core_app:list-nodes')

class ListPins(GuardianView):
    def get(self, request):
        user = User.objects.get(id=self.user_id)
        boardpins = user.boardpin_set.filter(organization=user.default)
        listpins = user.listpin_set.filter(organization=user.default)
        cardpins = user.cardpin_set.filter(organization=user.default)
        timelinepins = user.timelinepin_set.filter(organization=user.default)

        return render(request, 'board_app/list-pins.html', 
        {'user': user, 'boardpins': boardpins, 'listpins': listpins, 
        'cardpins': cardpins, 'timelinepins': timelinepins})

class Unpin(GuardianView):
    def get(self, request, pin_id):
        pin = BoardPin.objects.get(id=pin_id)
        pin.delete()
        return redirect('board_app:list-pins')

class BindBoardUser(GuardianView):
    def get(self, request, board_id, user_id):
        user     = User.objects.get(id=user_id)
        board    = Board.objects.get(id=board_id)
        me       = User.objects.get(id=self.user_id)
        me_admin = board.admins.filter(id=me.id).exists()

        if not me_admin:
            return HttpResponse("Just admins can add users!", status=403)

        board.members.add(user)
        board.save()

        event = EBindBoardUser.objects.create(organization=me.default,
        board=board, user=me, peer=user)
        event.dispatch(*board.members.all())

        me.ws_sound(board)
        me.ws_subscribe(board, target=user)

        # Warrant the user will receive the sound event
        # because we cant control the order in which
        # data flows to the different queues.
        me.ws_sound(target=user)

        return HttpResponse(status=200)

class UnbindBoardUser(GuardianView):
    def get(self, request, board_id, user_id):
        user = User.objects.get(id=user_id)
        board = Board.objects.get(id=board_id)

        if board.owner == user:
            return HttpResponse("You can't remove \
                the board owner!", status=403)

        me       = User.objects.get(id=self.user_id)
        is_admin = board.admins.filter(id=user.id).exists()
        me_admin = board.admins.filter(id=self.user_id).exists()

        me_owner = board.owner == me

        # In order to remove an user it is necessary to be an admin.
        if not me_admin:
            return HttpResponse("Just admins can do that!", status=403)

        if is_admin and not me_owner:
            return HttpResponse("Just the owner can do that!", status=403)

        # We make sure the user is no longer an admin at all.
        board.members.remove(user)
        board.admins.remove(user)
        board.save()

        event = EUnbindBoardUser.objects.create(organization=me.default,
        board=board, user=me, peer=user)
        event.dispatch(*board.members.all())

        me.ws_sound(board)
        me.ws_unsubscribe(board, target=user)
        me.ws_sound(user)

        return HttpResponse(status=200)

class BindBoardAdmin(GuardianView):
    def get(self, request, board_id, user_id):
        me    = User.objects.get(id=self.user_id)
        board = Board.objects.get(id=board_id)

        # Just the owner can add/remove admins.
        if board.owner != me:
            return HttpResponse("Just the owner can do that!", status=403)

        user = User.objects.get(id=user_id)
        board.admins.add(user)
        board.save()

        # event = EBindBoardUser.objects.create(organization=me.default,
        # board=board, user=me, peer=user)
        # event.dispatch(*board.admins.all())

        # me.ws_sound(board)
        # me.ws_subscribe(board, target=user)

        # Warrant the user will receive the sound event
        # because we cant control the order in which
        # data flows to the different queues.
        # me.ws_sound(target=user)

        return HttpResponse(status=200)

class UnbindBoardAdmin(GuardianView):
    def get(self, request, board_id, user_id):
        board = Board.objects.get(id=board_id)
        user = User.objects.get(id=user_id)

        # The owner admin status cant be removed.
        if board.owner == user:
            return HttpResponse("You can't \
                remove the owner!", status=403)

        me = User.objects.get(id=self.user_id)

        # Just the owner can add/remove admins.
        if board.owner != me:
            return HttpResponse("Just the owner can do that!", status=403)

        # This code shows up in board_app.views?
        # something is odd.
        board.admins.remove(user)
        board.save()

        # event = EUnbindBoardUser.objects.create(organization=me.default,
        # board=board, user=me, peer=user)
        # event.dispatch(*board.admins.all())

        # me.ws_sound(board)
        # me.ws_unsubscribe(board, target=user)
        # me.ws_sound(user)

        return HttpResponse(status=200)

class BoardLink(GuardianView):
    """
    """

    def get(self, request, board_id):
        board = Board.objects.get(id=board_id)
        # on_clipboard = not (board.ancestor and board.ancestor.ancestor)
# 
        # if on_clipboard:
            # return HttpResponse("This board is on clipboard! \
               # It can't be accessed.", status=403)

        user = core_app.models.User.objects.get(id=self.user_id)
        boardpins = user.boardpin_set.filter(organization=user.default)
        listpins = user.listpin_set.filter(organization=user.default)
        cardpins = user.cardpin_set.filter(organization=user.default)
        timelinepins = user.timelinepin_set.filter(organization=user.default)

        organizations = user.organizations.exclude(id=user.default.id)

        return render(request, 'board_app/board-link.html', 
        {'board': board, 'user': user, 'organization': user.default,
        'default': user.default, 'organizations': organizations,  'boardpins': boardpins,
        'listpins': listpins, 'cardpins': cardpins, 'timelinepins': timelinepins,
        'settings': settings})








