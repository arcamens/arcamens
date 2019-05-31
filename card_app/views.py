from django.shortcuts import render, redirect
from django.db.models.functions import Concat
from django.db.models import Q, F, Exists, OuterRef, Count, Value, CharField
from django.urls import reverse
from django.http import HttpResponse
from card_app.models import CardSearch, CardPin, EBindTagCard, \
EUnbindTagCard, CardTagship, EUpdateCard, Card
from core_app.sqlikes import SqUser, SqTag
from card_app.sqlikes import SqCard
from core_app.models import Clipboard, Event, Tag
from django.core.mail import send_mail
from core_app.views import GuardianView, FileDownload
from post_app.models import Post, ECreatePostFork
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from post_app.forms import PostForm
from group_app.models import Group
from core_app.models import User
from list_app.models import List, EPasteCard
from django.db import transaction
from jscroll.wrappers import JScroll
from functools import reduce
import board_app.models
import list_app.models
from . import models
from . import forms
import operator
import core_app.models
from django.conf import settings
from re import split
from re import findall

# Create your views here.
class RefreshCardLabel(GuardianView):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)
        return render(request, 'card_app/card.html',  {'card': card},) 

class CardLink(GuardianView):
    """
    """

    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)

        boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        listpins = self.me.listpin_set.filter(organization=self.me.default)
        cardpins = self.me.cardpin_set.filter(organization=self.me.default)
        grouppins = self.me.grouppin_set.filter(organization=self.me.default)

        forks = card.forks.all()
        workers = card.workers.all()
        attachments = card.cardfilewrapper_set.all()
        tags = card.tags.all()
        # comments = card.comments.all()
        relations = card.relations.all()
        path = card.path.all()

        relations = relations.filter(Q(
        ancestor__ancestor__members__id=self.user_id) | Q(workers__id=self.user_id))

        organizations = self.me.organizations.exclude(id=self.me.default.id)

        return render(request, 'card_app/card-link.html', 
        {'card': card, 'forks': forks, 'ancestor': card.ancestor, 
        'attachments': attachments, 'user': self.me, 'workers': workers, 'path': path,
        'relations': relations, 'tags': tags, 'boardpins': boardpins,
        'listpins': listpins, 'cardpins': cardpins, 'grouppins': grouppins,
        'user': self.me, 'default': self.me.default, 'organization': self.me.default,
        'organizations': organizations, 'settings': settings})

class ListCards(GuardianView):
    """
    """

    def get(self, request, list_id):
        list = list_app.models.List.objects.get(id=list_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        listpins = self.me.listpin_set.filter(organization=self.me.default)
        cardpins = self.me.cardpin_set.filter(organization=self.me.default)
        grouppins = self.me.grouppin_set.filter(organization=self.me.default)
        postpins = self.me.postpin_set.filter(organization=self.me.default)

        filter, _ = models.CardFilter.objects.get_or_create(
        user=self.me, organization=self.me.default, list=list)

        cards = list.cards.all()
        total = cards.count()
        cards = cards.filter(done=False)

        cards = filter.from_sqcard(cards) if filter.status else cards
        count = cards.count()

        workers1 = User.objects.filter(pk=self.me.pk, tasks=OuterRef('pk'))
        cards = cards.annotate(in_workers=Exists(workers1))
        cards = cards.annotate(has_workers=Count('workers'))

        # Need to be optmized.
        cards = cards.only('parent', 'label', 'id', 'owner__email',
        'owner__name', 'created')

        # cards = cards.order_by('-created')
        cards = cards.order_by('-priority')

        return render(request, 'card_app/list-cards.html', 
        {'list': list, 'total': total, 'cards': cards, 'filter': filter, 'postpins': postpins,
        'boardpins': boardpins, 'listpins':listpins, 'cardpins': cardpins, 'grouppins': grouppins,
        'user': self.me, 'board': list.ancestor, 'count': count})

class ViewData(GuardianView):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)

        # boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        # listpins = self.me.listpin_set.filter(organization=self.me.default)
        # cardpins = self.me.cardpin_set.filter(organization=self.me.default)
        # grouppins = self.me.grouppin_set.filter(organization=self.me.default)

        forks = card.forks.all()
        workers = card.workers.all()
        attachments = card.cardfilewrapper_set.all()
        tags = card.tags.all()
        relations = card.related.all()
        path = card.path.all()
        # post_forks = card.post_forks.all()
        # This doesnt work because the board members should be
        # notified of a card being related to other card.
        # It turns out to be reasonable if the a given board card
        # is related to some other card and both board members
        # (maybe card workers) get notified of it.
        # If the user has information scope thats restricted
        # he should use simple card links for relating.
        # relations = relations.filter(Q(
        # ancestor__ancestor__members__id=self.user_id) | Q(workers__id=self.user_id))

        return render(request, 'card_app/view-data.html', 
        {'card': card, 'forks': forks, 'ancestor': card.ancestor, 'path': path,
        'attachments': attachments, 'user': self.me, 'workers': workers,  
        'relations': relations, 'tags': tags})

class ConfirmCardDeletion(GuardianView):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)

        return render(request, 'card_app/confirm-card-deletion.html', 
        {'card': card})

