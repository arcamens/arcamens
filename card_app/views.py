from django.shortcuts import render, redirect
from django.db.models import Q, F, Exists, OuterRef
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic import View
from core_app.models import Clipboard
from core_app.views import GuardianView
from core_app.models import User
from functools import reduce
import board_app.models
import list_app.models
from . import models
from . import forms
import operator
import core_app.models
from core_app import ws
from django.conf import settings
import json

# Create your views here.


class Card(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)

        is_worker = card.workers.filter(id=self.user_id).count()
        has_workers = card.workers.count()

        return render(request, 'card_app/card.html', {'card': card,
        'is_worker': is_worker, 'has_workers': has_workers})

class CardLink(GuardianView):
    """
    """

    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)
        on_clipboard = not (card.ancestor and card.ancestor.ancestor)

        if on_clipboard:
            return HttpResponse("This card is on clipboard! \
               It can't be accessed.", status=400)

        user = core_app.models.User.objects.get(id=self.user_id)
        pins = user.pin_set.all()
        forks = card.forks.all()
        workers = card.workers.all()
        attachments = card.filewrapper_set.all()
        tags = card.tags.all()
        snippets = card.snippets.all()
        relations = card.relations.all()

        relations = relations.filter(Q(
        ancestor__ancestor__members__id=self.user_id) | Q(workers__id=self.user_id))


        organizations = user.organizations.exclude(id=user.default.id)

        queues = list(map(lambda ind: 'timeline%s' % ind, 
        user.timelines.values_list('id')))

        queues.extend(map(lambda ind: 'board%s' % ind, 
        user.boards.values_list('id')))

        return render(request, 'card_app/card-link.html', 
        {'card': card, 'forks': forks, 'ancestor': card.ancestor, 
        'attachments': attachments, 'user': user, 'workers': workers, 
        'relations': relations, 'snippets': snippets, 'pins': pins, 'tags': tags,
        'user': user, 'default': user.default, 'organization': user.default,
        'organizations': organizations, 'queues': json.dumps(queues),
         'settings': settings})

class ListCards(GuardianView):
    """
    """

    def get(self, request, list_id):
        list = list_app.models.List.objects.get(id=list_id)

        if not list.ancestor:
            return HttpResponse("This list is on clipboard!\
                It can't be accessed now.", status=400)

        user = core_app.models.User.objects.get(id=self.user_id)
        pins = user.pin_set.filter(organization=user.default)

        filter, _ = models.CardFilter.objects.get_or_create(
        user=user, organization=user.default, list=list)

        cards = list.cards.all()
        total = cards.count()
        
        cards = models.Card.collect_cards(cards, 
        filter.pattern, filter.done) if filter.status else \
        cards.filter(done=False)

        workers1 = User.objects.filter(pk=user.pk, tasks=OuterRef('pk'))
        workers2 = User.objects.filter(tasks=OuterRef('pk'))
        cards = cards.annotate(has_workers=Exists(workers2))
        cards = cards.annotate(in_workers=Exists(workers1))
        cards = cards.values('fork', 'label', 'id', 'has_workers', 'in_workers')
        cards = cards.order_by('-created')

        return render(request, 'card_app/list-cards.html', 
        {'list': list, 'total': total, 'cards': cards, 'filter': filter,
        'pins': pins, 'user': user, 'board': list.ancestor})

class ViewData(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)

        # First check if someone has cut this card.
        # Cards on clipboard shouldnt be accessed due to generating
        # too many inconsistencies.
        on_clipboard = not (card.ancestor and card.ancestor.ancestor)

        if on_clipboard:
            return HttpResponse("This card is on clipboard! \
               It can't be accessed.", status=400)

        user = core_app.models.User.objects.get(id=self.user_id)
        pins = user.pin_set.filter(organization=user.default)
        forks = card.forks.all()
        workers = card.workers.all()
        attachments = card.filewrapper_set.all()
        tags = card.tags.all()
        snippets = card.snippets.all()
        relations = card.relations.all()

        relations = relations.filter(Q(
        ancestor__ancestor__members__id=self.user_id) | Q(workers__id=self.user_id))

        # Maybe it should be retrieved here...
        # but cards dont have path manytomany
        # it may suggest cards should
        # have state of forks too?
        # path = card.path.all()

        return render(request, 'card_app/view-data.html', 
        {'card': card, 'forks': forks, 'ancestor': card.ancestor, 
        'attachments': attachments, 'user': user, 'workers': workers, 
        'relations': relations, 'snippets': snippets, 'pins': pins, 'tags': tags})

