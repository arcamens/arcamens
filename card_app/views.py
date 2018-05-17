from django.shortcuts import render, redirect
from django.db.models.functions import Concat
from django.db.models import Q, Exists, OuterRef, Count
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from card_app.models import GlobalTaskFilter, GlobalCardFilter, CardPin
from core_app.models import Clipboard, Event, Tag
from django.core.mail import send_mail
from core_app.views import GuardianView
from post_app.models import Post
from post_app.forms import PostForm
from timeline_app.models import Timeline
from core_app.models import User
from list_app.models import List, EPasteCard
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

        if not card.ancestor:
            return HttpResponse("This card is on clipboard! \
               It can't be accessed.", status=403)

        if not card.ancestor.ancestor:
            return HttpResponse("The card list is on clipboard!", status=403)

        user = core_app.models.User.objects.get(id=self.user_id)
        boardpins = user.boardpin_set.filter(organization=user.default)
        listpins = user.listpin_set.filter(organization=user.default)
        cardpins = user.cardpin_set.filter(organization=user.default)
        timelinepins = user.timelinepin_set.filter(organization=user.default)

        forks = card.forks.all()
        workers = card.workers.all()
        attachments = card.cardfilewrapper_set.all()
        tags = card.tags.all()
        # snippets = card.snippets.all()
        relations = card.relations.all()
        path = card.path.all()

        relations = relations.filter(Q(
        ancestor__ancestor__members__id=self.user_id) | Q(workers__id=self.user_id))

        organizations = user.organizations.exclude(id=user.default.id)

        return render(request, 'card_app/card-link.html', 
        {'card': card, 'forks': forks, 'ancestor': card.ancestor, 
        'attachments': attachments, 'user': user, 'workers': workers, 'path': path,
        'relations': relations, 'tags': tags, 'boardpins': boardpins,
        'listpins': listpins, 'cardpins': cardpins, 'timelinepins': timelinepins,
        'user': user, 'default': user.default, 'organization': user.default,
        'organizations': organizations, 'settings': settings})

class ListCards(GuardianView):
    """
    """

    def get(self, request, list_id):
        list = list_app.models.List.objects.get(id=list_id)

        if not list.ancestor:
            return HttpResponse("This list is on clipboard!\
                It can't be accessed now.", status=403)

        user = core_app.models.User.objects.get(id=self.user_id)
        boardpins = user.boardpin_set.filter(organization=user.default)
        listpins = user.listpin_set.filter(organization=user.default)
        cardpins = user.cardpin_set.filter(organization=user.default)
        timelinepins = user.timelinepin_set.filter(organization=user.default)

        filter, _ = models.CardFilter.objects.get_or_create(
        user=user, organization=user.default, list=list)

        cards = list.cards.all()

        total = cards.count()

        cards = filter.collect(cards)
        count = cards.count()

        workers1 = User.objects.filter(pk=user.pk, tasks=OuterRef('pk'))
        cards = cards.annotate(in_workers=Exists(workers1))
        cards = cards.annotate(has_workers=Count('workers'))

        cards = cards.values('parent', 'label', 'id', 
        'owner__name', 'created', 'in_workers', 'has_workers')

        cards = cards.order_by('-created')

        return render(request, 'card_app/list-cards.html', 
        {'list': list, 'total': total, 'cards': cards, 'filter': filter,
        'boardpins': boardpins, 'listpins':listpins, 'cardpins': cardpins, 'timelinepins': timelinepins,
        'user': user, 'board': list.ancestor, 'count': count})

class ViewData(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)

        if not card.ancestor:
            return HttpResponse("This card is on clipboard! \
               It can't be accessed.", status=403)

        if not card.ancestor.ancestor:
            return HttpResponse("The card list is on clipboard!", status=403)

        user = core_app.models.User.objects.get(id=self.user_id)
        boardpins = user.boardpin_set.filter(organization=user.default)
        listpins = user.listpin_set.filter(organization=user.default)
        cardpins = user.cardpin_set.filter(organization=user.default)
        timelinepins = user.timelinepin_set.filter(organization=user.default)

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
        'attachments': attachments, 'user': user, 'workers': workers,  'timelinepins': timelinepins,
        'relations': relations, 'listpins': listpins, 'boardpins': boardpins,
        'cardpins': cardpins, 'tags': tags})

