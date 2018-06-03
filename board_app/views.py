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
    Everyone in the organization is allowed to create boards,
    every user has its own workspace.
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
        board.owner = self.me

        board.members.add(self.me)
        board.admins.add(self.me)
        board.organization = self.me.default
        board.save()

        event = ECreateBoard.objects.create(organization=self.me.default,
        board=board, user=self.me)

        # Organization admins should be notified?
        event.dispatch(self.me)
        event.save()

        return redirect('core_app:list-nodes')


class PinBoard(GuardianView):
    def get(self, request, board_id):
        # Make sure the board belongs to my default organization.
        board = Board.objects.get(id=board_id, organization=self.me.default)

        pin   = BoardPin.objects.create(user=self.me, 
        organization=self.me.default, board=board)
        return redirect('board_app:list-pins')

class ManageUserBoards(GuardianView):
    """
    One is supposed to view a given user boards only if he belongs
    to the logged user default organization. It is gonna show a list of
    boards that i'm attached to.
    """

    def get(self, request, user_id):
        # Make sure the user belongs to my default organization. It is necessary
        # because it would allow one to view which boards the user is in. It is a security
        # flaw if we dont do this checking.
        user     = User.objects.get(id=user_id, organizations=self.me.default)
        boards   = self.me.boards.filter(organization=self.me.default)
        total    = boards.count()

        excluded = boards.exclude(members=user)
        included = boards.filter(members=user)

        env = {'user': user, 'included': included, 'excluded': excluded,
        'me': self.me, 'organization': self.me.default, 'total': total,
        'form':forms.BoardSearchForm(), 'count': total}

        return render(request, 'board_app/manage-user-boards.html', env)

    def post(self, request, user_id):
        # Does the necessary checking to make sure the user 
        # belongs to my default organization.
        user   = User.objects.get(id=user_id, organizations=self.me.default)
        sqlike = Board.from_sqlike()
        form   = forms.BoardSearchForm(request.POST, sqlike=sqlike)

        boards = self.me.boards.filter(organization=self.me.default)
        total = boards.count()

        if not form.is_valid():
            return render(request, 'board_app/manage-user-boards.html', 
                {'user': user, 'me': self.me, 'organization': self.me.default, 
                        'form':form}, status=400)

        excluded = boards.exclude(members=user)
        included = boards.filter(members=user)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)

        count = included.count() + excluded.count()
        env   = {'user': user, 'included': included, 'excluded': excluded, 
        'total': total, 'me': self.me, 'organization': self.me.default,
        'form':form, 'count': count}

        return render(request, 'board_app/manage-user-boards.html', env)

class ManageBoardMembers(GuardianView):
    """
    The logged user is supposed to view all existing members of the board
    altogether with the organization members.
    """

    def get(self, request, board_id):
        # Make sure the board belong to the user organization.
        # Otherwise it would be possible to view members of other
        # board organizations.
        board = Board.objects.get(id=board_id, organization=self.me.default)

        included = board.members.all()
        users = self.me.default.users.all()
        excluded = users.exclude(boards=board)

        total = included.count() + excluded.count()

        return render(request, 'board_app/manage-board-members.html', 
        {'included': included, 'excluded': excluded, 'board': board,
        'me': self.me, 'count': total, 'total': total, 
        'form':forms.UserSearchForm()})

    def post(self, request, board_id):
        sqlike = User.from_sqlike()
        form = forms.UserSearchForm(request.POST, sqlike=sqlike)

        board = Board.objects.get(id=board_id, organization=self.me.default)
        included = board.members.all()

        users = self.me.default.users.all()
        excluded = users.exclude(boards=board)
        total = included.count() + excluded.count()

        if not form.is_valid():
            return render(request, 'board_app/manage-board-members.html', 
                {'me': self.me, 'board': board, 'total': total, 'count': 0,
                        'form':form}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)
        count = included.count() + excluded.count()

        return render(request, 'board_app/manage-board-members.html', 
        {'included': included, 'excluded': excluded, 'board': board,
        'me': self.me, 'total': total, 'count': count, 'form':form})

