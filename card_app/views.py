from django.shortcuts import render, redirect
from django.db.models.functions import Concat
from django.db.models import Q, F, Exists, OuterRef, Count, Value, CharField
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from card_app.models import GlobalTaskFilter, GlobalCardFilter, CardPin
from core_app.models import Clipboard, Event, Tag
from django.core.mail import send_mail
from core_app.views import GuardianView
from post_app.models import Post, ECreateCardFork
from post_app.forms import PostForm
from timeline_app.models import Timeline
from core_app.models import User
from list_app.models import List, EPasteCard
from django.db import transaction
from jsim.jscroll import JScroll
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

class CardLink(GuardianView):
    """
    """

    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)

        boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        listpins = self.me.listpin_set.filter(organization=self.me.default)
        cardpins = self.me.cardpin_set.filter(organization=self.me.default)
        timelinepins = self.me.timelinepin_set.filter(organization=self.me.default)

        forks = card.forks.all()
        workers = card.workers.all()
        attachments = card.cardfilewrapper_set.all()
        tags = card.tags.all()
        # snippets = card.snippets.all()
        relations = card.relations.all()
        path = card.path.all()

        relations = relations.filter(Q(
        ancestor__ancestor__members__id=self.user_id) | Q(workers__id=self.user_id))

        organizations = self.me.organizations.exclude(id=self.me.default.id)

        return render(request, 'card_app/card-link.html', 
        {'card': card, 'forks': forks, 'ancestor': card.ancestor, 
        'attachments': attachments, 'user': self.me, 'workers': workers, 'path': path,
        'relations': relations, 'tags': tags, 'boardpins': boardpins,
        'listpins': listpins, 'cardpins': cardpins, 'timelinepins': timelinepins,
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
        timelinepins = self.me.timelinepin_set.filter(organization=self.me.default)

        filter, _ = models.CardFilter.objects.get_or_create(
        user=self.me, organization=self.me.default, list=list)

        cards = list.cards.all()

        total = cards.count()

        cards = filter.collect(cards)
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
        {'list': list, 'total': total, 'cards': cards, 'filter': filter,
        'boardpins': boardpins, 'listpins':listpins, 'cardpins': cardpins, 'timelinepins': timelinepins,
        'user': self.me, 'board': list.ancestor, 'count': count})

class ViewData(GuardianView):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)

        boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        listpins = self.me.listpin_set.filter(organization=self.me.default)
        cardpins = self.me.cardpin_set.filter(organization=self.me.default)
        timelinepins = self.me.timelinepin_set.filter(organization=self.me.default)

        forks = card.forks.all()
        workers = card.workers.all()
        attachments = card.cardfilewrapper_set.all()
        tags = card.tags.all()
        # snippets = card.snippets.all()
        relations = card.relations.all()
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
        'attachments': attachments, 'user': self.me, 'workers': workers,  'timelinepins': timelinepins,
        'relations': relations, 'listpins': listpins, 'boardpins': boardpins,
        'cardpins': cardpins, 'tags': tags})

class ConfirmCardDeletion(GuardianView):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)

        return render(request, 'card_app/confirm-card-deletion.html', 
        {'card': card})

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

        form     = forms.CardForm(request.POST)

        if not form.is_valid():
            return render(request, 'card_app/create-card.html', 
                {'form': form, 'ancestor': ancestor}, status=400)

        card          = form.save(commit=False)
        card.owner    = self.me
        card.ancestor = ancestor
        card.save()

        event = models.ECreateCard.objects.create(organization=self.me.default,
        ancestor=card.ancestor, card=card, user=self.me)
        event.dispatch(*ancestor.ancestor.members.all())

        REGX  ='card_app/card-link/([0-9]+)'
        ids   = findall(REGX, card.data)

        self.create_relations(card, ids)

        return redirect('card_app:view-data', card_id=card.id)

    def create_relations(self, card, ids):
        cards = models.Card.objects.filter(id__in=ids)

        for ind in cards:
            self.relate(card, ind)
    
    def relate(self, card0, card1):
        card0.relations.add(card1)
        event = models.ERelateCard.objects.create(
        organization=self.me.default, ancestor0=card0.ancestor, 
        ancestor1=card1.ancestor, card0=card0, card1=card1, user=self.me)

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
        fork.save()

        path = card.path.all()
        fork.path.add(*path, card)

        event = models.ECreateFork.objects.create(organization=self.me.default,
        ancestor=card.ancestor, card0=card, card1=fork, user=self.me)
        event.dispatch(*card.ancestor.ancestor.members.all())

        return redirect('card_app:view-data', card_id=fork.id)