class ConfirmCardDeletion(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)
        return render(request, 'card_app/confirm-card-deletion.html', 
        {'card': card})

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
        ancestor=card.ancestor, card=card, user=user)
        event.dispatch(*ancestor.ancestor.members.all())

        return redirect('card_app:view-data', card_id=card.id)

class SelectForkList(GuardianView):
    def get(self, request, card_id):
        user   = User.objects.get(id=self.user_id)
        card   = models.Card.objects.get(id=card_id)
        form   = forms.ListSearchform()
        boards = user.boards.filter(organization=user.default)
        lists  = List.objects.filter(ancestor__in=boards)

        return render(request, 'card_app/select-fork-list.html', 
        {'form':form, 'card': card, 'elems': lists})

    def post(self, request, card_id):
        form = forms.ListSearchform(request.POST)
        card = models.Card.objects.get(id=card_id)

        user  = User.objects.get(id=self.user_id)
        lists = List.objects.filter(ancestor__in=user.boards.all())

        if not form.is_valid():
            return render(request, 'card_app/select-fork-list.html', 
                  {'form':form, 'elems': lists, 'card': card})

        lists = lists.annotate(text=Concat('ancestor__name', 'name'))

        # Not sure if its the fastest way to do it.
        chks  = split(' *\++ *', form.cleaned_data['pattern'])

        lists = lists.filter(reduce(operator.and_, 
        (Q(text__contains=ind) for ind in chks))) 

        return render(request, 'card_app/select-fork-list.html', 
        {'form':form, 'card': card, 'elems': lists})

class SelectForkTimeline(GuardianView):
    def get(self, request, card_id):
        user = User.objects.get(id=self.user_id)
        card = models.Card.objects.get(id=card_id)
        form = forms.TimelineSearchform()
        timelines = Timeline.get_user_timelines(user)

        return render(request, 'card_app/select-fork-timeline.html', 
        {'form':form, 'card': card, 'elems': timelines})

    def post(self, request, card_id):
        form = forms.TimelineSearchform(request.POST)
        card = models.Card.objects.get(id=card_id)

        user  = User.objects.get(id=self.user_id)
        timelines = Timeline.get_user_timelines(user)

        if not form.is_valid():
            return render(request, 'card_app/select-fork-timeline.html', 
                  {'form':form, 'elems': timelines, 'card': card})

        timelines = timelines.annotate(text=Concat('name', 'description'))

        # Not sure if its the fastest way to do it.
        chks     = split(' *\++ *', form.cleaned_data['pattern'])

        timelines = timelines.filter(reduce(operator.and_, 
        (Q(text__contains=ind) for ind in chks))) 

        return render(request, 'card_app/select-fork-timeline.html', 
        {'form':form, 'card': card, 'elems': timelines})

class PullCardContent(GuardianView):
    """
    """

    def get(self, request, card_id, fork_id=None):
        card       = models.Card.objects.get(id=card_id)
        user       = User.objects.get(id=self.user_id)
        fork       = models.Card.objects.get(id=fork_id)

        fork.label = card.label
        fork.data  = card.data
        form       = forms.CardForm(instance=fork)

        return render(request, 'card_app/create-fork.html', 
        {'form':form, 'card': card, 'ancestor': fork.ancestor, 'fork':fork})

class CreateFork(GuardianView):
    """
    """

    def get(self, request, ancestor_id, card_id, fork_id=None):
        card = models.Card.objects.get(id=card_id)

        if not card.ancestor:
            return HttpResponse("On clipboard! \
                Can't fork now", status=403)

        if not card.ancestor.ancestor:
            return HttpResponse("The card's list is on \
                clipboard! Can't fork now.", status=403)

        user = User.objects.get(id=self.user_id)
        ancestor = List.objects.get(id=ancestor_id)
        fork = models.Card.objects.create(owner=user, 
        ancestor=ancestor, parent=card)

        form = forms.CardForm(instance=fork)
        fork.label = 'Draft.'

        path = card.path.all()
        fork.parent = card
        fork.path.add(*path, card)
        fork.save()

        return render(request, 'card_app/create-fork.html', 
        {'form':form, 'card': card, 'ancestor': ancestor, 'fork':fork})

    def post(self, request, ancestor_id, card_id, fork_id):
        card = models.Card.objects.get(id=card_id)
        fork = models.Card.objects.get(id=fork_id)
        form = forms.CardForm(request.POST, instance=fork)
        user = User.objects.get(id=self.user_id)

        if not form.is_valid():
            return render(request, 'card_app/create-fork.html', 
                {'form':form, 'ancestor': card.ancestor, 
                    'card': card, 'fork':fork}, status=400)

        fork.save()

        event = models.ECreateFork.objects.create(organization=user.default,
        ancestor=card.ancestor, card0=card, card1=fork, user=user)
        event.dispatch(*card.ancestor.ancestor.members.all())

        return redirect('card_app:view-data', card_id=fork.id)