class SetDeadline(GuardianView):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)
        form = forms.DeadlineForm(instance=card)

        return render(request, 'card_app/set-deadline.html', {'card': card, 'form': form})

    def post(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)
        form = forms.DeadlineForm(request.POST, instance=card)

        if not form.is_valid():
            return render(request, 'card_app/set-deadline.html', 
                {'form': form, 'card': card}, status=400)

        record = form.save(commit=False)
        record.expired = False
        record.save()

        event = models.ESetCardDeadline.objects.create(
        organization=self.me.default, card=card, ancestor=card.ancestor, 
        board=card.ancestor.ancestor, user=self.me)
        event.dispatch(*card.ancestor.ancestor.members.all(), *card.workers.all())

        return redirect('card_app:view-data', card_id=card.id)

class CreateCard(GuardianView):
    """
    """

    def get(self, request, ancestor_id):
        ancestor = list_app.models.List.objects.get(id=ancestor_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        form = forms.CardForm()
        return render(request, 'card_app/create-card.html', 
        {'form':form, 'ancestor':ancestor})

    def post(self, request, ancestor_id):
        ancestor = list_app.models.List.objects.get(id=ancestor_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        boardship = self.me.member_boardship.get(board=ancestor.ancestor)

        if boardship.status == '2':
            return HttpResponse("Board guests can't create cards!", status=403)

        form = forms.CardForm(request.POST)

        if not form.is_valid():
            return render(request, 'card_app/create-card.html', 
                {'form': form, 'ancestor': ancestor}, status=400)

        card          = form.save(commit=False)
        card.owner    = self.me
        card.ancestor = ancestor
        card.save()

        event = models.ECreateCard.objects.create(organization=self.me.default,
        ancestor=card.ancestor, board=card.ancestor.ancestor, card=card, user=self.me)
        event.dispatch(*ancestor.ancestor.members.all())

        REGX  ='card_app/card-link/([0-9]+)'
        ids   = findall(REGX, card.data)

        self.create_relations(card, ids)

        return redirect('card_app:view-data', card_id=card.id)

    def create_relations(self, card, ids):
        # It makes sure the card in fact can be accessed by the logged user.
        query0 = Q(ancestor__ancestor__organization=self.me.default)
        query1 = Q(ancestor__ancestor__members=self.me)
        query2 = Q(workers=self.me)
        query3 = query0 & (query1 | query2)
        cards  = Card.objects.filter(query3).distinct()
        cards  = cards.filter(id__in=ids)

        for ind in cards:
            self.relate(card, ind)
    
    def relate(self, card0, card1):
        card0.relations.add(card1)
        event = models.ERelateCard.objects.create(
        organization=self.me.default, ancestor0=card0.ancestor, 
        ancestor1=card1.ancestor, board0=card0.ancestor.ancestor, 
        board1=card1.ancestor.ancestor, card0=card0, card1=card1, user=self.me)

        event.dispatch(*card0.ancestor.ancestor.members.all())
        event.dispatch(*card1.ancestor.ancestor.members.all())

    def unrelate(self, card0, card1):
        pass

class SelectForkList(GuardianView):
    def get(self, request, card_id):
        card   = models.Card.locate(self.me, self.me.default, card_id)
        form   = forms.ListSearchform()
        boards = self.me.boards.filter(organization=self.me.default)
        lists  = List.objects.filter(ancestor__in=boards)

        return render(request, 'card_app/select-fork-list.html', 
        {'form':form, 'card': card, 'elems': lists})

    def post(self, request, card_id):
        sqlike = List.from_sqlike()
        form   = forms.ListSearchform(request.POST, sqlike=sqlike)
        card   = models.Card.locate(self.me, self.me.default, card_id)

        if not form.is_valid():
            return render(request, 'card_app/select-fork-list.html', 
                  {'form':form, 'card': card})

        boards = self.me.boards.filter(organization=self.me.default)
        lists = List.objects.filter(ancestor__in=boards)
        lists  = sqlike.run(lists)
        return render(request, 'card_app/select-fork-list.html', 
        {'form':form, 'card': card, 'elems': lists})

class PullCardContent(GuardianView):
    """
    """

    def get(self, request, ancestor_id, card_id):
        # Allow to pull just if the destination list is accessible
        # by the user and belongs to his default organization.
        ancestor = list_app.models.List.objects.get(id=ancestor_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        card = models.Card.locate(self.me, self.me.default, card_id)
        form = forms.CardForm(initial={'label': card.label, 'data': card.data})

        return render(request, 'card_app/create-fork.html', 
        {'form':form, 'card': card, 'ancestor': ancestor})

class CreateFork(GuardianView):
    """
    """

    def get(self, request, ancestor_id, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)
        ancestor = list_app.models.List.objects.get(id=ancestor_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        form = forms.CardForm()

        return render(request, 'card_app/create-fork.html', 
        {'form':form, 'card': card, 'ancestor': ancestor})

    def post(self, request, ancestor_id, card_id):
        card     = models.Card.locate(self.me, self.me.default, card_id)
        ancestor = list_app.models.List.objects.get(id=ancestor_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        form = forms.CardForm(request.POST)

        if not form.is_valid():
            return render(request, 'card_app/create-fork.html', 
                {'form':form, 'ancestor': ancestor, 'card': card}, status=400)

        fork          = form.save(commit=False)
        fork.owner    = self.me
        fork.ancestor = ancestor
        fork.parent   = card
        fork.deadline = card.deadline
        fork.expired  = card.expired
        fork.save()

        path = card.path.all()
        fork.path.add(*path, card)

        event = models.ECreateFork.objects.create(organization=self.me.default,
        ancestor0=card.ancestor, ancestor1=fork.ancestor, card0=card, 
        card1=fork, user=self.me, board0=card.ancestor.ancestor, 
        board1=fork.ancestor.ancestor)

        event.dispatch(*card.workers.all(), 
        *card.ancestor.ancestor.members.all())

        return redirect('card_app:view-data', card_id=fork.id)

@method_decorator(csrf_exempt, name='dispatch')
class ArchiveAll(GuardianView):
    def get(self, request, list_id):
        list = List.objects.get(id=list_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        return render(request, 'card_app/archive-all.html', {'list': list})

    def post(self, request, list_id):
        list = List.objects.get(id=list_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        boardship = self.me.member_boardship.get(board=list.ancestor)
        if boardship.status == '2':
            return HttpResponse("Board guests can't \
                archive cards!", status=403)

        cards = list.cards.filter(done=False)
        cards = cards.filter(Q(forks__done=True) | Q(forks__isnull=True))

        event = models.EArchiveCard.objects.create(
        organization=self.me.default, ancestor=list, 
        board=list.ancestor, user=self.me)

        event.save(hcache=False)
        event.cards.add(*cards)

        users = list.ancestor.members.all()
        workers = User.objects.filter(tasks__ancestor=list)
        event.dispatch(*users, *workers)
        event.save()

        cards.update(done=True)
        return redirect('card_app:list-cards', list_id=list.id)

class DeleteCard(GuardianView):
    def post(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)
        boardship = self.me.member_boardship.get(board=card.ancestor.ancestor)

        if boardship.status == '2':
            return HttpResponse("Board guests can't delete cards!", status=403)

        event = models.EDeleteCard.objects.create(organization=self.me.default,
        ancestor=card.ancestor, board=card.ancestor.ancestor, 
        label=card.label, user=self.me)

        event.dispatch(*card.workers.all(), 
        *card.ancestor.ancestor.members.all())
        card.delete()

        return redirect('card_app:list-cards', 
        list_id=card.ancestor.id)

class CutCard(GuardianView):
    def post(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)
        boardship = self.me.member_boardship.get(board=card.ancestor.ancestor)

        if boardship.status == '2':
            return HttpResponse("Board guests can't cut cards!", status=403)

        list = card.ancestor
        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)
    
        # To avoid the possibility of another user/me
        # having cut a card with the same priority from
        # other list which entails in cards with equal priority
        # when pasting over somewhere.
        card.priority = clipboard.cards.count() + 1
        card.ancestor  = None
        card.save()

        clipboard.cards.add(card)
        event = models.ECutCard.objects.create(organization=self.me.default,
        ancestor=list, board=list.ancestor, card=card, user=self.me)
        event.dispatch(*list.ancestor.members.all(), *card.workers.all())

        return redirect('card_app:list-cards', 
        list_id=list.id)

class CopyCard(GuardianView):
    def post(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)
        boardship = self.me.member_boardship.get(board=card.ancestor.ancestor)

        if boardship.status == '2':
            return HttpResponse("Board guests can't copy cards!", status=403)

        copy = card.duplicate()

        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)
        copy.priority = clipboard.cards.count() + 1
        copy.save()

        clipboard.cards.add(copy)

        event = models.ECopyCard.objects.create(organization=self.me.default,
        ancestor=card.ancestor, board=card.ancestor.ancestor, 
        card=card, user=self.me)

        event.dispatch(*card.workers.all(), 
        *card.ancestor.ancestor.members.all())

        return redirect('card_app:list-cards', 
        list_id=card.ancestor.id)

class AttachFile(GuardianView):
    """
    """

    def get(self, request, card_id):
        card     = models.Card.locate(self.me, self.me.default, card_id)
        attachments = card.cardfilewrapper_set.all()
        form = forms.CardFileWrapperForm()
        return render(request, 'card_app/attach-file.html', 
        {'card':card, 'form': form, 'attachments': attachments})

    def post(self, request, card_id):
        card        = models.Card.locate(self.me, self.me.default, card_id)

        attachments = card.cardfilewrapper_set.all()

        form = forms.CardFileWrapperForm(request.POST, 
        request.FILES, user=self.me)

        if not form.is_valid():
            return render(request, 'card_app/attach-file.html', 
                {'card':card, 'form': form, 'attachments': attachments})

        record = form.save(commit = False)
        record.card = card
        record.organization = self.me.default
        form.save()

        event = models.EAttachCardFile.objects.create(
        organization=self.me.default, list=card.ancestor, filewrapper=record, 
        board=card.ancestor.ancestor, card=card, user=self.me)

        event.dispatch(*card.workers.all(), *card.ancestor.ancestor.members.all())
        event.save()

        return self.get(request, card_id)

class DetachFile(GuardianView):
    """
    """

    def get(self, request, filewrapper_id):
        filewrapper = models.CardFileWrapper.objects.filter(
        Q(card__ancestor__ancestor__members=self.me) | Q(card__workers=self.me),
        id=filewrapper_id, card__ancestor__ancestor__organization=self.me.default)
        filewrapper = filewrapper.distinct().first()

        boardship = self.me.member_boardship.get(
            board=filewrapper.card.ancestor.ancestor)

        if boardship.status == '2':
            return HttpResponse("Board guests can't dettach files!", status=403)

        attachments = filewrapper.card.cardfilewrapper_set.all()
        form = forms.CardFileWrapperForm()

        event = models.EDettachCardFile.objects.create(
        organization=self.me.default, filename=filewrapper.file.name, 
        list=filewrapper.card.ancestor, board=filewrapper.card.ancestor.ancestor, 
        card=filewrapper.card, user=self.me)

        filewrapper.delete()

        event.dispatch(*filewrapper.card.workers.all(), 
        *filewrapper.card.ancestor.ancestor.members.all())
        event.save()

        return render(request, 'card_app/attach-file.html', 
        {'card':filewrapper.card, 'form': form, 'attachments': attachments})

class UpdateCard(CreateCard):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)
        return render(request, 'card_app/update-card.html',
        {'card': card, 'form': forms.CardForm(instance=card),})

    def post(self, request, card_id):
        record = models.Card.locate(self.me, self.me.default, card_id)
        boardship = self.me.member_boardship.get(board=record.ancestor.ancestor)

        if boardship.status == '2':
            return HttpResponse("Board guests can't update cards!", status=403)

        event = models.EUpdateCard.objects.create(card_data=record.data, card_html=record.html,
        organization=self.me.default, ancestor=record.ancestor, card_label=record.label,
        board=record.ancestor.ancestor, card=record, user=self.me)

        form  = forms.CardForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'card_app/update-card.html',
                        {'form': form, 'card':record, }, status=400)

        record.save()

        event.dispatch(*record.workers.all(), 
        *record.ancestor.ancestor.members.all())
        event.save()

        REGX  ='card_app/card-link/([0-9]+)'
        ids   = findall(REGX, record.data)

        self.update_relations(record, ids)

        return redirect('card_app:view-data', 
        card_id=record.id)

    def update_relations(self, card, ids):
        # It makes sure the card in fact can be 
        # accessed by the logged user.
        query0 = Q(ancestor__ancestor__organization=self.me.default)
        query1 = Q(ancestor__ancestor__members=self.me)
        query2 = Q(workers=self.me)
        query3 = query0 & (query1 | query2)
        cards  = Card.objects.filter(query3).distinct()
        cards  = cards.filter(id__in=ids)
        cards  = cards.exclude(id__in=card.relations.all())

        for ind in cards:
            self.relate(card, ind)

        cards = card.relations.exclude(id__in=ids)
        for ind in cards:
            self.unrelate(card, ind)

    def unrelate(self, card0, card1):
        card0.relations.remove(card1)
        card0.save()

        event = models.EUnrelateCard.objects.create(
        organization=self.me.default, ancestor0=card0.ancestor, 
        ancestor1=card1.ancestor, board0=card0.ancestor.ancestor, 
        board1=card1.ancestor.ancestor, card0=card0, 
        card1=card1, user=self.me)

        event.dispatch(*card0.ancestor.ancestor.members.all(),
        *card1.ancestor.ancestor.members.all(), *card0.workers.all(),
        *card1.workers.all())

class SetupCardFilter(GuardianView):
    def get(self, request, list_id):
        list = list_app.models.List.objects.get(id=list_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        filter = models.CardFilter.objects.get(user__id=self.user_id, 
        organization__id=self.me.default.id, list__id=list_id)

        return render(request, 'card_app/setup-card-filter.html', 
        {'form': forms.CardFilterForm(instance=filter), 
        'list': list})

    def post(self, request, list_id):
        list = list_app.models.List.objects.get(id=list_id, 
        ancestor__organization=self.me.default, ancestor__members=self.me)

        filter = models.CardFilter.objects.get(user__id=self.user_id, 
        organization__id=self.me.default.id, list__id=list_id)

        sqlike = SqCard()
        form   = forms.CardFilterForm(request.POST, 
            sqlike=sqlike, instance=filter)

        if not form.is_valid():
            return render(request, 'card_app/setup-card-filter.html',
                   {'form': form, 'list': list}, status=400)

        form.save()
        return redirect('card_app:list-cards', list_id=list_id)


class PinCard(GuardianView):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)

        pin  = CardPin.objects.create(user=self.me, 
        organization=self.me.default, card=card)

        return redirect('board_app:list-pins')

class Done(GuardianView):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)
        boardship = self.me.member_boardship.get(board=card.ancestor.ancestor)
        if boardship.status == '2':
            return HttpResponse("Board guests can't \
                archive cards!", status=403)

        can_archive = all(card.forks.values_list('done', flat=True))
        if not can_archive:
            return HttpResponse("It has unarchived forks\
                    cards. Can't archive it now", status=403)

        card.done = True
        card.save()

        # cards in the clipboard cant be archived.
        event    = models.EArchiveCard.objects.create(
        organization=self.me.default, ancestor=card.ancestor, 
        board=card.ancestor.ancestor, user=self.me)

        event.save(hcache=False)
        event.cards.add(card)

        users = card.ancestor.ancestor.members.all()
        event.dispatch(*card.workers.all(), *users)
        event.save()

        return redirect('card_app:list-cards', list_id=card.ancestor.id)

class Undo(GuardianView):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)
        boardship = self.me.member_boardship.get(board=card.ancestor.ancestor)
        if boardship.status == '2':
            return HttpResponse("Board guests can't \
                unaarchive cards!", status=403)

        card.done = False
        card.save()
        # cards in the clipboard cant be archived.
        event    = models.EUnarchiveCard.objects.create(
        organization=self.me.default, ancestor=card.ancestor, 
        board=card.ancestor.ancestor, card=card, user=self.me)

        users = card.ancestor.ancestor.members.all()
        event.dispatch(*card.workers.all(), *users)

        return redirect('card_app:list-cards', list_id=card.ancestor.id)

class CardWorkerInformation(GuardianView):
    def get(self, request, peer_id, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)
        peer = User.objects.get(id=peer_id, organizations=self.me.default)

        taskship = models.CardTaskship.objects.get(worker=peer, card=card)

        active_posts = peer.assignments.filter(done=False)
        done_posts = peer.assignments.filter(done=True)

        active_cards = peer.tasks.filter(done=False)
        done_cards = peer.tasks.filter(done=True)

        active_tasks = active_posts.count() + active_cards.count()
        done_tasks = done_posts.count() + done_cards.count()

        return render(request, 'card_app/card-worker-information.html', 
        {'peer': peer, 'created': taskship.created, 'active_tasks': active_tasks,
        'done_tasks': done_tasks, 'assigner':taskship.assigner, 'card': card})

class RequestCardAttention(GuardianView):
    def get(self, request, peer_id, card_id):
        peer = User.objects.get(id=peer_id, organizations=self.me.default)
        card = models.Card.locate(self.me, self.me.default, card_id)

        form = forms.CardAttentionForm()
        return render(request, 'card_app/request-card-attention.html', 
        {'peer': peer,  'card': card, 'form': form})

    def post(self, request, peer_id, card_id):
        peer = User.objects.get(id=peer_id, organizations=self.me.default)
        card = models.Card.locate(self.me, self.me.default, card_id)

        form = forms.CardAttentionForm(request.POST)

        if not form.is_valid():
            return render(request, 'card_app/request-card-attention.html', 
                    {'peer': peer, 'card': card, 'form': form})    

        url  = reverse('card_app:card-link', 
            kwargs={'card_id': card.id})

        url = '%s%s' % (settings.LOCAL_ADDR, url)
        msg = '%s (%s) has requested your attention on\n%s\n\n%s' % (
        self.me.name, self.me.email, url, form.cleaned_data['message'])

        send_mail('%s %s' % (self.me.default.name, 
        self.me.name), msg, self.me.email, [peer.email], fail_silently=False)
        return redirect('card_app:card-worker-information', 
        peer_id=peer.id, card_id=card.id)

class CardTagInformation(GuardianView):
    def get(self, request, tag_id, card_id):
        card    = models.Card.locate(self.me, self.me.default, card_id)
        tag     = Tag.objects.get(id=tag_id, organization=self.me.default)
        tagship = models.CardTagship.objects.get(card=card, tag=tag)

        return render(request, 'card_app/card-tag-information.html', 
        {'tagger': tagship.tagger, 'card': card, 
        'created': tagship.created, 'tag':tag})

class AlertCardWorkers(GuardianView):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)

        form = forms.AlertCardWorkersForm()
        return render(request, 'card_app/alert-card-workers.html', 
        {'card': card, 'form': form, 'user': self.me})

    def post(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)
        form = forms.AlertCardWorkersForm(request.POST)

        if not form.is_valid():
            return render(request,'card_app/alert-card-workers.html', 
                    {'user': self.me, 'card': card, 'form': form})    

        url  = reverse('card_app:card-link', 
        kwargs={'card_id': card.id})

        url = '%s%s' % (settings.LOCAL_ADDR, url)
        msg = '%s (%s) has alerted you on\n%s\n\n%s' % (
        self.me.name, self.me.email, url, form.cleaned_data['message'])

        for ind in card.workers.values_list('email'):
            send_mail('%s %s' % (self.me.default.name, 
                self.me.name), msg, self.me.email, 
                    [ind[0]], fail_silently=False)

        return render(request, 'card_app/alert-card-workers-sent.html', {})


