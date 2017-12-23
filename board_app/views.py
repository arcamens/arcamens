from core_app.views import AuthenticatedView, GuardianView
from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import render, redirect
from django.db.models import Q
import board_app.models
import card_app.models
from . import models
from . import forms
from . import models
from . import forms
import core_app.models
import board_app.models
from core_app import ws

# Create your views here.

class ListBoards(GuardianView):
    """
    """

    def get(self, request):
        user   = core_app.models.User.objects.get(id=self.user_id)

        total = user.boards.filter(
        organization__id=user.default.id)
        pins = user.pin_set.all()

        filter, _ = models.BoardFilter.objects.get_or_create(
        user=user, organization=user.default)

        boards = total.filter((Q(name__icontains=filter.pattern) | \
        Q(description__icontains=filter.pattern))) if filter.status else total

        return render(request, 'board_app/list-boards.html', 
        {'boards': boards, 'total': boards, 'user': user, 'pins': pins, 'filter': filter,
        'organization': user.default})

class Board(GuardianView):
    def get(self, request, board_id):
        board = models.Board.objects.get(id=board_id)
        return render(request, 'board_app/board.html', 
        {'board':board})

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
        user        = core_app.models.User.objects.get(id=self.user_id)
        board.owner = user

        board.members.add(user)
        board.organization = user.default
        board.save()

        # ws.client.publish('board%s' % board.id, 
            # 'board on: %s!' % board.name, 0, False)
        ws.client.publish('user%s' % user.id, 
            'subscribe board%s' % board.id, 0, False)

        return redirect('board_app:list-boards')


class PinBoard(GuardianView):
    def get(self, request, board_id):
        user  = core_app.models.User.objects.get(id=self.user_id)
        board = models.Board.objects.get(id=board_id)
        pin   = board_app.models.Pin.objects.create(user=user, board=board)
        return redirect('board_app:list-pins')

class ManageUserBoards(GuardianView):
    def get(self, request, user_id):
        me = core_app.models.User.objects.get(id=self.user_id)
        user = core_app.models.User.objects.get(id=user_id)

        boards = me.boards.filter(organization=me.default)
        excluded = boards.exclude(members=user)
        included = boards.filter(members=user)

        return render(request, 'board_app/manage-user-boards.html', 
        {'user': user, 'included': included, 'excluded': excluded,
        'me': me, 'organization': me.default,'form':forms.BoardSearchForm()})

    def post(self, request, user_id):
        user = core_app.models.User.objects.get(id=user_id)
        form = forms.BoardSearchForm(request.POST)

        me = core_app.models.User.objects.get(id=self.user_id)
        boards = me.boards.filter(organization=me.default)

        if not form.is_valid():
            return render(request, 'board_app/manage-user-boards.html', 
                {'user': user, 'included': included, 'excluded': excluded,
                    'me': me, 'organization': me.default, 
                        'form':forms.BoardSearchForm()}, status=400)

        boards = boards.filter(
        name__contains=form.cleaned_data['name'])

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
        me = core_app.models.User.objects.get(id=self.user_id)
        board = models.Board.objects.get(id=board_id)

        included = board.members.all()
        excluded = core_app.models.User.objects.exclude(boards=board)

        return render(request, 'board_app/manage-board-users.html', 
        {'included': included, 'excluded': excluded, 'board': board,
        'me': me, 'organization': me.default,'form':forms.UserSearchForm()})

    def post(self, request, board_id):
        form = forms.UserSearchForm(request.POST)

        me = core_app.models.User.objects.get(id=self.user_id)
        board = models.Board.objects.get(id=board_id)
        included = board.members.all()
        excluded = core_app.models.User.objects.exclude(boards=board)

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
        board = models.Board.objects.get(id=board_id)
        user = core_app.models.User.objects.get(id=self.user_id)

        for ind in user.list_clipboard.all():
            ind.ancestor = board; ind.save()
        user.list_clipboard.clear()

        return redirect('list_app:list-lists', 
        board_id=board.id)

class UpdateBoard(GuardianView):
    def get(self, request, board_id):
        board = models.Board.objects.get(id=board_id)
        return render(request, 'board_app/update-board.html',
        {'board': board, 'form': forms.BoardForm(instance=board)})

    def post(self, request, board_id):
        record  = models.Board.objects.get(id=board_id)
        form    = forms.BoardForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'board_app/update-board.html',
                        {'form': form, 'board':record, }, status=400)

        record.save()

        me = models.User.objects.get(id=self.user_id)
        event    = models.EUpdateBoard.objects.create(organization=me.default,
        board=record, user=me)
        event.users.add(*record.members.all())

        ws.client.publish('board%s' % record.id, 
            'subscribe board%s' % record.id, 0, False)

        return redirect('list_app:list-lists', 
        board_id=record.id)

class DeleteBoard(GuardianView):
    def get(self, request, board_id):
        board = models.Board.objects.get(id=board_id)
        board.delete()

        return redirect('board_app:list-boards')

