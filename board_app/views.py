from core_app.views import GuardianView
from board_app.models import ECreateBoard, Board, BoardPin, Boardship,\
EPasteList, EUpdateBoard, EDeleteBoard, EBindBoardUser, EUnbindBoardUser, Board
from django.shortcuts import render, redirect
from core_app.sqlikes import SqUser
from core_app.models import Clipboard, User, Organization, Membership
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
        membership = Membership.objects.get(
            user=self.me, organization=self.me.default)

        if membership.status == '2':
            return HttpResponse("Contributors can't create boards!", status=403)
        form = forms.BoardForm(request.POST, me=self.me)

        if not form.is_valid():
            return render(request, 'board_app/create-board.html',
                        {'form': form, }, status=400)

        board       = form.save()
        board.owner = self.me
        board.organization = self.me.default
        board.save()

        # The board members if it is open.
        members    = self.me.default.users.all() if board.public else (self.me,)
        boardships = (Boardship(member=ind, board=board, 
        binder=self.me) for ind in members)
        Boardship.objects.bulk_create(boardships)

        # Make myself admin of the board after adding me
        # as a regular user.
        boardship = self.me.member_boardship.get(board=board)
        boardship.status = '0'
        boardship.save()

        # Boardship.objects.create(member=self.me, board=board, 
        # binder=self.me, status='0')

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
        {'board': board, 'form': forms.BoardForm(instance=board)})

    def post(self, request, board_id):
        # Make sure i'm owner of the board and it belongs to 
        # my default organization.
        record = self.me.boards.get(id=board_id, organization=self.me.default)
        if not record.owner == self.me: 
            return HttpResponse("Just the owner can do that!", status=403)

        form = forms.BoardForm(request.POST, instance=record, me=self.me)

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
        if not board.owner == self.me: 
            return HttpResponse("Just the owner can do that!", status=403)

        form  = forms.ConfirmBoardDeletionForm(
        request.POST,  confirm_token=board.name)

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


class UnbindBoardMembers(GuardianView):
    """
    The listed members are supposed to belong to the logged member default
    organization. It also checks if the member belongs to the board
    in order to list its members.
    """

    def get(self, request, board_id):
        board = self.me.boards.get(id=board_id, 
        organization=self.me.default)

        included = board.members.all()
        members    = self.me.default.users.all()
        total    = included.count() 

        return render(request, 'board_app/unbind-board-members.html', {
        'included': included, 'board': board, 'organization': self.me.default,
        'form':forms.UserSearchForm(), 'me': self.me, 
        'count': total, 'total': total,})

    def post(self, request, board_id):
        sqlike = SqUser()
        form   = forms.UserSearchForm(request.POST, sqlike=sqlike)
        board  = self.me.boards.get(id=board_id, organization=self.me.default)

        included = board.members.all()
        members  = self.me.default.users.all()
        total    = included.count() 
        
        if not form.is_valid():
            return render(request, 'board_app/manage-board-members.html', 
                {'me': self.me, 'board': board, 'count': 0, 'total': total,
                        'form':form}, status=400)

        included = sqlike.run(included)
        count = included.count() 

        return render(request, 'board_app/unbind-board-members.html', 
        {'included': included, 'board': board, 'me': self.me, 
        'organization': self.me.default,'form':form, 
        'count': count, 'total': total,})

class BindBoardMembers(GuardianView):
    """
    The listed members are supposed to belong to the logged member default
    organization. It also checks if the member belongs to the board
    in order to list its members.
    """

    def get(self, request, board_id):
        board = self.me.boards.get(id=board_id, 
        organization=self.me.default)

        members    = self.me.default.users.all()
        excluded = members.exclude(boards=board)
        total    = excluded.count()

        return render(request, 'board_app/bind-board-members.html', 
        {'excluded': excluded, 'board': board, 'me': self.me, 
        'organization': self.me.default,'form':forms.UserSearchForm(), 
        'count': total, 'total': total,})

    def post(self, request, board_id):
        sqlike = SqUser()
        form   = forms.UserSearchForm(request.POST, sqlike=sqlike)
        board  = self.me.boards.get(id=board_id, organization=self.me.default)

        members  = self.me.default.users.all()
        excluded = members.exclude(boards=board)
        total    = excluded.count()
        
        if not form.is_valid():
            return render(request, 'board_app/bind-board-members.html', 
                {'me': self.me, 'board': board, 'count': 0, 'total': total,
                        'form':form}, status=400)

        excluded = sqlike.run(excluded)
        count = excluded.count()

        return render(request, 'board_app/bind-board-members.html', 
        {'excluded': excluded, 'board': board, 'me': self.me, 
        'organization': self.me.default,'form':form, 
        'count': count, 'total': total,})