class PullPostContent(GuardianView):
    """
    """

    def get(self, request, card_id, fork_id=None):
        card       = models.Card.objects.get(id=card_id)
        user       = User.objects.get(id=self.user_id)
        fork       = Post.objects.get(id=fork_id)

        fork.label = card.label
        fork.data  = card.data
        form       = PostForm(instance=fork)

        return render(request, 'card_app/create-post-fork.html', 
        {'form':form, 'post': fork, 'ancestor': fork.ancestor, 'card': card})

class CreatePostFork(GuardianView):
    """
    """

    def get(self, request, ancestor_id, card_id, fork_id=None):
        card = models.Card.objects.get(id=card_id)

        if not card.ancestor:
            return HttpResponse("This card is on clipboard! \
               Can't fork now.", status=403)

        if not card.ancestor.ancestor:
            return HttpResponse("The card list is on clipboard! \
                Can't fork now.", status=403)

        user = User.objects.get(id=self.user_id)
        ancestor = Timeline.objects.get(id=ancestor_id)
        fork = Post.objects.create(user=user, 
        ancestor=ancestor, parent=card)

        form = PostForm(instance=fork)
        fork.label = 'Draft.'

        # path = card.path.all()
        fork.parent = card
        # fork.path.add(*path, card)
        fork.save()

        return render(request, 'card_app/create-post-fork.html', 
        {'form':form, 'post': fork, 'ancestor': ancestor, 'card': card})

    def post(self, request, ancestor_id, card_id, fork_id):
        card = models.Card.objects.get(id=card_id)
        fork = Post.objects.get(id=fork_id)
        form = PostForm(request.POST, instance=fork)

        user = User.objects.get(id=self.user_id)

        if not form.is_valid():
            return render(request, 'card_app/create-post-fork.html', 
                {'form':form, 'ancestor': card.ancestor, 
                    'card': card, 'post': fork}, status=400)

        fork.save()

        event = models.ECreatePostFork.objects.create(organization=user.default,
        list=card.ancestor, timeline=fork.ancestor, card=card, post=fork, user=user)
        event.dispatch(*fork.ancestor.users.all())
        event.dispatch(*card.ancestor.ancestor.members.all())

        # user.ws_sound(card.ancestor.ancestor)
        # user.ws_sound(fork.ancestor)

        return redirect('timeline_app:list-posts', timeline_id=ancestor_id)

class CancelCardCreation(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id = card_id)
        card.delete()

        return HttpResponse(status=200)

class DeleteCard(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id = card_id)

        if not card.ancestor:
            return HttpResponse("On clipboard ! \
                Can't delete now", status=403)

        if not card.ancestor.ancestor:
            return HttpResponse("The card's list is on clipboard!\
                Can't delete now.", status=403)

        user = core_app.models.User.objects.get(id=self.user_id)
        event = models.EDeleteCard.objects.create(organization=user.default,
        ancestor=card.ancestor, label=card.label, user=user)
        event.dispatch(*card.ancestor.ancestor.members.all())
        card.delete()

        # user.ws_sound(card.ancestor.ancestor)

        return redirect('card_app:list-cards', 
        list_id=card.ancestor.id)

class CutCard(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)

        if not card.ancestor:
            return HttpResponse("On clipboard ! \
                Can't cut now", status=403)

        if not card.ancestor.ancestor:
            return HttpResponse("The card's list is on clipboard!\
                Can't cut now.", status=403)

        user = core_app.models.User.objects.get(id=self.user_id)
        list = card.ancestor

        # Missing event.
        # user.ws_sound(card.ancestor.ancestor)

        card.ancestor = None
        card.save()

        clipboard, _    = Clipboard.objects.get_or_create(
        user=user, organization=user.default)
        clipboard.cards.add(card)

        event = models.ECutCard.objects.create(organization=user.default,
        ancestor=list, card=card, user=user)
        event.dispatch(*list.ancestor.members.all())

        return redirect('card_app:list-cards', 
        list_id=list.id)