class ManageBoardAdmins(GuardianView):
    def get(self, request, board_id):
        board = Board.objects.get(id=board_id, organization=self.me.default)

        included = board.admins.all()
        excluded = board.members.exclude(id__in=included)

        total = included.count() + excluded.count()

        return render(request, 'board_app/manage-board-admins.html', 
        {'included': included, 'excluded': excluded, 'board': board,
        'me': self.me, 'count': total, 'total': total, 
        'form':forms.UserSearchForm()})

    def post(self, request, board_id):
        sqlike = User.from_sqlike()
        form = forms.UserSearchForm(request.POST, sqlike=sqlike)

        board = Board.objects.get(id=board_id, organization=self.me.default)

        included = board.admins.all()
        excluded = board.members.exclude(id__in=included)

        total = included.count() + excluded.count()

        if not form.is_valid():
            return render(request, 'board_app/manage-board-admins.html', 
                {'me': self.me, 'board': board, 'total': total, 'count': 0,
                        'form':form}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)
        count = included.count() + excluded.count()

        return render(request, 'board_app/manage-board-admins.html', 
        {'included': included, 'excluded': excluded, 'board': board,
        'me': self.me, 'total': total, 'count': count, 'form':form})

class PasteLists(GuardianView):
    def get(self, request, board_id):
        # We need to make sure the board belongs to the organization.
        # It as well makes sure i belong to the board.
        board = self.me.boards.get(id=board_id, organization=self.me.default)

        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)

        lists = clipboard.lists.all()

        if not lists.exists():
            return HttpResponse("There is no list on \
                the clipboard.", status=403)

        lists.update(ancestor=board)

        event = EPasteList.objects.create(
        organization=self.me.default, board=board, user=self.me)
        event.lists.add(*lists)
        event.dispatch(*board.members.all())
        event.save()

        clipboard.lists.clear()

        return redirect('list_app:list-lists', 
        board_id=board.id)

class UpdateBoard(GuardianView):
    """
    This view is supopsed to allow the user to view the dialog for
    updating the board but just the admins can perform the action.
    """

    def get(self, request, board_id):
        # Just make sure the board belong to the my default organization
        # but allows the user to view the update dialog template.
        board = self.me.boards.get(id=board_id, organization=self.me.default)
        return render(request, 'board_app/update-board.html',
        {'board': board, 'form': forms.BoardForm(instance=board)})

    def post(self, request, board_id):
        record = Board.objects.get(id=board_id)
        # Make sure i'm admin of the board and it belongs to 
        # my default organization.
        record = self.me.managed_boards.get(
            id=board_id, organization=self.me.default)

        form = forms.BoardForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'board_app/update-board.html',
                        {'form': form, 'board':record, }, status=400)

        record.save()

        event = EUpdateBoard.objects.create(organization=self.me.default,
        board=record, user=self.me)
        event.dispatch(*record.members.all())

        return redirect('list_app:list-lists', 
        board_id=record.id)

class DeleteBoard(GuardianView):
    """
    Allow the users/admins to view the dialog for confirming board deletion
    but just the owner can finalize with the action.
    """

    def get(self, request, board_id):
        board = self.me.boards.get(id=board_id, organization=self.me.default)
        form = forms.ConfirmBoardDeletionForm()

        return render(request, 'board_app/delete-board.html', 
        {'board': board, 'form': form})

    def post(self, request, board_id):
        board = self.me.owned_boards.get(
            id=board_id, organization=self.me.default)

        form = forms.ConfirmBoardDeletionForm(request.POST, 
        confirm_token=board.name)

        if not form.is_valid():
            return render(request, 
                'board_app/delete-board.html', 
                    {'board': board, 'form': form}, status=400)


        event = EDeleteBoard.objects.create(organization=self.me.default,
        board_name=board.name, user=self.me)
        event.dispatch(*board.members.all())

        board.delete()

        return redirect('core_app:list-nodes')