class UnbindMemberBoards(GuardianView):
    """
    Make sure the logged member can view the boards that he belongs to.
    It also makes sure the listed boards belong to his default organization.
    """

    def get(self, request, member_id):
        # Make sure the member belongs to my default organization.
        member      = User.objects.get(id=member_id, organizations=self.me.default)
        boards = self.me.boards.filter(organization=self.me.default)
        total     = boards.count()

        included  = boards.filter(members=member)
        count = included.count()

        env = {'member': member, 'included': included, 
        'count': count, 'total': total, 'me': self.me, 
        'organization': self.me.default, 'form':forms.BoardSearchForm()}

        return render(request, 'board_app/unbind-member-boards.html', env)

    def post(self, request, member_id):
        # Make sure the member belongs to my default organization.
        member      = User.objects.get(id=member_id, organizations=self.me.default)
        sqlike    = Board.from_sqlike()
        form      = forms.BoardSearchForm(request.POST, sqlike=sqlike)
        boards = self.me.boards.filter(organization=self.me.default)
        total     = boards.count()

        if not form.is_valid():
            return render(request, 'board_app/unbind-member-boards.html', 
                {'member': member, 'me': self.me, 'organization': self.me.default, 
                    'count': 0,'form':form, 'total': total,}, status=400)

        included  = boards.filter(members=member)
        included = sqlike.run(included)
        count    = included.count() 
        env      = {'member': member, 'included': included, 
        'total': total, 'me': self.me, 'organization': self.me.default, 
        'form':form, 'count': count}

        return render(request, 'board_app/unbind-member-boards.html', env)

class BindMemberBoards(GuardianView):
    """
    Make sure the logged member can view the boards that he belongs to.
    It also makes sure the listed boards belong to his default organization.
    """

    def get(self, request, member_id):
        # Make sure the member belongs to my default organization.
        member      = User.objects.get(id=member_id, organizations=self.me.default)
        boards = self.me.boards.filter(organization=self.me.default)
        total     = boards.count()

        excluded = boards.exclude(members=member)
        count    = excluded.count()

        env      = {'member': member, 'excluded': excluded,  'count': count, 
        'total': total, 'me': self.me,  'organization': self.me.default, 
        'form':forms.BoardSearchForm()}

        return render(request, 'board_app/bind-member-boards.html', env)

    def post(self, request, member_id):
        # Make sure the member belongs to my default organization.
        member      = User.objects.get(id=member_id, organizations=self.me.default)
        sqlike    = Board.from_sqlike()
        form      = forms.BoardSearchForm(request.POST, sqlike=sqlike)
        boards = self.me.boards.filter(organization=self.me.default)
        total     = boards.count()

        if not form.is_valid():
            return render(request, 'board_app/bind-member-boards.html', 
                {'member': member, 'me': self.me, 'organization': self.me.default, 
                    'count': 0,'form':form, 'total': total,}, status=400)

        excluded  = boards.exclude(members=member)
        count    = excluded.count()
        env      = {'member': member, 'excluded': excluded, 
        'total': total, 'me': self.me, 'organization': self.me.default, 
        'form':form, 'count': count}

        return render(request, 'board_app/bind-member-boards.html', env)

class CreateBoardshipMember(GuardianView):
    """
    """

    def get(self, request, board_id, member_id):
        member  = User.objects.get(id=member_id, organizations=self.me.default)
        board = self.me.boards.get(id=board_id, organization=self.me.default)
        form  = forms.BoardshipForm()

        return render(request, 'board_app/create-boardship-member.html', {
        'member': member, 'board': board, 'form': form})

    def post(self, request, board_id, member_id):
        member  = User.objects.get(id=member_id, organizations=self.me.default)
        board = self.me.boards.get(id=board_id, organization=self.me.default)

        form = forms.BoardshipForm(request.POST)
        if not form.is_valid():
            return render(request, self.template, {
                'member': member, 'board': board, 'form': form})

        boardship = Boardship.objects.get(member=self.me, board=board)
        if boardship.status != '0':
            return HttpResponse("No permissions for that!", status=403)

        membership = Membership.objects.get(
        user=member_id, organization=self.me.default)

        if membership.status == '2' and form.cleaned_data['status'] != '2':
            return HttpResponse("User is a contributor! Contributors\
                can only be board guests.", status=403)

        record = form.save(commit=False)
        record.member = member
        record.binder = self.me
        record.board  = board
        record.save()

        event = EBindBoardUser.objects.create(organization=self.me.default,
        board=board, user=self.me, peer=member, status=record.status)
        event.dispatch(*board.members.all())

        return redirect('board_app:bind-board-members', board_id=board.id)