class CopyCard(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)

        if not card.ancestor:
            return HttpResponse("On clipboard ! \
                Can't copy now", status=403)

        if not card.ancestor.ancestor:
            return HttpResponse("The card's list is on clipboard!\
                Can't copy now.", status=403)

        user = core_app.models.User.objects.get(id=self.user_id)
        copy = card.duplicate()

        clipboard, _    = Clipboard.objects.get_or_create(
        user=user, organization=user.default)
        clipboard.cards.add(copy)

        event = models.ECopyCard.objects.create(organization=user.default,
        ancestor=card.ancestor, card=card, user=user)
        event.dispatch(*card.ancestor.ancestor.members.all())

        # Missing event.
        # user.ws_sound(card.ancestor.ancestor)

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
        attachments = card.cardfilewrapper_set.all()
        form = forms.CardFileWrapperForm()
        return render(request, 'card_app/attach-file.html', 
        {'card':card, 'form': form, 'attachments': attachments})

    def post(self, request, card_id):
        card = models.Card.objects.get(id=card_id)

        if not card.ancestor:
            return HttpResponse("On clipboard ! \
                Can't update now", status=403)

        if not card.ancestor.ancestor:
            return HttpResponse("The card's list is on clipboard!\
                Can't update now.", status=403)

        attachments = card.cardfilewrapper_set.all()
        form = forms.CardFileWrapperForm(request.POST, request.FILES)

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
        filewrapper = models.CardFileWrapper.objects.get(id=filewrapper_id)

        if not filewrapper.card.ancestor:
            return HttpResponse("On clipboard ! \
                Can't update now", status=403)

        if not filewrapper.card.ancestor.ancestor:
            return HttpResponse("The card's list is on clipboard!\
                Can't update now.", status=403)

        filewrapper.delete()
        attachments = filewrapper.card.cardfilewrapper_set.all()

        form = forms.CardFileWrapperForm()
        return render(request, 'card_app/attach-file.html', 
        {'card':filewrapper.card, 'form': form, 'attachments': attachments})

class UpdateCard(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)
        return render(request, 'card_app/update-card.html',
        {'card': card, 'form': forms.CardForm(instance=card),})

    def post(self, request, card_id):
        record  = models.Card.objects.get(id=card_id)

        if not record.ancestor:
            return HttpResponse("On clipboard ! \
                Can't update now", status=403)

        if not record.ancestor.ancestor:
            return HttpResponse("The card's list is on clipboard!\
                Can't update now.", status=403)

        form    = forms.CardForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'card_app/update-card.html',
                        {'form': form, 'card':record, }, status=400)

        record.save()

        user  = core_app.models.User.objects.get(id=self.user_id)
        event = models.EUpdateCard.objects.create(
        organization=user.default, ancestor=record.ancestor, 
        card=record, user=user)
        event.dispatch(*record.ancestor.ancestor.members.all())
        event.save()

        # user.ws_sound(record.ancestor.ancestor)

        return redirect('card_app:view-data', 
        card_id=record.id)

class SetupCardFilter(GuardianView):
    def get(self, request, list_id):
        user   = core_app.models.User.objects.get(id=self.user_id)

        filter = models.CardFilter.objects.get(user__id=self.user_id, 
        organization__id=user.default.id, list__id=list_id)

        return render(request, 'card_app/setup-card-filter.html', 
        {'form': forms.CardFilterForm(instance=filter), 
        'list': filter.list})

    def post(self, request, list_id):
        user = core_app.models.User.objects.get(id=self.user_id)

        filter = models.CardFilter.objects.get(user__id=self.user_id, 
        organization__id=user.default.id, list__id=list_id)
        list   = list_app.models.List.objects.get(id=list_id)

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
        user = core_app.models.User.objects.get(id=self.user_id)
        card = models.Card.objects.get(id=card_id)

        pin  = CardPin.objects.create(user=user, 
        organization=user.default, card=card)

        return redirect('board_app:list-pins')

class UnrelateCard(GuardianView):
    def get(self, request, card0_id, card1_id):
        user = User.objects.get(id=self.user_id)

        card0 = models.Card.objects.get(id=card0_id)
        card1 = models.Card.objects.get(id=card1_id)

        if not card0.ancestor or not card1.ancestor:
            return HttpResponse("On clipboard ! \
                Can't unrelate now", status=403)

        if not card0.ancestor.ancestor or not card1.ancestor.ancestor:
            return HttpResponse("The card's list is on clipboard!\
                Can't unrelate now.", status=403)

        card0.relations.remove(card1)
        card0.save()

        event = models.EUnrelateCard.objects.create(
        organization=user.default, ancestor0=card0.ancestor, 
        ancestor1=card1.ancestor, card0=card0, 
        card1=card1, user=user)

        event.dispatch(*card0.ancestor.ancestor.members.all())
        event.dispatch(*card1.ancestor.ancestor.members.all())

        # user.ws_sound(card0.ancestor.ancestor)
        # user.ws_sound(card1.ancestor.ancestor)

        return HttpResponse(status=200)