class ListPins(GuardianView):
    """
    This view is already secured for default.
    """
    def get(self, request):
        boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        listpins = self.me.listpin_set.filter(organization=self.me.default)
        cardpins = self.me.cardpin_set.filter(organization=self.me.default)
        timelinepins = self.me.timelinepin_set.filter(organization=self.me.default)

        return render(request, 'board_app/list-pins.html', 
        {'user': self.me, 'boardpins': boardpins, 'listpins': listpins, 
        'cardpins': cardpins, 'timelinepins': timelinepins})

class Unpin(GuardianView):
    """
    Make sure the pin is mine and it belongs to the my
    default organization.
    """

    def get(self, request, pin_id):
        pin = self.me.boardpin_set.get(
        id=pin_id, organization=self.me.default)

        pin.delete()
        return redirect('board_app:list-pins')

class BindBoardUser(GuardianView):
    def get(self, request, board_id, user_id):
        user     = User.objects.get(id=user_id)
        board    = Board.objects.get(id=board_id)
        me_admin = board.admins.filter(id=self.me.id).exists()

        if not me_admin:
            return HttpResponse("Just admins can add users!", status=403)

        board.members.add(user)
        board.save()

        event = EBindBoardUser.objects.create(organization=self.me.default,
        board=board, user=self.me, peer=user)
        event.dispatch(*board.members.all())

        return HttpResponse(status=200)

class UnbindBoardUser(GuardianView):
    def get(self, request, board_id, user_id):
        user = User.objects.get(id=user_id)
        board = Board.objects.get(id=board_id)

        if board.owner == user:
            return HttpResponse("You can't remove \
                the board owner!", status=403)

        is_admin = board.admins.filter(id=user.id).exists()
        me_admin = board.admins.filter(id=self.user_id).exists()

        me_owner = board.owner == self.me

        # In order to remove an user it is necessary to be an admin.
        if not me_admin:
            return HttpResponse("Just admins can do that!", status=403)

        if is_admin and not me_owner:
            return HttpResponse("Just the owner can do that!", status=403)

        # We make sure the user is no longer an admin at all.
        board.members.remove(user)
        board.admins.remove(user)
        board.save()

        event = EUnbindBoardUser.objects.create(organization=self.me.default,
        board=board, user=self.me, peer=user)
        event.dispatch(*board.members.all())

        return HttpResponse(status=200)

class BindBoardAdmin(GuardianView):
    def get(self, request, board_id, user_id):
        board = Board.objects.get(id=board_id)

        # Just the owner can add/remove admins.
        if board.owner != self.me:
            return HttpResponse("Just the owner can do that!", status=403)

        user = User.objects.get(id=user_id)
        board.admins.add(user)
        board.save()

        return HttpResponse(status=200)

class UnbindBoardAdmin(GuardianView):
    def get(self, request, board_id, user_id):
        board = Board.objects.get(id=board_id)
        user = User.objects.get(id=user_id)

        # The owner admin status cant be removed.
        if board.owner == user:
            return HttpResponse("You can't \
                remove the owner!", status=403)

        # Just the owner can add/remove admins.
        if board.owner != self.me:
            return HttpResponse("Just the owner can do that!", status=403)

        # This code shows up in board_app.views?
        # something is odd.
        board.admins.remove(user)
        board.save()

        return HttpResponse(status=200)

class BoardLink(GuardianView):
    """
    """

    def get(self, request, board_id):
        board = Board.objects.get(id=board_id, 
        organization=self.me.default)
        # on_clipboard = not (board.ancestor and board.ancestor.ancestor)
# 
        # if on_clipboard:
            # return HttpResponse("This board is on clipboard! \
               # It can't be accessed.", status=403)

        boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        listpins = self.me.listpin_set.filter(organization=self.me.default)
        cardpins = self.me.cardpin_set.filter(organization=self.me.default)
        timelinepins = self.me.timelinepin_set.filter(organization=self.me.default)

        organizations = self.me.organizations.exclude(id=self.me.default.id)

        return render(request, 'board_app/board-link.html', 
        {'board': board, 'user': self.me, 'organization': self.me.default,
        'default': self.me.default, 'organizations': organizations,  'boardpins': boardpins,
        'listpins': listpins, 'cardpins': cardpins, 'timelinepins': timelinepins,
        'settings': settings})