class SetBoardshipMember(GuardianView):
    """
    """

    def get(self, request, board_id, member_id):
        member = User.objects.get(id=member_id, organizations=self.me.default)
        board  = self.me.boards.get(id=board_id, organization=self.me.default)

        boardship = Boardship.objects.get(member=member, board=board)
        form      = forms.BoardshipForm(instance=boardship)

        return render(request, 'board_app/set-boardship-member.html', {
        'member': member, 'board': board, 'me': self.me, 'form': form})

    def post(self, request, board_id, member_id):
        member     = User.objects.get(id=member_id, organizations=self.me.default)
        board = self.me.boards.get(id=board_id, organization=self.me.default)

        boardship0 = Boardship.objects.get(member=member, board=board)
        form      = forms.BoardshipForm(request.POST, instance=boardship0)

        if not form.is_valid():
            return render(request, 'board_app/set-boardship-member.html', {
                'member': member, 'board': board, 'form': form})

        if member == board.owner:
            return HttpResponse("Can't change owner status!", status=403)

        boardship1 = Boardship.objects.get(member=self.me, board=board)
        if boardship1.status != '0':
            return HttpResponse("No permissions for that!", status=403)

        membership = Membership.objects.get(
        user=member_id, organization=self.me.default)

        if membership.status == '2' and form.cleaned_data['status'] != '2':
            return HttpResponse("User is a contributor! Contributors\
                can only be board guests.", status=403)

        record = form.save()

        event = EBindBoardUser.objects.create(organization=self.me.default,
        board=board, user=self.me, peer=member, status=record.status)
        event.dispatch(*board.members.all())
        return redirect('board_app:unbind-board-members', board_id=board.id)

class CreateMemberBoardship(GuardianView):
    """
    """

    def get(self, request, board_id, member_id):
        member  = User.objects.get(id=member_id, organizations=self.me.default)
        board = self.me.boards.get(id=board_id, organization=self.me.default)
        form  = forms.BoardshipForm()

        return render(request, 'board_app/create-member-boardship.html', {
        'member': member, 'board': board, 'form': form})

    def post(self, request, board_id, member_id):
        member  = User.objects.get(id=member_id, organizations=self.me.default)
        board = self.me.boards.get(id=board_id, organization=self.me.default)

        form = forms.BoardshipForm(request.POST)
        if not form.is_valid():
            return render(request, self.template, {
                'member': member, 'board': board, 'form': form})

        boardship = Boardship.objects.get(member=self.me, board=board)
        if boardship.status != '0':
            return HttpResponse("No permissions for that!", status=403)

        membership = Membership.objects.get(
        user=member_id, organization=self.me.default)

        if membership.status == '2' and form.cleaned_data['status'] != '2':
            return HttpResponse("User is a contributor! Contributors\
                can only be board guests.", status=403)

        record = form.save(commit=False)
        record.member   = member
        record.binder = self.me
        record.board  = board
        record.save()


        event = EBindBoardUser.objects.create(organization=self.me.default,
        board=board, user=self.me, peer=member, status=record.status)
        event.dispatch(*board.members.all())

        return redirect('board_app:bind-member-boards', member_id=member.id)