class CreateCard(GuardianView):
    """
    """

    def get(self, request, ancestor_id, card_id=None):
        ancestor = list_app.models.List.objects.get(id=ancestor_id)
        user     = core_app.models.User.objects.get(id=self.user_id)
        card     = models.Card.objects.create(owner=user, 
        ancestor=ancestor)
        card.save()

        form = forms.CardForm(instance=card)
        card.label = 'Draft.'
        card.save()
        return render(request, 'card_app/create-card.html', 
        {'form':form, 'card': card, 'ancestor':ancestor})

    def post(self, request, ancestor_id, card_id):
        ancestor = list_app.models.List.objects.get(id=ancestor_id)
        card     = models.Card.objects.get(id=card_id)
        form     = forms.CardForm(request.POST, instance=card)
        user     = core_app.models.User.objects.get(id=self.user_id)

        if not form.is_valid():
            return render(request, 'card_app/create-card.html', 
                {'form': form, 'card':card, 
                    'ancestor': ancestor}, status=400)

        card.save()

        event = models.ECreateCard.objects.create(organization=user.default,
        ancestor=card.ancestor, child=card, user=user)
        event.users.add(*ancestor.ancestor.members.all())

        ws.client.publish('board%s' % card.ancestor.ancestor.id, 
            'sound', 0, False)

        return redirect('card_app:view-data', card_id=card.id)

class CreateFork(GuardianView):
    """
    """

    def get(self, request, card_id, fork_id=None):
        card = models.Card.objects.get(id=card_id)
        user = User.objects.get(id=self.user_id)
        fork = models.Fork.objects.create(owner=user, 
        ancestor=card.ancestor, parent=card)

        form = forms.ForkForm(instance=fork)
        fork.label = 'Draft.'
        fork.save()
        return render(request, 'card_app/create-fork.html', 
        {'form':form, 'card': card, 'fork':fork})

    def post(self, request, card_id, fork_id):
        card = models.Card.objects.get(id=card_id)
        fork = models.Fork.objects.get(id=fork_id)
        form = forms.ForkForm(request.POST, instance=fork)
        user = User.objects.get(id=self.user_id)

        # Its a hack, it means there is something wrong
        # with the models.
        try:
            path = card.fork.path.all()
        except Exception as e:
            path = fork.path.all()
        finally:
            fork.path.add(*path, *(card, ))

        if not form.is_valid():
            return render(request, 'card_app/create-fork.html', 
                {'form':form, 'card': card, 'fork':fork}, status=400)

        fork.save()

        event = models.ECreateFork.objects.create(organization=user.default,
        ancestor=card.ancestor, child0=card, child1=fork, user=user)
        event.users.add(*card.ancestor.ancestor.members.all())

        ws.client.publish('board%s' % card.ancestor.ancestor.id, 
            'sound', 0, False)

        return redirect('card_app:view-data', card_id=fork.id)

class CancelCardCreation(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id = card_id)
        card.delete()

        return HttpResponse(status=200)

class DeleteCard(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id = card_id)

        user = core_app.models.User.objects.get(id=self.user_id)
        event = models.EDeleteCard.objects.create(organization=user.default,
        ancestor=card.ancestor, label=card.label, user=user)
        event.users.add(*card.ancestor.ancestor.members.all())
        card.delete()

        ws.client.publish('board%s' % card.ancestor.ancestor.id, 
            'sound', 0, False)

        return redirect('card_app:list-cards', 
        list_id=card.ancestor.id)

class CutCard(GuardianView):
    def get(self, request, card_id):
        card          = models.Card.objects.get(id=card_id)
        user          = core_app.models.User.objects.get(id=self.user_id)
        list          = card.ancestor

        # Missing event.
        ws.client.publish('board%s' % card.ancestor.ancestor.id, 
            'sound', 0, False)

        card.ancestor = None
        card.save()

        clipboard, _    = Clipboard.objects.get_or_create(
        user=user, organization=user.default)
        clipboard.cards.add(card)

        event = models.ECutCard.objects.create(organization=user.default,
        ancestor=list, child=card, user=user)
        event.users.add(*list.ancestor.members.all())

        return redirect('card_app:list-cards', 
        list_id=list.id)