class DeleteCard(GuardianView):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)
        event = models.EDeleteCard.objects.create(organization=self.me.default,
        ancestor=card.ancestor, label=card.label, user=self.me)
        event.dispatch(*card.ancestor.ancestor.members.all())
        card.delete()

        return redirect('card_app:list-cards', 
        list_id=card.ancestor.id)

class CutCard(GuardianView):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)
        list = card.ancestor

        # Missing event.
        # user.ws_sound(card.ancestor.ancestor)

        card.ancestor = None
        card.save()

        clipboard, _    = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)
        clipboard.cards.add(card)

        event = models.ECutCard.objects.create(organization=self.me.default,
        ancestor=list, card=card, user=self.me)
        event.dispatch(*list.ancestor.members.all())

        return redirect('card_app:list-cards', 
        list_id=list.id)

class CopyCard(GuardianView):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)
        copy = card.duplicate()

        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)
        clipboard.cards.add(copy)

        event = models.ECopyCard.objects.create(organization=self.me.default,
        ancestor=card.ancestor, card=card, user=self.me)
        event.dispatch(*card.ancestor.ancestor.members.all())

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
        form        = forms.CardFileWrapperForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, 'card_app/attach-file.html', 
                {'card':card, 'form': form, 'attachments': attachments})
        record = form.save(commit = False)
        record.card = card
        form.save()

        event = models.EAttachCardFile.objects.create(
        organization=self.me.default, filewrapper=record, 
        card=card, user=self.me)

        event.dispatch(*card.ancestor.ancestor.members.all())
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

        attachments = filewrapper.card.cardfilewrapper_set.all()
        form = forms.CardFileWrapperForm()

        event = models.EDettachCardFile.objects.create(
        organization=self.me.default, filename=filewrapper.file.name, 
        card=filewrapper.card, user=self.me)

        filewrapper.delete()

        event.dispatch(*filewrapper.card.ancestor.ancestor.members.all())
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
        form    = forms.CardForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'card_app/update-card.html',
                        {'form': form, 'card':record, }, status=400)

        record.save()

        event = models.EUpdateCard.objects.create(
        organization=self.me.default, ancestor=record.ancestor, 
        card=record, user=self.me)
        event.dispatch(*record.ancestor.ancestor.members.all())
        event.save()

        REGX  ='card_app/card-link/([0-9]+)'
        ids   = findall(REGX, record.data)

        self.update_relations(record, ids)

        return redirect('card_app:view-data', 
        card_id=record.id)

    def update_relations(self, card, ids):
        cards = models.Card.objects.filter(id__in=ids)
        cards = cards.exclude(id__in=card.relations.all())
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
        ancestor1=card1.ancestor, card0=card0, 
        card1=card1, user=self.me)

        event.dispatch(*card0.ancestor.ancestor.members.all())
        event.dispatch(*card1.ancestor.ancestor.members.all())

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

        sqlike = models.Card.from_sqlike()
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