class Find(GuardianView):
    def get(self, request):
        filter, _ = CardSearch.objects.get_or_create(
        user=self.me, organization=self.me.default)

        form   = forms.CardSearchForm(instance=filter)
        query0 = Q(ancestor__ancestor__organization=self.me.default)
        query1 = Q(ancestor__ancestor__members=self.me)
        query2 = Q(workers=self.me)
        query3 = query0 & (query1 | query2)
        cards  = Card.objects.filter(query3).distinct()
        total  = cards.count()

        cards  = filter.get_partial(cards)
        sqlike = SqCard()

        sqlike.feed(filter.pattern)

        cards = sqlike.run(cards)
        count = cards.count()

        cards = cards.only('done', 'label', 'id').order_by('id')
        elems = JScroll(self.me.id, 'card_app/find-scroll.html', cards)

        return render(request, 'card_app/find.html', 
        {'form': form, 'elems':  elems.as_div(), 'total': total, 'count': count})

    def post(self, request):
        filter, _ = CardSearch.objects.get_or_create(
        user=self.me, organization=self.me.default)

        sqlike = SqCard()
        form   = forms.CardSearchForm(request.POST, 
        sqlike=sqlike, instance=filter)

        query0 = Q(ancestor__ancestor__organization=self.me.default)
        query1 = Q(ancestor__ancestor__members=self.me)
        query2 = Q(workers=self.me)
        query3 = query0 & (query1 | query2)
        cards  = Card.objects.filter(query3).distinct()
        total  = cards.count()

        if not form.is_valid():
            return render(request, 'card_app/find.html', 
                {'form': form, 'total': total, 'count': 0}, status=400)
        form.save()

        cards  = filter.get_partial(cards)
        cards = sqlike.run(cards)

        count =  cards.count()
        cards = cards.only('done', 'label', 'id').order_by('id')
        elems = JScroll(self.me.id, 'card_app/find-scroll.html', cards)

        return render(request, 'card_app/find.html', 
        {'form': form, 'elems':  elems.as_div(), 'total': total, 'count': count})