class SetupBoardFilter(GuardianView):
    def get(self, request, organization_id):
        filter = models.BoardFilter.objects.get(
        user__id=self.user_id, organization__id=organization_id)
        organization = board_app.models.Organization.objects.get(id=organization_id)

        return render(request, 'board_app/setup-board-filter.html', 
        {'form': forms.BoardFilterForm(instance=filter), 
        'organization': organization})

    def post(self, request, organization_id):
        record = models.BoardFilter.objects.get(
        organization__id=organization_id, user__id=self.user_id)

        form   = forms.BoardFilterForm(request.POST, instance=record)
        organization = board_app.models.Organization.objects.get(id=organization_id)

        if not form.is_valid():
            return render(request, 'board_app/setup-board-filter.html',
                   {'board': record, 'form': form, 
                        'organization': organization}, status=400)
        form.save()
        return redirect('board_app:list-boards')


class DisabledAccount(GuardianView):
    def get(self, request):
        pass

class Login(View):
    """
    """

    def get(self, request):
        return render(request, 'board_app/login.html', 
        {'form':forms.LoginForm()})

    def post(self, request):
        form = forms.LoginForm(request.POST)

        if not form.is_valid():
            return render(request, 'board_app/login.html',
                        {'form': form})

        email        = form.cleaned_data['email']
        password     = form.cleaned_data['password']
        organization = form.cleaned_data['organization']
        user         = core_app.models.User.objects.get(email = email, 
        organization__name=organization, password=password)
        request.session['user_id'] = user.id
        return redirect('board_app:index')

class Logout(View):
    """
    """

    def get(self, request):
        del request.session['user_id']
        return redirect('board_app:login')

class ListEvents(GuardianView):
    """
    """

    def get(self, request):
        user   = core_app.models.User.objects.get(id=self.user_id)
        events = user.default.events.all().order_by('-created')
        pins   = user.pin_set.all()
        form   = forms.FindEventForm()
        return render(request, 'board_app/list-events.html', 
        {'events': events, 'pins': pins, 'user': user, 
        'form': form, 'organization': user.default})

class SwitchOrganization(GuardianView):
    def get(self, request, organization_id):
        user = core_app.models.User.objects.get(id=self.user_id)
        user.default = models.Organization.objects.get(
        id=organization_id)
        user.save()
        return redirect('board_app:index')

class ListPins(GuardianView):
    def get(self, request):
        user = core_app.models.User.objects.get(id=self.user_id)
        pins = user.pin_set.all()
        return render(request, 'board_app/list-pins.html', 
        {'user': user, 'pins': pins})

class Unpin(GuardianView):
    def get(self, request, pin_id):
        pin = models.Pin.objects.get(id=pin_id)
        pin.delete()
        return redirect('board_app:list-pins')

class CheckEvent(GuardianView):
    def get(self, request, user_id):
        user = core_app.models.User.objects.get(
        id=self.user_id)

        try:
            event = user.events.latest('id')
        except Exception:
            return HttpResponse(status=400)
        return HttpResponse(str(event.id), status=200)

class ListClipboard(GuardianView):
    def get(self, request):
        user   = core_app.models.User.objects.get(id=self.user_id)
        
        return render(request, 'board_app/list-clipboard.html', 
        {'user': user, 'cards': user.card_clipboard.all(), 'lists': user.list_clipboard.all()})

class ListArchive(GuardianView):
    def get(self, request):
        user   = core_app.models.User.objects.get(id=self.user_id)
        return render(request, 'board_app/list-archive.html', 
        {'user': user})

class Find(GuardianView):
    def get(self, request):
        user   = core_app.models.User.objects.get(id=self.user_id)
        return render(request, 'board_app/find.html', 
        {'user': user})

class BindBoardUser(GuardianView):
    def get(self, request, board_id, user_id):
        user = core_app.models.User.objects.get(id=user_id)
        board = board_app.models.Board.objects.get(id=board_id)

        board.members.add(user)
        board.save()

        me = models.User.objects.get(id=self.user_id)
        event    = models.EBindBoardUser.objects.create(organization=me.default,
        board=board, user=me, peer=user)
        event.users.add(*board.members.all())

        ws.client.publish('board%s' % board.id, 
            'timeline on: %s!' % board.name, 0, False)

        ws.client.publish('user%s' % user.id, 
            'subscribe board%s' % board.id, 0, False)

        return HttpResponse(status=200)

class UnbindBoardUser(GuardianView):
    def get(self, request, board_id, user_id):
        # This code shows up in board_app.views?
        # something is odd.
        user = core_app.models.User.objects.get(id=user_id)
        board = board_app.models.Board.objects.get(id=board_id)
        board.members.remove(user)
        board.save()

        me = models.User.objects.get(id=self.user_id)
        event    = models.EUnbindBoardUser.objects.create(organization=me.default,
        board=board, user=me, peer=user)
        event.users.add(*board.members.all())

        ws.client.publish('board%s' % board.id, 
            'timeline on: %s!' % board.name, 0, False)

        ws.client.publish('user%s' % user.id, 
            'unsubscribe board%s' % board.id, 0, False)

        return HttpResponse(status=200)

class EBindBoardUser(GuardianView):
    def get(self, request, event_id):
        event = models.EBindBoardUser.objects.get(id=event_id)
        return render(request, 'board_app/e-bind-board-user.html', 
        {'event':event})

class EUpdateBoard(GuardianView):
    def get(self, request, event_id):
        event = models.EUpdateBoard.objects.get(id=event_id)
        return render(request, 'board_app/e-update-board.html', 
        {'event':event})

class EUnbindBoardUser(GuardianView):
    def get(self, request, event_id):
        event = models.EUnbindBoardUser.objects.get(id=event_id)
        return render(request, 'board_app/e-unbind-board-user.html', 
        {'event':event})