class ManageCardWorkers(GuardianView):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)

        included = card.workers.all()
        excluded = self.me.default.users.exclude(tasks=card)
        total = included.count() + excluded.count()

        return render(request, 'card_app/manage-card-workers.html', 
        {'included': included, 'excluded': excluded, 'card': card,
        'me': self.me, 'organization': self.me.default, 'total': total, 
        'count': total, 'form':forms.UserSearchForm()})

    def post(self, request, card_id):
        sqlike   = User.from_sqlike()
        form     = forms.UserSearchForm(request.POST, sqlike=sqlike)
        card     = models.Card.locate(self.me, self.me.default, card_id)
        included = card.workers.all()
        excluded = self.me.default.users.exclude(tasks=card)
        total    = included.count() + excluded.count()

        if not form.is_valid():
            return render(request, 'card_app/manage-card-workers.html', 
                {'me': self.me, 'card': card, 'form':form, 'total': total, 
                    'count': total,}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)
        count = included.count() + excluded.count()

        return render(request, 'card_app/manage-card-workers.html', 
        {'included': included, 'excluded': excluded, 'card': card, 'total': total,
        'count': count, 'me': self.me, 'form':form})

class UnbindCardWorker(GuardianView):
    def get(self, request, card_id, user_id):
        user = User.objects.get(id=user_id, organizations=self.me.default)
        card = models.Card.locate(self.me, self.me.default, card_id)

        card.workers.remove(user)
        card.save()

        event = models.EUnbindCardWorker.objects.create(
        organization=self.me.default, ancestor=card.ancestor, 
        card=card, user=self.me, peer=user)
        event.dispatch(*card.ancestor.ancestor.members.all())
        event.save()

        return HttpResponse(status=200)

class BindCardWorker(GuardianView):
    def get(self, request, card_id, user_id):
        user = User.objects.get(id=user_id, organizations=self.me.default)
        card = models.Card.locate(self.me, self.me.default, card_id)
        card.workers.add(user)
        card.save()

        event = models.EBindCardWorker.objects.create(
        organization=self.me.default, ancestor=card.ancestor, 
        card=card, user=self.me, peer=user)
        event.dispatch(*card.ancestor.ancestor.members.all())
        event.save()

        return HttpResponse(status=200)

class ManageCardTags(GuardianView):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)

        included = card.tags.all()
        excluded = self.me.default.tags.exclude(cards=card)
        total = included.count() + excluded.count()

        return render(request, 'card_app/manage-card-tags.html', 
        {'included': included, 'excluded': excluded, 'card': card,
        'organization': self.me.default,'form':forms.TagSearchForm(),
        'total': total, 'count': total})

    def post(self, request, card_id):
        sqlike = Tag.from_sqlike()
        form = forms.TagSearchForm(request.POST, sqlike=sqlike)

        card = models.Card.locate(self.me, self.me.default, card_id)

        included = card.tags.all()
        excluded = self.me.default.tags.exclude(cards=card)
        total = included.count() + excluded.count()

        if not form.is_valid():
            return render(request, 'card_app/manage-card-tags.html', 
                {'organization': self.me.default, 'card': card, 'total': total,
                        'count': 0, 'form':form}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)

        count = included.count() + excluded.count()

        return render(request, 'card_app/manage-card-tags.html', 
        {'included': included, 'excluded': excluded, 'card': card,
        'me': self.me, 'organization': self.me.default,
        'total': total, 'count': count, 'form':form})

class UnbindCardTag(GuardianView):
    def get(self, request, card_id, tag_id):
        tag = core_app.models.Tag.objects.get(id=tag_id, 
        organization=self.me.default)

        card = models.Card.locate(self.me, self.me.default, card_id)
        card.tags.remove(tag)
        card.save()

        event = models.EUnbindTagCard.objects.create(
        organization=self.me.default, ancestor=card.ancestor, 
        card=card, tag=tag, user=self.me)
        event.dispatch(*card.ancestor.ancestor.members.all())
        event.save()

        return HttpResponse(status=200)

class BindCardTag(GuardianView):
    def get(self, request, card_id, tag_id):
        tag = core_app.models.Tag.objects.get(id=tag_id, 
        organization=self.me.default)

        card = models.Card.locate(self.me, self.me.default, card_id)

        card.tags.add(tag)
        card.save()

        event = models.EBindTagCard.objects.create(
        organization=self.me.default, ancestor=card.ancestor, 
        card=card, tag=tag, user=self.me)
        event.dispatch(*card.ancestor.ancestor.members.all())
        event.save()

        return HttpResponse(status=200)