class CardEvents(GuardianView):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)

        query = Q(erelatecard__card0__id=card.id) | Q(erelatecard__card1__id=card.id) \
        | Q(eunrelatecard__card0__id=card.id) | Q(eunrelatecard__card1__id=card.id) | \
        Q(ecreatecard__card__id=card.id) | Q(ebindcardworker__card__id=card.id) | \
        Q(eunbindcardworker__card__id=card.id) | Q(ecreatefork__card0=card.id) \
        | Q(ecreatefork__card1=card.id) | Q(ecreatepostfork__card__id=card.id) | \
        Q(eupdatecard__card__id=card.id) | Q(ebindtagcard__card__id=card.id) | \
        Q(eunbindtagcard__card__id=card.id) | Q(ecutcard__card__id=card.id) |\
        Q(earchivecard__cards__id=card.id) | Q(epastecard__cards=card.id) | \
        Q(ecopycard__card=card.id) | Q(eattachcardfile__card=card.id) |\
        Q(edettachcardfile__card=card.id) | Q(eupdatenote__child=card.id) |\
        Q(ecreatenote__child=card.id) | Q(edeletenote__child=card.id) |\
        Q(eattachnotefile__note__card=card.id) | \
        Q(edettachnotefile__note__card=card.id)|\
        Q(ecreatepostfork__card=card.id) |\
        Q(esetcardpriorityup__card0=card.id) |\
        Q(esetcardprioritydown__card0=card.id) |\
        Q(esetcardpriorityup__card1=card.id) |\
        Q(esetcardprioritydown__card1=card.id) |\
        Q(eunarchivecard__card__id=card.id)|\
        Q(esetcarddeadline__card__id=card.id)|\
        Q(ebitbucketcommit__note__card__id=card.id)|\
        Q(erestorenote__card__id=card.id)|\
        Q(erestorecard__card__id=card.id)

        events = Event.objects.filter(query).order_by('-created').values('html')
        count = events.count()
        return render(request, 'card_app/card-events.html', 
        {'card': card, 'elems': events, 'count': count})