class CopyCard(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)
        user = core_app.models.User.objects.get(id=self.user_id)
        copy = card.duplicate()

        clipboard, _    = Clipboard.objects.get_or_create(
        user=user, organization=user.default)
        clipboard.cards.add(copy)

        # Missing event.
        ws.client.publish('board%s' % card.ancestor.ancestor.id, 
            'sound', 0, False)

        return redirect('card_app:list-cards', 
        list_id=card.ancestor.id)

class AttachImage(GuardianView):
    """
    """

    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)
        attachments = card.imagewrapper_set.all()
        form = forms.ImageWrapperForm()
        return render(request, 'card_app/attach-image.html', 
        {'card':card, 'form': form, 'attachments': attachments})

    def post(self, request, card_id):
        card = models.Card.objects.get(id=card_id)
        attachments = card.imagewrapper_set.all()
        form = forms.ImageWrapperForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, 'card_app/attach-image.html', 
                {'card':card, 'form': form, 'attachments': attachments})

        record = form.save(commit = False)
        record.card = card
        form.save()
        return self.get(request, card_id)


class AttachFile(GuardianView):
    """
    """

    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)
        attachments = card.filewrapper_set.all()
        form = forms.FileWrapperForm()
        return render(request, 'card_app/attach-file.html', 
        {'card':card, 'form': form, 'attachments': attachments})

    def post(self, request, card_id):
        card = models.Card.objects.get(id=card_id)
        attachments = card.filewrapper_set.all()
        form = forms.FileWrapperForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, 'card_app/attach-file.html', 
                {'card':card, 'form': form, 'attachments': attachments})
        record = form.save(commit = False)
        record.card = card
        form.save()
        return self.get(request, card_id)

class DetachFile(GuardianView):
    """
    """

    def get(self, request, filewrapper_id):
        filewrapper = models.FileWrapper.objects.get(id=filewrapper_id)
        filewrapper.delete()
        attachments = filewrapper.card.filewrapper_set.all()

        form = forms.FileWrapperForm()
        return render(request, 'card_app/attach-file.html', 
        {'card':filewrapper.card, 'form': form, 'attachments': attachments})

class UpdateCard(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)
        return render(request, 'card_app/update-card.html',
        {'card': card, 'form': forms.CardForm(instance=card),})

    def post(self, request, card_id):
        record  = models.Card.objects.get(id=card_id)
        form    = forms.CardForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'card_app/update-card.html',
                        {'form': form, 'card':record, }, status=400)

        record.save()

        user  = core_app.models.User.objects.get(id=self.user_id)
        event = models.EUpdateCard.objects.create(
        organization=user.default, ancestor=record.ancestor, 
        child=record, user=user)
        event.users.add(*record.ancestor.ancestor.members.all())
        event.save()

        ws.client.publish('board%s' % record.ancestor.ancestor.id, 
            'sound', 0, False)

        return redirect('card_app:view-data', 
        card_id=record.id)