class Done(GuardianView):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)
        card.done = True
        card.save()


        # cards in the clipboard cant be archived.
        event    = models.EArchiveCard.objects.create(organization=self.me.default,
        ancestor=card.ancestor, card=card, user=self.me)

        users = card.ancestor.ancestor.members.all()
        event.dispatch(*users)

        return redirect('card_app:view-data', card_id=card.id)

class Undo(GuardianView):
    def get(self, request, card_id):
        card = models.Card.locate(self.me, self.me.default, card_id)
        card.done = False
        card.save()

        # cards in the clipboard cant be archived.
        event    = models.EUnarchiveCard.objects.create(organization=self.me.default,
        ancestor=card.ancestor, card=card, user=self.me)

        users = card.ancestor.ancestor.members.all()
        event.dispatch(*users)

        return redirect('card_app:view-data', card_id=card.id)

class CardWorkerInformation(GuardianView):
    def get(self, request, peer_id, card_id):
        event = models.EBindCardWorker.objects.filter(
        Q(card__workers=self.me) | Q(card__ancestor__ancestor__members=self.me),
        card__id=card_id, peer__id=peer_id).last()

        active_posts = event.peer.assignments.filter(done=False)
        done_posts = event.peer.assignments.filter(done=True)

        active_cards = event.peer.tasks.filter(done=False)
        done_cards = event.peer.tasks.filter(done=True)

        active_tasks = active_posts.count() + active_cards.count()
        done_tasks = done_posts.count() + done_cards.count()

        return render(request, 'card_app/card-worker-information.html', 
        {'peer': event.peer, 'created': event.created, 'active_tasks': active_tasks,
        'done_tasks': done_tasks, 'user':event.user, 'card': event.card})

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
        event = models.EBindTagCard.objects.filter(
        Q(card__ancestor__ancestor__members=self.me) | Q(card__workers=self.me),
        card__id=card_id, tag__id=tag_id).last()

        return render(request, 'post_app/post-tag-information.html', 
        {'user': event.user, 'created': event.created, 'tag':event.tag})

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


class UndoClipboard(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id,
        card_clipboard_users__organization=self.me.default,
        card_clipboard_users__user=self.me)

        event0 = card.e_copy_card1.last()
        event1 = card.e_cut_card1.last()

        # Then it is a copy because there is no event
        # mapped to it. A copy contains no e_copy_card1 nor
        # e_cut_card1.
        if not (event0 or event1):
            card.delete()
        else:
            self.undo_cut(event1)

        return redirect('core_app:list-clipboard')

    def undo_cut(self, event):
        event.card.ancestor = event.ancestor
        event.card.save()

        event1 = EPasteCard(
        organization=self.me.default, ancestor=event.ancestor, user=self.me)
        event1.save(hcache=False)
        event1.cards.add(event.card)
        event.dispatch(*event.ancestor.ancestor.members.all())
        event1.save()
        
        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)

        clipboard.cards.remove(event.card)

class ListAllTasks(GuardianView):
    def get(self, request):
        filter, _ = GlobalTaskFilter.objects.get_or_create(
        user=self.me, organization=self.me.default)

        form  = forms.GlobalTaskFilterForm(instance=filter)

        cards = models.Card.get_allowed_cards(self.me)
        cards = cards.filter(Q(workers__isnull=False))
        total = cards.count()
        cards = filter.get_partial(cards)
        
        sqlike = models.Card.from_sqlike()
        sqlike.feed(filter.pattern)

        cards = sqlike.run(cards)

        count = cards.count()
        cards = cards.only('done', 'label', 'id').order_by('id')
        elems = JScroll(self.me.id, 'card_app/list-all-tasks-scroll.html', cards)

        return render(request, 'card_app/list-all-tasks.html', 
        {'total': total, 'count': count, 
        'form': form, 'elems': elems.as_div()})

    def post(self, request):
        filter, _ = GlobalTaskFilter.objects.get_or_create(
        user=self.me, organization=self.me.default)

        sqlike = models.Card.from_sqlike()
        form   = forms.GlobalTaskFilterForm(
            request.POST, sqlike=sqlike, instance=filter)

        cards = models.Card.get_allowed_cards(self.me)
        cards = cards.filter(Q(workers__isnull=False))
        total = cards.count()

        if not form.is_valid():
            return render(request, 'card_app/list-all-tasks.html', 
                {'form': form, 'total': total,
                    'count': 0}, status=400)

        form.save()

        cards = filter.get_partial(cards)
        cards = sqlike.run(cards)

        count = cards.count()
        cards = cards.only('done', 'label', 'id').order_by('id')
        elems = JScroll(self.me.id, 'card_app/list-all-tasks-scroll.html', cards)

        return render(request, 'card_app/list-all-tasks.html', 
        {'form': form, 'elems': elems.as_div(), 'total': total, 'count': count})