class CardPriority(GuardianView):
    def get(self, request, card_id):
        card  = models.Card.locate(self.me, self.me.default, card_id)
        cards = card.ancestor.cards.filter(done=False)
        cards = cards.exclude(id=card_id)
        cards = cards.order_by('-priority')
        total = cards.count()

        return render(request, 'card_app/card-priority.html', 
        {'card': card, 'total': total, 'count': total, 'me': self.me,
        'cards': cards, 'form': forms.CardPriorityForm()})

    def post(self, request, card_id):
        sqlike = SqCard()
        card   = models.Card.locate(self.me, self.me.default, card_id)
        cards  = card.ancestor.cards.filter(done=False)
        cards = cards.exclude(id=card_id)
        total  = cards.count()
        form   = forms.CardPriorityForm(request.POST, sqlike=sqlike)

        if not form.is_valid():
            return render(request, 'card_app/card-priority.html', 
                {'me': self.me, 'organization': self.me.default, 'card': card,
                     'total': total, 'count': 0, 'form':form}, status=400)

        cards = sqlike.run(cards)
        cards = cards.order_by('-priority')

        count = cards.count()

        return render(request, 'card_app/card-priority.html', 
        {'card': card, 'total': total, 'count': count, 'me': self.me,
        'cards': cards, 'form': form})

