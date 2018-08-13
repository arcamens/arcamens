from core_app.views import GuardianView
from board_app.models import ECreateBoard, Board, BoardPin, Boardship,\
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
        board.organization = self.me.default
        board.save()

        # The board members if it is open.
        members    = self.me.default.users.all() if board.open else (self.me,)
        boardships = (Boardship(member=ind, board=board, 
        binder=self.me) for ind in members)
        Boardship.objects.bulk_create(boardships)

        # Make myself admin of the board after adding me
        # as a regular user.
        boardship = self.me.member_boardship.get(board=board)
        boardship.admin = True
        boardship.save()

        event = ECreateBoard.objects.create(organization=self.me.default,
        board=board, user=self.me)

        # Organization admins should be notified?
        event.dispatch(*members)
        event.save()

        return redirect('core_app:list-nodes')


class PinBoard(GuardianView):
    """
    This view is allowed to be performed just by the user who belongs to the    
    board. The board has to be in the user default organization too.
    """
    def get(self, request, board_id):
        # Make sure the board belongs to my default organization.
        board = self.me.boards.get(id=board_id, organization=self.me.default)
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

    This dialog should be shown just if the user in fact belongs to the board
    and his default organization contains the board.
    """

    def get(self, request, board_id):
        # Make sure the board belong to the user organization.
        # Otherwise it would be possible to view members of other
        # board organizations.
        board = self.me.boards.get(id=board_id, organization=self.me.default)

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
        board = self.me.boards.get(id=board_id, organization=self.me.default)
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
    """
    One is supposed view the dialog only if he belongs to the board
    and his default organization contains the board.
    """

    def get(self, request, board_id):
        board = self.me.boards.get(id=board_id, organization=self.me.default)

        included = board.members.filter(member_boardship__admin=True, 
        member_boardship__board=board)

        excluded = board.members.filter(member_boardship__admin=False,
        member_boardship__board=board)

        total = included.count() + excluded.count()

        return render(request, 'board_app/manage-board-admins.html', 
        {'included': included, 'excluded': excluded, 'board': board,
        'me': self.me, 'count': total, 'total': total, 
        'form':forms.UserSearchForm()})

    def post(self, request, board_id):
        sqlike = User.from_sqlike()
        form   = forms.UserSearchForm(request.POST, sqlike=sqlike)
        board  = self.me.boards.get(id=board_id, organization=self.me.default)

        included = board.members.filter(member_boardship__admin=True, 
        member_boardship__board=board)

        excluded = board.members.filter(member_boardship__admin=False,
        member_boardship__board=board)

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

class SelectDestinBoard(GuardianView):
    def get(self, request, board_id):
        board = models.Board.objects.get(id=board_id, 
        organization=self.me.default, members=self.me)

        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)

        lists = clipboard.lists.all()
        total = lists.count() 

        return render(request, 'board_app/select-destin-board.html', 
        {'user': self.me, 'board': board, 'lists': lists,  'total': total})

class PasteList(GuardianView):
    def get(self, request, board_id, list_id):
        board = models.Board.objects.get(id=board_id, 
        organization=self.me.default, members=self.me)

        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)

        list = clipboard.lists.get(id=list_id)
        list.ancestor = board
        list.save()

        event = EPasteList(organization=self.me.default, 
        board=board, user=self.me)

        event.save(hcache=False)
        event.lists.add(list)
    
        # Workers of the list dont need to be notified of this event
        # because them may not belong to the board at all.
        event.dispatch(*board.members.all())
        event.save()

        clipboard.lists.remove(list)

        return redirect('board_app:select-destin-board', board_id=board.id)

class PasteAllLists(GuardianView):
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
        {'board': board, 'form': forms.UpdateBoardForm(instance=board)})

    def post(self, request, board_id):
        # record = Board.objects.get(id=board_id)
        # Make sure i'm owner of the board and it belongs to 
        # my default organization.
        record = self.me.boards.get(id=board_id, organization=self.me.default)
        if not record.owner == self.me: return HttpResponse(
            "Just the owner can do that!", status=403)

        form = forms.UpdateBoardForm(request.POST, instance=record)
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
        board = self.me.boards.get(id=board_id, organization=self.me.default)
        if not board.owner == self.me: return HttpResponse(
            "Just the owner can do that!", status=403)

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
        grouppins = self.me.grouppin_set.filter(organization=self.me.default)
        postpins = self.me.postpin_set.filter(organization=self.me.default)

        return render(request, 'board_app/list-pins.html', 
        {'user': self.me, 'boardpins': boardpins, 'listpins': listpins, 
        'cardpins': cardpins, 'postpins': postpins, 'grouppins': grouppins})

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
    """
    Secured.
    """

    def redirect(self, request, board_id, user_id):
        return ManageBoardMembers.as_view()(request, board_id)

    def post(self, request, board_id, user_id):
        # Make sure the user belongs to my default organization.
        user  = User.objects.get(id=user_id, organizations=self.me.default)
        board = Board.objects.get(id=board_id, organization=self.me.default)

        me_admin = self.me.member_boardship.filter(
        board=board, admin=True).exists()

        if not me_admin:
            return HttpResponse("Just admins can add users!", status=403)

        Boardship.objects.create(member=user, binder=self.me, board=board)

        event = EBindBoardUser.objects.create(organization=self.me.default,
        board=board, user=self.me, peer=user)
        event.dispatch(*board.members.all())

        return self.redirect(request, board_id, user_id)

class BindUserBoard(BindBoardUser):
    def redirect(self, request, board_id, user_id):
        return ManageUserBoards.as_view()(request, user_id)

class UnbindBoardUser(GuardianView):
    """
    Secured.
    """
    def redirect(self, request, board_id, user_id):
        return ManageBoardMembers.as_view()(request, board_id)

    def post(self, request, board_id, user_id):
        user  = User.objects.get(id=user_id, organizations=self.me.default)
        board = Board.objects.get(id=board_id, organization=self.me.default)

        if board.owner == user:
            return HttpResponse("You can't remove \
                the board owner!", status=403)

        is_admin = user.member_boardship.filter(
        board=board, admin=True).exists()

        me_admin = self.me.member_boardship.filter(
        board=board, admin=True).exists()

        me_owner = board.owner == self.me

        # In order to remove an user it is necessary to be an admin.
        if not me_admin:
            return HttpResponse("Just admins can do that!", status=403)

        if is_admin and not me_owner:
            return HttpResponse("Just the owner can do that!", status=403)

        # We make sure the user is no longer an admin at all.
        event = EUnbindBoardUser.objects.create(organization=self.me.default,
        board=board, user=self.me, peer=user)
        event.dispatch(*board.members.all())

        user.member_boardship.get(board=board).delete()
        return self.redirect(request, board_id, user_id)

class UnbindUserBoard(UnbindBoardUser):
    def redirect(self, request, board_id, user_id):
        return ManageUserBoards.as_view()(request, user_id)

class BindBoardAdmin(GuardianView):
    def post(self, request, board_id, user_id):
        user  = User.objects.get(id=user_id, organizations=self.me.default)
        board = Board.objects.get(id=board_id, organization=self.me.default)

        # Just the owner can add/remove admins.
        if board.owner != self.me:
            return HttpResponse("Just the owner can do that!", status=403)

        boardship = user.member_boardship.get(board=board)
        boardship.admin = True
        boardship.save()
        return ManageBoardAdmins.as_view()(request, board_id)

class UnbindBoardAdmin(GuardianView):
    def post(self, request, board_id, user_id):
        user  = User.objects.get(id=user_id, organizations=self.me.default)
        board = Board.objects.get(id=board_id, organization=self.me.default)

        # The owner admin status cant be removed.
        if board.owner == user:
            return HttpResponse("You can't \
                remove the owner!", status=403)

        # Just the owner can add/remove admins.
        if board.owner != self.me:
            return HttpResponse("Just the owner can do that!", status=403)

        boardship = user.member_boardship.get(board=board)
        boardship.admin = False
        boardship.save()
        return ManageBoardAdmins.as_view()(request, board_id)

class BoardLink(GuardianView):
    """
    Make sure the user belongs to the board and his default
    organization contains the board.
    """

    def get(self, request, board_id):
        board = self.me.boards.get(id=board_id, 
        organization=self.me.default)

        boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        listpins = self.me.listpin_set.filter(organization=self.me.default)
        cardpins = self.me.cardpin_set.filter(organization=self.me.default)
        grouppins = self.me.grouppin_set.filter(organization=self.me.default)

        organizations = self.me.organizations.exclude(id=self.me.default.id)

        return render(request, 'board_app/board-link.html', 
        {'board': board, 'user': self.me, 'organization': self.me.default,
        'default': self.me.default, 'organizations': organizations,  'boardpins': boardpins,
        'listpins': listpins, 'cardpins': cardpins, 'grouppins': grouppins,
        'settings': settings})