class RelateCard(GuardianView):
    def get(self, request, card0_id, card1_id):
        user = User.objects.get(id=self.user_id)

        card0 = models.Card.objects.get(id=card0_id)
        card1 = models.Card.objects.get(id=card1_id)

        if not card0.ancestor or not card1.ancestor:
            return HttpResponse("On clipboard ! \
                Can't relate now", status=403)

        if not card0.ancestor.ancestor or not card1.ancestor.ancestor:
            return HttpResponse("The card's list is on clipboard!\
                Can't relate now.", status=403)

        card0.relations.add(card1)
        card0.save()

        event = models.ERelateCard.objects.create(
        organization=user.default, ancestor0=card0.ancestor, 
        ancestor1=card1.ancestor, card0=card0, card1=card1, user=user)

        event.dispatch(*card0.ancestor.ancestor.members.all())
        event.dispatch(*card1.ancestor.ancestor.members.all())

        # user.ws_sound(card0.ancestor.ancestor)
        # user.ws_sound(card1.ancestor.ancestor)

        return HttpResponse(status=200)

class ManageCardRelations(GuardianView):
    def get(self, request, card_id):
        me       = User.objects.get(id=self.user_id)
        card     = models.Card.objects.get(id=card_id)
        included = card.relations.filter(done=False)
        cards    = models.Card.get_allowed_cards(me)
        total    = cards.count()
        cards    = cards.filter(done=False)
        excluded = cards.exclude(Q(pk__in=included) | Q(pk=card.pk))

        return render(request, 'card_app/manage-card-relations.html', 
        {'included': included, 'excluded': excluded, 'card': card, 
        'total': total, 'count': total, 'me': me, 
        'organization': me.default,'form':forms.CardSearchForm()})

    def post(self, request, card_id):
        sqlike = models.Card.from_sqlike()

        form   = forms.CardSearchForm(request.POST, sqlike=sqlike)
        me     = User.objects.get(id=self.user_id)
        card   = models.Card.objects.get(id=card_id)
        cards  = models.Card.get_allowed_cards(me)
        total  = cards.count()

        if not form.is_valid():
            return render(request, 'card_app/manage-card-relations.html', 
                {'me': me, 'organization': me.default, 'card': card,
                     'total': total, 'count': 0, 'form':form}, status=400)

        included = card.relations.all()
        excluded = cards.exclude(Q(pk__in=included) | Q(pk=card.pk))

        included = included.filter(Q(done=form.cleaned_data['done']))
        included = sqlike.run(included)

        excluded = excluded.filter(Q(done=form.cleaned_data['done']))
        excluded = sqlike.run(excluded)
        count    = excluded.count() + included.count()

        return render(request, 'card_app/manage-card-relations.html', 
        {'included': included, 'excluded': excluded, 'card': card, 
        'count': count, 'total': total, 'me': me, 'form':form})


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
        sqlike   = User.from_sqlike()
        form     = forms.UserSearchForm(request.POST, sqlike=sqlike)

        me       = User.objects.get(id=self.user_id)
        card     = models.Card.objects.get(id=card_id)
        included = card.workers.all()
        excluded = me.default.users.exclude(tasks=card)
        total    = included.count() + excluded.count()

        if not form.is_valid():
            return render(request, 'card_app/manage-card-workers.html', 
                {'me': me, 'card': card, 'form':form, 'total': total, 
                    'count': total,}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)
        count = included.count() + excluded.count()

        return render(request, 'card_app/manage-card-workers.html', 
        {'included': included, 'excluded': excluded, 'card': card, 'total': total,
        'count': count, 'me': me, 'form':form})