class SetCardPriorityUp(GuardianView):
    @transaction.atomic
    def get(self, request, card0_id, card1_id):
        card0  = models.Card.locate(self.me, self.me.default, card0_id)
        card1  = models.Card.locate(self.me, self.me.default, card1_id)
        dir    = -1 if card0.priority < card1.priority else 1
        flag   = 0 if card0.priority <= card1.priority else 1

        q0     = Q(priority__lte=card1.priority, priority__gt=card0.priority)
        q1     = Q(priority__gt=card1.priority, priority__lt=card0.priority)
        query  =  q0 if card0.priority < card1.priority else q1
        cards  = card0.ancestor.cards.filter(query)

        cards.update(priority=F('priority') + dir)
        card0.priority = card1.priority + flag
        card0.save()

        event = models.ESetCardPriorityUp.objects.create(
        organization=self.me.default, ancestor=card0.ancestor, 
        board=card0.ancestor.ancestor, card0=card0, card1=card1, user=self.me)

        event.dispatch(*card0.ancestor.ancestor.members.all())
        print('Priority', [[ind.label, ind.priority] 
        for ind in card0.ancestor.cards.all().order_by('-priority')])

        return redirect('card_app:list-cards', list_id=card0.ancestor.id)

class SetCardPriorityDown(GuardianView):
    @transaction.atomic
    def get(self, request, card0_id, card1_id):
        card0  = models.Card.locate(self.me, self.me.default, card0_id)
        card1  = models.Card.locate(self.me, self.me.default, card1_id)
        dir    = -1 if card0.priority < card1.priority else 1
        flag   = -1 if card0.priority < card1.priority else 0

        q0     = Q(priority__lt=card1.priority, priority__gt=card0.priority)
        q1     = Q(priority__gte=card1.priority, priority__lt=card0.priority)
        query  = q0 if card0.priority < card1.priority else q1
        cards  = card0.ancestor.cards.filter(query)

        cards.update(priority=F('priority') + dir)
        card0.priority = card1.priority + flag
        card0.save()

        event = models.ESetCardPriorityDown.objects.create(
        organization=self.me.default, ancestor=card0.ancestor, 
        board=card0.ancestor.ancestor, card0=card0, card1=card1, user=self.me)

        event.dispatch(*card0.ancestor.ancestor.members.all())
        print('Priority', [[ind.label, ind.priority] for ind in card0.ancestor.cards.all().order_by('-priority')])

        return redirect('card_app:list-cards', list_id=card0.ancestor.id)