class Find(GuardianView):
    def get(self, request):
        filter, _ = GlobalCardFilter.objects.get_or_create(
        user=self.me, organization=self.me.default)
        form  = forms.GlobalCardFilterForm(instance=filter)

        cards = models.Card.get_allowed_cards(self.me)
        total = cards.count()

        sqlike = models.Card.from_sqlike()
        sqlike.feed(filter.pattern)

        cards = cards.filter(Q(done=filter.done))
        cards = sqlike.run(cards)
        count = cards.count()

        cards = cards.only('done', 'label', 'id').order_by('id')
        elems = JScroll(self.me.id, 'card_app/find-scroll.html', cards)

        return render(request, 'card_app/find.html', 
        {'form': form, 'elems':  elems.as_div(), 'total': total, 'count': count})

    def post(self, request):
        filter, _ = GlobalCardFilter.objects.get_or_create(
        user=self.me, organization=self.me.default)

        sqlike = models.Card.from_sqlike()
        form  = forms.GlobalCardFilterForm(request.POST, sqlike=sqlike, instance=filter)

        cards = models.Card.get_allowed_cards(self.me)
        total = cards.count()

        if not form.is_valid():
            return render(request, 'card_app/find.html', 
                {'form': form, 'total': total, 'count': 0}, status=400)
        form.save()

        cards  = cards.filter(Q(done=filter.done))
        cards  = sqlike.run(cards)
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
        Q(earchivecard__card__id=card.id) | Q(epastecard__cards=card.id) | \
        Q(ecopycard__card=card.id) | Q(eattachcardfile__card=card.id) |\
        Q(edettachcardfile__card=card.id) | Q(eupdatenote__child=card.id) |\
        Q(ecreatenote__child=card.id) | Q(edeletenote__child=card.id) |\
        Q(eattachnotefile__note__card=card.id) | \
        Q(edettachnotefile__note__card=card.id)|\
        Q(ecreatecardfork__card=card.id)| Q(esetcardpriorityup__card0=card.id)|\
        Q(esetcardprioritydown__card0=card.id)


        events = Event.objects.filter(query).order_by('-created').values('html')
        return render(request, 'card_app/card-events.html', 
        {'card': card, 'elems': events})

class ConnectCard(GuardianView):
    def get(self, request, card_id):
        card  = models.Card.locate(self.me, self.me.default, card_id)
        cards = models.Card.get_allowed_cards(self.me)
        cards = cards.order_by('-priority')
        total = cards.count()

        return render(request, 'card_app/connect-card.html', 
        {'card': card, 'total': total, 'count': total, 'me': self.me,
        'cards': cards, 'form': forms.ConnectCardForm()})

    def post(self, request, card_id):
        sqlike = models.Card.from_sqlike()
        card   = models.Card.locate(self.me, self.me.default, card_id)
        cards = models.Card.get_allowed_cards(self.me)
        total  = cards.count()
        form   = forms.ConnectCardForm(request.POST, sqlike=sqlike)

        if not form.is_valid():
            return render(request, 'card_app/connect-card.html', 
                {'me': self.me, 'organization': self.me.default, 'card': card,
                     'total': total, 'count': 0, 'form':form}, status=400)

        cards = sqlike.run(cards)
        cards = cards.order_by('-priority')

        count = cards.count()

        return render(request, 'card_app/connect-card.html', 
        {'card': card, 'total': total, 'count': count, 'me': self.me,
        'cards': cards, 'form': form})