class UnbindCardWorker(GuardianView):
    def get(self, request, card_id, user_id):
        user = User.objects.get(id=user_id)
        card = models.Card.objects.get(id=card_id)

        if not card.ancestor:
            return HttpResponse("This card is on clipboard! \
               It can't unbind.", status=403)

        if not card.ancestor.ancestor:
            return HttpResponse("The card list is on \
                clipboard! Can't unbind now.", status=403)

        card.workers.remove(user)
        card.save()

        me = User.objects.get(id=self.user_id)
        event = models.EUnbindCardWorker.objects.create(
        organization=me.default, ancestor=card.ancestor, 
        card=card, user=me, peer=user)
        event.dispatch(*card.ancestor.ancestor.members.all())
        event.save()

        # me.ws_sound(card.ancestor.ancestor)

        return HttpResponse(status=200)

class BindCardWorker(GuardianView):
    def get(self, request, card_id, user_id):
        user = User.objects.get(id=user_id)
        card = models.Card.objects.get(id=card_id)

        if not card.ancestor:
            return HttpResponse("This card is on clipboard! \
               It can't bind.", status=403)

        if not card.ancestor.ancestor:
            return HttpResponse("The card list is on \
                clipboard! Can't bind now.", status=403)

        card.workers.add(user)
        card.save()

        me = User.objects.get(id=self.user_id)
        event = models.EBindCardWorker.objects.create(
        organization=me.default, ancestor=card.ancestor, 
        card=card, user=me, peer=user)
        event.dispatch(*card.ancestor.ancestor.members.all())
        event.save()

        # me.ws_sound(card.ancestor.ancestor)

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
        sqlike = Tag.from_sqlike()
        form = forms.TagSearchForm(request.POST, sqlike=sqlike)

        me = User.objects.get(id=self.user_id)
        card = models.Card.objects.get(id=card_id)
        included = card.tags.all()
        excluded = me.default.tags.exclude(cards=card)
        total = included.count() + excluded.count()

        if not form.is_valid():
            return render(request, 'card_app/manage-card-tags.html', 
                {'organization': me.default, 'card': card, 'total': total,
                        'count': 0, 'form':form}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)

        count = included.count() + excluded.count()

        return render(request, 'card_app/manage-card-tags.html', 
        {'included': included, 'excluded': excluded, 'card': card,
        'me': me, 'organization': me.default,
        'total': total, 'count': count, 'form':form})

class UnbindCardTag(GuardianView):
    def get(self, request, card_id, tag_id):
        tag = core_app.models.Tag.objects.get(id=tag_id)
        card = models.Card.objects.get(id=card_id)

        if not card.ancestor:
            return HttpResponse("This card is on clipboard! \
               Can't untag now.", status=403)

        if not card.ancestor.ancestor:
            return HttpResponse("The card list is on \
                clipboard! Can't untag now.", status=403)

        card.tags.remove(tag)
        card.save()

        # me = User.objects.get(id=self.user_id)

        # event = models.EUnbindCardTag.objects.create(
        # organization=me.default, ancestor=card.ancestor, 
        # card=card, user=me, peer=user)
        # event.dispatch(*card.ancestor.users.all())
        # event.save()
        me = User.objects.get(id=self.user_id)
        event = models.EUnbindTagCard.objects.create(
        organization=me.default, ancestor=card.ancestor, 
        card=card, tag=tag, user=me)
        event.dispatch(*card.ancestor.ancestor.members.all())
        event.save()

        # me.ws_sound(card.ancestor.ancestor)

        return HttpResponse(status=200)

class BindCardTag(GuardianView):
    def get(self, request, card_id, tag_id):
        tag = core_app.models.Tag.objects.get(id=tag_id)
        card = models.Card.objects.get(id=card_id)

        if not card.ancestor:
            return HttpResponse("This card is on clipboard! \
               Can't tag now.", status=403)

        if not card.ancestor.ancestor:
            return HttpResponse("The card list is on \
                clipboard! Can't tag now.", status=403)

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
        event.dispatch(*card.ancestor.ancestor.members.all())
        event.save()

        # me.ws_sound(card.ancestor.ancestor)

        return HttpResponse(status=200)

class Done(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)

        if not card.ancestor:
            return HttpResponse("This card is on clipboard! \
               It can't archive now.", status=403)

        if not card.ancestor.ancestor:
            return HttpResponse("The card list is on \
                clipboard! Can't archive now.", status=403)

        card.done = True
        card.save()

        user = core_app.models.User.objects.get(id=self.user_id)

        # cards in the clipboard cant be archived.
        event    = models.EArchiveCard.objects.create(organization=user.default,
        ancestor=card.ancestor, card=card, user=user)

        users = card.ancestor.ancestor.members.all()
        event.dispatch(*users)

        # Missing event.
        # user.ws_sound(card.ancestor.ancestor)

        return redirect('card_app:view-data', card_id=card.id)