class Unpin(GuardianView):
    def get(self, request, pin_id):
        pin = self.me.cardpin_set.get(id=pin_id)
        pin.delete()
        return redirect('board_app:list-pins')



class CardFileDownload(FileDownload):
    def get(self, request, filewrapper_id):
        filewrapper = models.CardFileWrapper.objects.filter(
        Q(card__ancestor__ancestor__members=self.me) | Q(card__workers=self.me),
        id=filewrapper_id, card__ancestor__ancestor__organization=self.me.default)
        filewrapper = filewrapper.distinct().first()

        return self.get_file_url(filewrapper.file)


class UnbindCardWorkers(GuardianView):
    """
    """

    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)
        included = card.workers.all()
        total    = included.count() 

        return render(request, 'card_app/unbind-card-workers.html', {
        'included': included, 'card': card, 'organization': self.me.default,
        'form':forms.UserSearchForm(), 'me': self.me, 
        'count': total, 'total': total,})

    def post(self, request, card_id):
        sqlike   = SqUser()
        form     = forms.UserSearchForm(request.POST, sqlike=sqlike)

        card     = models.Card.objects.get(id=card_id)
        included = card.workers.all()
        users    = self.me.default.users.all()
        total    = included.count() 
        
        if not form.is_valid():
            return render(request, 'card_app/unbind-card-workers.html', 
                {'me': self.me, 'card': card, 'count': 0, 'total': total,
                        'form':form}, status=400)

        included = sqlike.run(included)
        count = included.count() 

        return render(request, 'card_app/unbind-card-workers.html', 
        {'included': included, 'card': card, 'me': self.me, 
        'organization': self.me.default,'form':form, 
        'count': count, 'total': total,})

class BindCardWorkers(GuardianView):
    """
    The listed users are supposed to belong to the logged user default
    organization. It also checks if the user belongs to the card
    in order to list its users.
    """

    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)

        users  = self.me.default.users.all()
        excluded = users.exclude(tasks=card)
        total    = excluded.count()

        return render(request, 'card_app/bind-card-workers.html', 
        {'excluded': excluded, 'card': card, 'me': self.me, 
        'organization': self.me.default,'form':forms.UserSearchForm(), 
        'count': total, 'total': total,})

    def post(self, request, card_id):
        sqlike   = SqUser()
        form     = forms.UserSearchForm(request.POST, sqlike=sqlike)
        card     = models.Card.objects.get(id=card_id)
        users    = self.me.default.users.all()
        excluded = users.exclude(tasks=card)

        total = excluded.count()
        
        if not form.is_valid():
            return render(request, 'card_app/bind-card-workers.html', 
                {'me': self.me, 'card': card, 'count': 0, 'total': total,
                        'form':form}, status=400)

        excluded = sqlike.run(excluded)
        count = excluded.count()

        return render(request, 'card_app/bind-card-workers.html', 
        {'excluded': excluded, 'card': card, 'me': self.me, 
        'organization': self.me.default,'form':form, 
        'count': count, 'total': total,})

class CreateCardTaskshipUser(GuardianView):
    """
    """

    def get(self, request, card_id, user_id):
        user  = User.objects.get(id=user_id, organizations=self.me.default)
        card = models.Card.objects.get(id=card_id)
        form  = forms.CardTaskshipForm()

        return render(request, 'card_app/create-card-taskship-user.html', {
        'user': user, 'card': card, 'form': form})

    def post(self, request, card_id, user_id):
        user = User.objects.get(id=user_id, organizations=self.me.default)
        card = models.Card.objects.get(id=card_id)

        boardship0 = self.me.member_boardship.get(board=card.ancestor.ancestor)
        error0     = "Board guests can't bind card workers!"

        if boardship0.status == '2':
            return HttpResponse(error0, status=403)

        form = forms.CardTaskshipForm(request.POST)
        if not form.is_valid():
            return render(request, 'card_app/create-card-taskship-user.html', {
                'user': user, 'card': card, 'form': form})

        record          = form.save(commit=False)
        record.worker   = user
        record.assigner = self.me
        record.card     = card
        record.save()


        event = models.EBindCardWorker.objects.create(status=record.status,
        organization=self.me.default, ancestor=card.ancestor, 
        board=card.ancestor.ancestor, card=card, user=self.me, peer=user)

        event.dispatch(*card.workers.all(),
        *card.ancestor.ancestor.members.all())
        event.save()

        return redirect('card_app:bind-card-workers', card_id=card.id)

class DeleteCardTaskshipUser(GuardianView):
    def post(self, request, card_id, user_id):
        user  = User.objects.get(id=user_id, organizations=self.me.default)
        card = models.Card.objects.get(id=card_id)
        boardship = self.me.member_boardship.get(board=card.ancestor.ancestor)

        if boardship.status == '2':
            return HttpResponse("Board guests can't \
                unbind card workers!", status=403)

        event = models.EUnbindCardWorker.objects.create(
        organization=self.me.default, ancestor=card.ancestor, 
        board=card.ancestor.ancestor, card=card, user=self.me, peer=user)

        event.dispatch(*card.workers.all(), 
        *card.ancestor.ancestor.members.all())
        event.save()


        user.card_workership.get(card=card).delete()
        return redirect('card_app:unbind-card-workers', card_id=card.id)