class SetMemberBoardship(GuardianView):
    """
    """
    def get(self, request, board_id, member_id):
        member     = User.objects.get(id=member_id, organizations=self.me.default)
        board = self.me.boards.get(id=board_id, organization=self.me.default)
        boardship = Boardship.objects.get(member=member, board=board)
        form  = forms.BoardshipForm(instance=boardship)

        return render(request, 'board_app/set-member-boardship.html', {
        'member': member, 'board': board, 'me': self.me, 'form': form})

    def post(self, request, board_id, member_id):
        member  = User.objects.get(id=member_id, organizations=self.me.default)
        board = self.me.boards.get(id=board_id, organization=self.me.default)

        boardship = Boardship.objects.get(member=member, board=board)
        form      = forms.BoardshipForm(request.POST, instance=boardship)
        if not form.is_valid():
            return render(request, 'board_app/set-member-boardship.html', {
                'member': member, 'board': board, 'form': form})

        if member == board.owner:
            return HttpResponse("Can't change owner status!", status=403)

        boardship = Boardship.objects.get(member=self.me, board=board)
        if boardship.status != '0':
            return HttpResponse("No permissions for that!", status=403)

        membership = Membership.objects.get(
        user=member_id, organization=self.me.default)

        if membership.status == '2' and form.cleaned_data['status'] != '2':
            return HttpResponse("User is a contributor! Contributors\
                can only be board guests.", status=403)

        record = form.save()
        event = EBindBoardUser.objects.create(organization=self.me.default,
        board=board, user=self.me, peer=member, status=record.status)
        event.dispatch(*board.members.all())
        return redirect('board_app:unbind-member-boards', member_id=member.id)

class DeleteBoardshipMember(GuardianView):
    """
    """

    def get(self, request, board_id, member_id):
        member = User.objects.get(id=member_id, organizations=self.me.default)
        board  = self.me.boards.get(id=board_id, organization=self.me.default)

        boardship = Boardship.objects.get(member=member, board=board)

        return render(request, 'board_app/delete-boardship-member.html', {
        'member': member, 'board': board})

    def post(self, request, board_id, member_id):
        member     = User.objects.get(id=member_id, organizations=self.me.default)
        board = self.me.boards.get(id=board_id, organization=self.me.default)

        if member == board.owner:
            return HttpResponse("Can't change owner status!", status=403)

        boardship0 = Boardship.objects.get(member=member, board=board)
        boardship1 = Boardship.objects.get(member=self.me, board=board)
        if boardship1.status != '0':
            return HttpResponse("No permissions for that!", status=403)

        event = EUnbindBoardUser.objects.create(organization=self.me.default,
        board=board, user=self.me, peer=member)
        event.dispatch(*board.members.all())

        boardship0.delete()
        return redirect('board_app:unbind-board-members', board_id=board.id)

class DeleteMemberBoardship(GuardianView):
    """
    """

    def get(self, request, board_id, member_id):
        member = User.objects.get(id=member_id, organizations=self.me.default)
        board  = self.me.boards.get(id=board_id, organization=self.me.default)

        boardship = Boardship.objects.get(member=member, board=board)

        return render(request, 'board_app/delete-member-boardship.html', {
        'member': member, 'board': board})

    def post(self, request, board_id, member_id):
        member     = User.objects.get(id=member_id, organizations=self.me.default)
        board = self.me.boards.get(id=board_id, organization=self.me.default)

        if member == board.owner:
            return HttpResponse("Can't change owner status!", status=403)

        boardship0 = Boardship.objects.get(member=member, board=board)
        boardship1 = Boardship.objects.get(member=self.me, board=board)
        if boardship1.status != '0':
            return HttpResponse("No permissions for that!", status=403)

        event = EUnbindBoardUser.objects.create(organization=self.me.default,
        board=board, user=self.me, peer=member)
        event.dispatch(*board.members.all())

        boardship0.delete()
        return redirect('board_app:unbind-member-boards', member_id=member.id)

class JoinPublicBoard(GuardianView):
    """
    """

    def post(self, request, board_id):
        board = models.Board.objects.get(id=board_id, organization=self.me.default)
        organization = Organization.objects.get(id=organization_id)

        Boardship.objects.create(user=self.me, status='2',
        organization=organization, board=board, binder=self.me)

        event = EBindBoardUser.objects.create(organization=self.me.default,
        board=board, user=self.me, peer=self.me, status='2')
        event.dispatch(*board.users.all())

        return redirect('core_app:index')

class LeaveBoard(GuardianView):
    """
    """
    def get(self, request, board_id):
        board = self.me.boards.get(id=board_id, organization=self.me.default)

        return render(request, 'board_app/leave-board.html', {'board': board})

    def post(self, request, board_id):
        board = self.me.boards.get(id=board_id, organization=self.me.default)

        if board.owner == self.me: 
            return HttpResponse("Owner can't leave the board!", status=403)

        boardship = Boardship.objects.get(member=self.me, board=board)
        boardship.delete()

        event = EUnbindBoardUser.objects.create(organization=self.me.default,
        board=board, user=self.me, peer=self.me)
        event.dispatch(*board.members.all())

        return redirect('core_app:list-nodes')