class Undo(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)

        if not card.ancestor:
            return HttpResponse("This card is on clipboard! \
               It can't unarchive now.", status=403)

        if not card.ancestor.ancestor:
            return HttpResponse("The card list is on \
                clipboard! Can't unarchive now.", status=403)

        card.done = False
        card.save()

        user = core_app.models.User.objects.get(id=self.user_id)

        # cards in the clipboard cant be archived.
        event    = models.EUnarchiveCard.objects.create(organization=user.default,
        ancestor=card.ancestor, card=card, user=user)

        users = card.ancestor.ancestor.members.all()
        event.dispatch(*users)

        # user.ws_sound(card.ancestor.ancestor)

        return redirect('card_app:view-data', card_id=card.id)

class CardWorkerInformation(GuardianView):
    def get(self, request, peer_id, card_id):
        event = models.EBindCardWorker.objects.filter(card__id=card_id,
        peer__id=peer_id).last()

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
        peer = User.objects.get(id=peer_id)
        card = models.Card.objects.get(id=card_id)

        form = forms.CardAttentionForm()
        return render(request, 'card_app/request-card-attention.html', 
        {'peer': peer,  'card': card, 'form': form})

    def post(self, request, peer_id, card_id):
        user = User.objects.get(id=self.user_id)
        peer = User.objects.get(id=peer_id)
        card = models.Card.objects.get(id=card_id)
        form = forms.CardAttentionForm(request.POST)

        if not form.is_valid():
            return render(request, 'card_app/request-card-attention.html', 
                    {'peer': peer, 'card': card, 'form': form})    

        url  = reverse('card_app:card-link', 
            kwargs={'card_id': card.id})

        url = '%s%s' % (settings.LOCAL_ADDR, url)
        msg = '%s (%s) has requested your attention on\n%s\n\n%s' % (
        user.name, user.email, url, form.cleaned_data['message'])

        send_mail('%s %s' % (user.default.name, 
        user.name), msg, user.email, [peer.email], fail_silently=False)
        return redirect('card_app:card-worker-information', 
        peer_id=peer.id, card_id=card.id)

class CardTagInformation(GuardianView):
    def get(self, request, tag_id, card_id):
        event = models.EBindTagCard.objects.filter(card__id=card_id,
        tag__id=tag_id).last()

        return render(request, 'post_app/post-tag-information.html', 
        {'user': event.user, 'created': event.created, 'tag':event.tag})

class AlertCardWorkers(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)
        user = User.objects.get(id=self.user_id)

        form = forms.AlertCardWorkersForm()
        return render(request, 'card_app/alert-card-workers.html', 
        {'card': card, 'form': form, 'user': user})

    def post(self, request, card_id):
        user = User.objects.get(id=self.user_id)
        card = models.Card.objects.get(id=card_id)
        form = forms.AlertCardWorkersForm(request.POST)

        if not form.is_valid():
            return render(request,'card_app/alert-card-workers.html', 
                    {'user': user, 'card': card, 'form': form})    

        url  = reverse('card_app:card-link', 
        kwargs={'card_id': card.id})

        url = '%s%s' % (settings.LOCAL_ADDR, url)
        msg = '%s (%s) has alerted you on\n%s\n\n%s' % (
        user.name, user.email, url, form.cleaned_data['message'])

        for ind in card.workers.values_list('email'):
            send_mail('%s %s' % (user.default.name, 
                user.name), msg, user.email, 
                    [ind[0]], fail_silently=False)

        return HttpResponse(status=200)


class UndoClipboard(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)
        user = User.objects.get(id=self.user_id)
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
        user = User.objects.get(id=self.user_id)

        event.card.ancestor = event.ancestor
        event.card.save()

        event1 = EPasteCard(
        organization=user.default, ancestor=event.ancestor, user=user)
        event1.save(hcache=False)
        event1.cards.add(event.card)
        event.dispatch(*event.ancestor.ancestor.members.all())
        event1.save()
        
        clipboard, _ = Clipboard.objects.get_or_create(
        user=user, organization=user.default)

        clipboard.cards.remove(event.card)