class UnbindCardTags(GuardianView):
    """
    """

    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)

        included = card.tags.all()
        total    = included.count() 

        return render(request, 'card_app/unbind-card-tags.html', {
        'included': included, 'card': card, 'organization': self.me.default,
        'form':forms.TagSearchForm(), 'me': self.me, 
        'count': total, 'total': total,})

    def post(self, request, card_id):
        sqlike   = SqTag()
        form     = forms.TagSearchForm(request.POST, sqlike=sqlike)
        card     = models.Card.objects.get(id=card_id)

        included = card.tags.all()
        tags     = self.me.default.tags.all()
        total    = included.count() 
        
        if not form.is_valid():
            return render(request, 'card_app/unbind-card-tags.html', 
                {'me': self.me, 'card': card, 'count': 0, 'total': total,
                        'form':form}, status=400)

        included = sqlike.run(included)
        count = included.count() 

        return render(request, 'card_app/unbind-card-tags.html', 
        {'included': included, 'card': card, 'me': self.me, 
        'organization': self.me.default,'form':form, 
        'count': count, 'total': total,})

class BindCardTags(GuardianView):
    """
    The listed tags are supposed to belong to the logged tag default
    organization. It also checks if the tag belongs to the card
    in order to list its tags.
    """

    def get(self, request, card_id):
        card     = models.Card.objects.get(id=card_id)
        tags     = self.me.default.tags.all()
        excluded = tags.exclude(cards=card)
        total    = excluded.count()

        return render(request, 'card_app/bind-card-tags.html', 
        {'excluded': excluded, 'card': card, 'me': self.me, 
        'organization': self.me.default,'form':forms.TagSearchForm(), 
        'count': total, 'total': total,})

    def post(self, request, card_id):
        sqlike   = SqTag()
        form     = forms.TagSearchForm(request.POST, sqlike=sqlike)
        card     = models.Card.objects.get(id=card_id)
        tags     = self.me.default.tags.all()
        excluded = tags.exclude(cards=card)
        total    = excluded.count()
        
        if not form.is_valid():
            return render(request, 'card_app/bind-card-tags.html', 
                {'me': self.me, 'card': card, 'count': 0, 'total': total,
                        'form':form}, status=400)

        excluded = sqlike.run(excluded)
        count = excluded.count()

        return render(request, 'card_app/bind-card-tags.html', 
        {'excluded': excluded, 'card': card, 'me': self.me, 
        'organization': self.me.default,'form':form, 
        'count': count, 'total': total,})

class CreateCardTagship(GuardianView):
    """
    """

    def get(self, request, card_id, tag_id):
        tag  = Tag.objects.get(id=tag_id, organization=self.me.default)
        card = models.Card.objects.get(id=card_id)
        form  = forms.CardTagshipForm()

        return render(request, 'card_app/create-card-tagship.html', {
        'tag': tag, 'card': card, 'form': form})

    def post(self, request, card_id, tag_id):
        tag  = Tag.objects.get(id=tag_id, organization=self.me.default)
        card = models.Card.objects.get(id=card_id)

        boardship = self.me.member_boardship.get(board=card.ancestor.ancestor)
        if boardship.status == '2':
            return HttpResponse("Board guests can't \
                bind card tags!", status=403)

        form = forms.CardTagshipForm(request.POST)
        if not form.is_valid():
            return render(request, 'card_app/create-card-tagship.html', {
                'tag': tag, 'card': card, 'form': form})

        record        = form.save(commit=False)
        record.tag   = tag
        record.tagger = self.me
        record.card  = card
        record.save()

        event = EBindTagCard.objects.create(
        organization=self.me.default, ancestor=card.ancestor, 
        card=card, tag=tag, board=card.ancestor.ancestor, user=self.me)
        event.dispatch(*card.ancestor.ancestor.members.all(), *card.workers.all())
        event.save()



        return redirect('card_app:bind-card-tags', card_id=card.id)

class DeleteCardTagship(GuardianView):
    def post(self, request, card_id, tag_id):
        tag  = Tag.objects.get(id=tag_id, organization=self.me.default)
        card = models.Card.objects.get(id=card_id)

        boardship = self.me.member_boardship.get(board=card.ancestor.ancestor)
        if boardship.status == '2':
            return HttpResponse("Board guests can't \
                        unbind card tags!", status=403)

        event = EUnbindTagCard.objects.create(
        organization=self.me.default, ancestor=card.ancestor, 
        card=card, tag=tag, board=card.ancestor.ancestor, user=self.me)
        event.dispatch(*card.ancestor.ancestor.members.all(), *card.workers.all())
        event.save()

        CardTagship.objects.get(card=card, tag=tag).delete()
        return redirect('card_app:unbind-card-tags', card_id=card.id)

class CardDiff(GuardianView):
    def get(self, request, event_id):
        event = EUpdateCard.objects.get(id=event_id)

        # Necessary to check permissions.
        card = models.Card.locate(self.me, self.me.default, event.card.id)


        return render(request, 'card_app/card-diff.html', 
        {'card': card, 'event': event})

class RestoreCard(GuardianView):
    def post(self, request, event_id):
        event = EUpdateCard.objects.get(id=event_id)
        card  = models.Card.locate(self.me, self.me.default, event.card.id)

        boardship = self.me.member_boardship.get(board=card.ancestor.ancestor)

        if boardship.status == '2':
            return HttpResponse("Board guests can't update cards!", status=403)

        card.label = event.card_label
        card.data = event.card_data
        card.save()

        event = models.ERestoreCard.objects.create(
        event_html=event.html, organization=self.me.default, ancestor=card.ancestor,
        board=card.ancestor.ancestor, card=card, user=self.me)

        event.dispatch(*card.workers.all(), 
        *card.ancestor.ancestor.members.all())
        event.save()
        return redirect('card_app:view-data', card_id=card.id)