class ConnectPost(GuardianView):
    def get(self, request, card_id):
        card   = models.Card.locate(self.me, self.me.default, card_id)
        posts = Post.get_allowed_posts(self.me)
        posts = posts.order_by('-priority')
        total = posts.count()

        return render(request, 'card_app/connect-post.html', 
        {'card': card, 'total': total, 'count': total, 'me': self.me,
        'posts': posts, 'form': forms.ConnectPostForm()})

    def post(self, request, card_id):
        sqlike = Post.from_sqlike()
        card   = models.Card.locate(self.me, self.me.default, card_id)
        posts = Post.get_allowed_posts(self.me)

        total  = posts.count()
        form   = forms.ConnectPostForm(request.POST, sqlike=sqlike)

        if not form.is_valid():
            return render(request, 'card_app/connect-post.html', 
                {'me': self.me, 'organization': self.me.default, 'card': card,
                     'total': total, 'count': 0, 'form':form}, status=400)

        posts = sqlike.run(posts)
        posts = posts.order_by('-priority')

        count = posts.count()

        return render(request, 'card_app/connect-post.html', 
        {'card': card, 'total': total, 'count': count, 'me': self.me,
        'posts': posts, 'form': form})

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
        sqlike = models.Card.from_sqlike()
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

class SetCardParent(GuardianView):
    @transaction.atomic
    def get(self, request, card0_id, card1_id):
        card0  = models.Card.locate(self.me, self.me.default, card0_id)
        card1  = models.Card.locate(self.me, self.me.default, card1_id)
        card0.parent = card1
        card0.path.clear()
        card0.path.add(*card1.path.all(), card1)

        # Make sure it is a post fork, otherwise
        # we get a broken concept. A card can have just
        # one parent.
        card0.parent_post = None
        card0.save()

        event = models.ECreateFork.objects.create(organization=self.me.default,
        ancestor=card0.ancestor, card0=card0, card1=card1, user=self.me)
        event.dispatch(*card0.ancestor.ancestor.members.all())

        return redirect('card_app:view-data', card_id=card0.id)

class SetPostFork(GuardianView):
    @transaction.atomic
    def get(self, request, card_id, post_id):
        card  = models.Card.locate(self.me, self.me.default, card_id)
        post  = Post.locate(self.me, self.me.default, post_id)
        card.parent      = None
        card.parent_post = post
        card.path.clear()
        card.save()

        event = ECreateCardFork.objects.create(organization=self.me.default,
        ancestor=post.ancestor, post=post, card=card, user=self.me)

        return redirect('card_app:view-data', card_id=card.id)

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

        event = models.ESetCardPriorityUp.objects.create(organization=self.me.default,
        ancestor=card0.ancestor, card0=card0, card1=card1, user=self.me)
        event.dispatch(*card0.ancestor.ancestor.members.all())
        print('Priority', [[ind.label, ind.priority] for ind in card0.ancestor.cards.all().order_by('-priority')])

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

        event = models.ESetCardPriorityDown.objects.create(organization=self.me.default,
        ancestor=card0.ancestor, card0=card0, card1=card1, user=self.me)
        event.dispatch(*card0.ancestor.ancestor.members.all())
        print('Priority', [[ind.label, ind.priority] for ind in card0.ancestor.cards.all().order_by('-priority')])

        return redirect('card_app:list-cards', list_id=card0.ancestor.id)

class Unpin(GuardianView):
    def get(self, request, pin_id):
        pin = self.me.cardpin_set.get(id=pin_id)
        pin.delete()
        return redirect('board_app:list-pins')



class CardFileDownload(GuardianView):
    def get(self, request, filewrapper_id):
        filewrapper = models.CardFileWrapper.objects.filter(
        Q(card__ancestor__ancestor__members=self.me) | Q(card__workers=self.me),
        id=filewrapper_id, card__ancestor__ancestor__organization=self.me.default)
        filewrapper = filewrapper.distinct().first()
        return redirect(filewrapper.file.url)