class ListAllTasks(GuardianView):
    def get(self, request):
        me        = User.objects.get(id=self.user_id)
        filter, _ = GlobalTaskFilter.objects.get_or_create(
        user=me, organization=me.default)

        form  = forms.GlobalTaskFilterForm(instance=filter)

        cards = models.Card.get_allowed_cards(me)
        cards = cards.filter(Q(workers__isnull=False))
        total = cards.count()
        cards = filter.get_partial(cards)
        
        sqlike = models.Card.from_sqlike()
        sqlike.feed(filter.pattern)

        cards = sqlike.run(cards)

        count = cards.count()
        cards = cards.only('done', 'label', 'id').order_by('id')
        elems = JScroll(me.id, 'card_app/list-all-tasks-scroll.html', cards)

        return render(request, 'card_app/list-all-tasks.html', 
        {'total': total, 'count': count, 
        'form': form, 'elems': elems.as_div()})

    def post(self, request):
        me        = User.objects.get(id=self.user_id)
        filter, _ = GlobalTaskFilter.objects.get_or_create(
        user=me, organization=me.default)

        sqlike = models.Card.from_sqlike()
        form   = forms.GlobalTaskFilterForm(
            request.POST, sqlike=sqlike, instance=filter)

        cards = models.Card.get_allowed_cards(me)
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
        elems = JScroll(me.id, 'card_app/list-all-tasks-scroll.html', cards)

        return render(request, 'card_app/list-all-tasks.html', 
        {'form': form, 'elems': elems.as_div(), 'total': total, 'count': count})

class Find(GuardianView):
    def get(self, request):
        me    = User.objects.get(id=self.user_id)

        filter, _ = GlobalCardFilter.objects.get_or_create(
        user=me, organization=me.default)
        form  = forms.GlobalCardFilterForm(instance=filter)

        cards = models.Card.get_allowed_cards(me)
        total = cards.count()

        sqlike = models.Card.from_sqlike()
        sqlike.feed(filter.pattern)

        cards = cards.filter(Q(done=filter.done))
        cards = sqlike.run(cards)
        count = cards.count()

        cards = cards.only('done', 'label', 'id').order_by('id')
        elems = JScroll(me.id, 'card_app/find-scroll.html', cards)

        return render(request, 'card_app/find.html', 
        {'form': form, 'elems':  elems.as_div(), 'total': total, 'count': count})

    def post(self, request):
        me        = User.objects.get(id=self.user_id)
        filter, _ = GlobalCardFilter.objects.get_or_create(
        user=me, organization=me.default)

        sqlike = models.Card.from_sqlike()
        form  = forms.GlobalCardFilterForm(request.POST, sqlike=sqlike, instance=filter)

        cards = models.Card.get_allowed_cards(me)
        total = cards.count()

        if not form.is_valid():
            return render(request, 'card_app/find.html', 
                {'form': form, 'total': total, 'count': 0}, status=400)
        form.save()

        cards  = cards.filter(Q(done=filter.done))
        cards  = sqlike.run(cards)
        count =  cards.count()

        cards = cards.only('done', 'label', 'id').order_by('id')
        elems = JScroll(me.id, 'card_app/find-scroll.html', cards)

        return render(request, 'card_app/find.html', 
        {'form': form, 'elems':  elems.as_div(), 'total': total, 'count': count})

class CardEvents(GuardianView):
    def get(self, request, card_id):
        card = models.Card.objects.get(id=card_id)

        query = Q(erelatecard__card0__id=card.id) | Q(erelatecard__card1__id=card.id) \
        | Q(eunrelatecard__card0__id=card.id) | Q(eunrelatecard__card1__id=card.id) | \
        Q(ecreatecard__card__id=card.id) | Q(ebindcardworker__card__id=card.id) | \
        Q(eunbindcardworker__card__id=card.id) | Q(ecreatefork__card0=card.id) \
        | Q(ecreatefork__card1=card.id) | Q(ecreatepostfork__card__id=card.id) | \
        Q(eupdatecard__card__id=card.id) | Q(ebindtagcard__card__id=card.id) | \
        Q(eunbindtagcard__card__id=card.id) | Q(ecutcard__card__id=card.id) |\
        Q(earchivecard__card__id=card.id) | Q(epastecard__cards=card.id) | \
        Q(ecopycard__card=card.id)

        events = Event.objects.filter(query).order_by('-created').values('html')
        return render(request, 'card_app/card-events.html', 
        {'card': card, 'elems': events})

class Unpin(GuardianView):
    def get(self, request, pin_id):
        pin = CardPin.objects.get(id=pin_id)
        pin.delete()
        return redirect('board_app:list-pins')