class EBindCardWorker(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.EBindCardWorker.objects.get(id=event_id)
        return render(request, 'card_app/e-bind-card-worker.html', 
        {'event':event})

class EUnbindCardWorker(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.EUnbindCardWorker.objects.get(id=event_id)
        return render(request, 'card_app/e-unbind-card-worker.html', 
        {'event':event})

class ECreateCard(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.ECreateCard.objects.get(id=event_id)
        return render(request, 'card_app/e-create-card.html', 
        {'event':event})

class ECreateFork(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.ECreateFork.objects.get(id=event_id)
        return render(request, 'card_app/e-create-fork.html', 
        {'event':event})

class ERelateCard(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.ERelateCard.objects.get(id=event_id)
        return render(request, 'card_app/e-relate-card.html', 
        {'event':event})

class EUnrelateCard(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.EUnrelateCard.objects.get(id=event_id)
        return render(request, 'card_app/e-unrelate-card.html', 
        {'event':event})

class EUpdateCard(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.EUpdateCard.objects.get(id=event_id)
        return render(request, 'card_app/e-update-card.html', 
        {'event':event})


class EDeleteCard(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.EDeleteCard.objects.get(id=event_id)
        return render(request, 'card_app/e-delete-card.html', 
        {'event':event})

class ECutCard(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.ECutCard.objects.get(id=event_id)
        return render(request, 'card_app/e-cut-card.html', 
        {'event':event})

class EArchiveCard(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.EArchiveCard.objects.get(id=event_id)
        return render(request, 'card_app/e-archive-card.html', 
        {'event':event})

class SetupCardFilter(GuardianView):
    def get(self, request, list_id):
        user = core_app.models.User.objects.get(id=self.user_id)
        list = list_app.models.List.objects.get(id=list_id)

        filter = models.CardFilter.objects.get(
        user__id=self.user_id, organization__id=user.default.id,
        list__id=list_id)

        return render(request, 'card_app/setup-card-filter.html', 
        {'form': forms.CardFilterForm(instance=filter), 
        'list': filter.list})

    def post(self, request, list_id):
        user = core_app.models.User.objects.get(id=self.user_id)

        filter = models.CardFilter.objects.get(
        user__id=self.user_id, organization__id=user.default.id,
        list__id=list_id)

        form   = forms.CardFilterForm(request.POST, instance=filter)

        if not form.is_valid():
            return render(request, 'card_app/setup-filter.html',
                   {'card': record, 'form': form, 
                        'list': record.list}, status=400)
        form.save()
        return redirect('card_app:list-cards', list_id=list_id)


class ListTasks(GuardianView):
    def get(self, request):
        user = core_app.models.User.objects.get(id=self.user_id)

        return render(request, 'card_app/list-tasks.html', 
        {'tasks': user.tasks.all()})

class PinCard(GuardianView):
    def get(self, request, card_id):
        user = core_app.models.User.objects.get(id=self.user_id)
        card = models.Card.objects.get(id=card_id)
        pin  = board_app.models.Pin.objects.create(user=user, 
        organization=user.default, card=card)
        return redirect('board_app:list-pins')

class UnrelateCard(GuardianView):
    def get(self, request, card0_id, card1_id):
        user = User.objects.get(id=self.user_id)

        card0 = models.Card.objects.get(id=card0_id)
        card1 = models.Card.objects.get(id=card1_id)
        card0.relations.remove(card1)
        card0.save()

        event = models.EUnrelateCard.objects.create(
        organization=user.default, ancestor0=card0.ancestor, 
        ancestor1=card1.ancestor, child0=card0, 
        child1=card1, user=user)

        event.users.add(*card0.ancestor.ancestor.members.all())
        event.users.add(*card1.ancestor.ancestor.members.all())

        ws.client.publish('board%s' % 
        card0.ancestor.ancestor.id, 'sound', False)

        ws.client.publish('board%s' % 
        card1.ancestor.ancestor.id, 'sound', False)

        return HttpResponse(status=200)

class RelateCard(GuardianView):
    def get(self, request, card0_id, card1_id):
        user = User.objects.get(id=self.user_id)

        card0 = models.Card.objects.get(id=card0_id)
        card1 = models.Card.objects.get(id=card1_id)
        card0.relations.add(card1)
        card0.save()

        event = models.ERelateCard.objects.create(
        organization=user.default, ancestor0=card0.ancestor, 
        ancestor1=card1.ancestor, child0=card0, child1=card1, user=user)

        event.users.add(*card0.ancestor.ancestor.members.all())
        event.users.add(*card1.ancestor.ancestor.members.all())

        ws.client.publish('board%s' % 
        card0.ancestor.ancestor.id, 'sound', False)
        ws.client.publish('board%s' % 
        card1.ancestor.ancestor.id, 'sound', False)

        return HttpResponse(status=200)

class ManageCardRelations(GuardianView):
    def get(self, request, card_id):
        me = User.objects.get(id=self.user_id)
        card = models.Card.objects.get(id=card_id)

        included = card.relations.filter(done=False)

        cards = models.Card.get_allowed_cards(me)
        cards = cards.filter(done=False)

        excluded = cards.exclude(pk__in=included)

        return render(request, 'card_app/manage-card-relations.html', 
        {'included': included, 'excluded': excluded, 'card': card,
        'me': me, 'organization': me.default,'form':forms.CardSearchForm()})

    def post(self, request, card_id):
        form = forms.CardSearchForm(request.POST)
        me = User.objects.get(id=self.user_id)
        card = models.Card.objects.get(id=card_id)

        if not form.is_valid():
            return render(request, 'card_app/manage-card-relations.html', 
                {'me': me, 'organization': me.default, 'card': card,
                        'form':form}, status=400)

        included = card.relations.all()
        cards = models.Card.get_allowed_cards(me)
        excluded = cards.exclude(pk__in=included)

        included = models.Card.collect_cards(included, 
        form.cleaned_data['pattern'], form.cleaned_data['done']) 

        excluded = models.Card.collect_cards(excluded, 
        form.cleaned_data['pattern'], form.cleaned_data['done']) 

        return render(request, 'card_app/manage-card-relations.html', 
        {'included': included, 'excluded': excluded, 'card': card,
        'me': me, 'organization': me.default,'form':form})


class ManageCardWorkers(GuardianView):
    def get(self, request, card_id):
        me = User.objects.get(id=self.user_id)
        card = models.Card.objects.get(id=card_id)

        included = card.workers.all()
        excluded = me.default.users.exclude(tasks=card)
        total = included.count() + excluded.count()
        
        return render(request, 'card_app/manage-card-workers.html', 
        {'included': included, 'excluded': excluded, 'card': card,
        'me': me, 'organization': me.default, 'total': total, 
        'count': total, 'form':forms.UserSearchForm()})

    def post(self, request, card_id):
        form = forms.UserSearchForm(request.POST)

        me = User.objects.get(id=self.user_id)
        card = models.Card.objects.get(id=card_id)
        included = card.workers.all()
        excluded = me.default.users.exclude(tasks=card)
        total = included.count() + excluded.count()

        if not form.is_valid():
            return render(request, 'card_app/manage-card-workers.html', 
                {'included': included, 'excluded': excluded,
                    'me': me, 'organization': me.default, 'card': card,
                        'form':forms.UserSearchForm(), 'total': total,
                            'count': total,}, status=400)

        included = included.filter(
        name__contains=form.cleaned_data['pattern'])

        excluded = excluded.filter(
        name__contains=form.cleaned_data['pattern'])

        count = included.count() + excluded.count()

        return render(request, 'card_app/manage-card-workers.html', 
        {'included': included, 'excluded': excluded, 'card': card, 'total': total,
        'count': count, 'me': me, 'organization': me.default,
        'form':forms.UserSearchForm()})

class UnbindCardWorker(GuardianView):
    def get(self, request, card_id, user_id):
        user = User.objects.get(id=user_id)
        card = models.Card.objects.get(id=card_id)
        card.workers.remove(user)
        card.save()

        me = User.objects.get(id=self.user_id)
        event = models.EUnbindCardWorker.objects.create(
        organization=me.default, ancestor=card.ancestor, 
        child=card, user=me, peer=user)
        event.users.add(*card.ancestor.ancestor.members.all())
        event.save()

        ws.client.publish('board%s' % 
        card.ancestor.ancestor.id, 'sound', 0, False)

        return HttpResponse(status=200)

class BindCardWorker(GuardianView):
    def get(self, request, card_id, user_id):
        user = User.objects.get(id=user_id)
        card = models.Card.objects.get(id=card_id)
        card.workers.add(user)
        card.save()

        me = User.objects.get(id=self.user_id)
        event = models.EBindCardWorker.objects.create(
        organization=me.default, ancestor=card.ancestor, 
        child=card, user=me, peer=user)
        event.users.add(*card.ancestor.ancestor.members.all())
        event.save()

        ws.client.publish('board%s' % 
        card.ancestor.ancestor.id, 'sound', 0, False)

        return HttpResponse(status=200)

class ManageCardTags(GuardianView):
    def get(self, request, card_id):
        me = User.objects.get(id=self.user_id)
        card = models.Card.objects.get(id=card_id)

        included = card.tags.all()
        excluded = me.default.tags.exclude(cards=card)
        total = included.count() + excluded.count()

        return render(request, 'card_app/manage-card-tags.html', 
        {'included': included, 'excluded': excluded, 'card': card,
        'organization': me.default,'form':forms.TagSearchForm(),
        'total': total, 'count': total})

    def post(self, request, card_id):
        form = forms.TagSearchForm(request.POST)

        me = User.objects.get(id=self.user_id)
        card = models.Card.objects.get(id=card_id)
        included = card.tags.all()
        excluded = me.default.tags.exclude(cards=card)
        total = included.count() + excluded.count()

        if not form.is_valid():
            return render(request, 'card_app/manage-card-tags.html', 
                {'included': included, 'excluded': excluded,
                    'organization': me.default, 'card': card, 'total': total,
                        'count': total, 'form':form}, status=400)

        included = included.filter(
        name__contains=form.cleaned_data['name'])

        excluded = excluded.filter(
        name__contains=form.cleaned_data['name'])

        count = included.count() + excluded.count()

        return render(request, 'card_app/manage-card-tags.html', 
        {'included': included, 'excluded': excluded, 'card': card,
        'me': me, 'organization': me.default,
        'total': total, 'count': count, 'form':form})

class UnbindCardTag(GuardianView):
    def get(self, request, card_id, tag_id):
        tag = core_app.models.Tag.objects.get(id=tag_id)
        card = models.Card.objects.get(id=card_id)
        card.tags.remove(tag)
        card.save()

        # me = User.objects.get(id=self.user_id)

        # event = models.EUnbindCardTag.objects.create(
        # organization=me.default, ancestor=card.ancestor, 
        # card=card, user=me, peer=user)
        # event.users.add(*card.ancestor.users.all())
        # event.save()
        me = User.objects.get(id=self.user_id)
        event = models.EUnbindTagCard.objects.create(
        organization=me.default, ancestor=card.ancestor, 
        card=card, tag=tag, user=me)
        event.users.add(*card.ancestor.ancestor.members.all())
        event.save()

        ws.client.publish('board%s' % card.ancestor.ancestor.id, 
            'sound', 0, False)

        return HttpResponse(status=200)

class BindCardTag(GuardianView):
    def get(self, request, card_id, tag_id):
        tag = core_app.models.Tag.objects.get(id=tag_id)
        card = models.Card.objects.get(id=card_id)
        card.tags.add(tag)
        card.save()

        # me = User.objects.get(id=self.user_id)

        # event = models.EUnbindCardTag.objects.create(
        # organization=me.default, ancestor=card.ancestor, 
        # card=card, tag=me, peer=tag)
        # event.tags.add(*card.ancestor.tags.all())
        # event.save()
        me = User.objects.get(id=self.user_id)

        event = models.EBindTagCard.objects.create(
        organization=me.default, ancestor=card.ancestor, 
        card=card, tag=tag, user=me)
        event.users.add(*card.ancestor.ancestor.members.all())
        event.save()

        ws.client.publish('board%s' % card.ancestor.ancestor.id, 
            'sound', 0, False)

        return HttpResponse(status=200)


class EBindTagCard(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.EBindTagCard.objects.get(id=event_id)
        return render(request, 'card_app/e-bind-tag-card.html', 
        {'event':event})

class EUnbindTagCard(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.EUnbindTagCard.objects.get(id=event_id)
        return render(request, 'card_app/e-unbind-tag-card.html', 
        {'event':event})


class Done(GuardianView):
    def get(self, request, card_id):
        card      = models.Card.objects.get(id=card_id)
        card.done = True
        card.save()

        user = core_app.models.User.objects.get(id=self.user_id)

        # cards in the clipboard cant be archived.
        event    = models.EArchiveCard.objects.create(organization=user.default,
        ancestor=card.ancestor, child=card, user=user)

        users = card.ancestor.ancestor.members.all()
        event.users.add(*users)

        # Missing event.
        ws.client.publish('board%s' % 
        card.ancestor.ancestor.id, 'sound', 0, False)

        return redirect('card_app:view-data', card_id=card.id)

class Undo(GuardianView):
    def get(self, request, card_id):
        card      = models.Card.objects.get(id=card_id)
        card.done = False
        card.save()

        user = core_app.models.User.objects.get(id=self.user_id)

        # cards in the clipboard cant be archived.
        # event    = models.EArchiveCard.objects.create(organization=user.default,
        # ancestor=card.ancestor, child=card, user=user)

        # users = card.ancestor.ancestor.members.all()
        # event.users.add(*users)

        # Missing event.
        ws.client.publish('board%s' % 
        card.ancestor.ancestor.id, 'sound', 0, False)

        return redirect('card_app:view-data', card_id=card.id)

class CardWorkerInformation(GuardianView):
    def get(self, request, peer_id, card_id):
        event = models.EBindCardWorker.objects.filter(child__id=card_id,
        peer__id=peer_id).last()

        return render(request, 'card_app/card-worker-information.html', 
        {'peer': event.peer, 'created': event.created, 'user':event.user})

class CardTagInformation(GuardianView):
    def get(self, request, tag_id, card_id):
        event = models.EBindTagCard.objects.filter(card__id=card_id,
        tag__id=tag_id).last()

        return render(request, 'post_app/post-tag-information.html', 
        {'user': event.user, 'created': event.created, 'tag':event.tag})


class PreviewCard(GuardianView):
    def get(self, request, card_id):
        pass


























