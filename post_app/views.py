from post_app.models import EUnbindTagPost, ECreatePost, EUpdatePost, \
PostFileWrapper, EDeletePost, EAssignPost, EBindTagPost, EUnassignPost, \
PostFilter, GlobalPostFilter, ECutPost, EArchivePost, ECopyPost, \
GlobalAssignmentFilter, EUnarchivePost
from django.db.models import Q, F, Exists, OuterRef, Count, Sum
from core_app.models import Clipboard, Tag, User, Event
from django.db.models.functions import Concat
from django.shortcuts import render, redirect
from core_app.views import GuardianView
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.core.mail import send_mail
from django.http import HttpResponse
from list_app.models import List
from timeline_app.models import Timeline, EPastePost
from django.conf import settings
from jsim.jscroll import JScroll
from card_app.models import Card
from card_app.forms import CardForm, ListSearchform
from functools import reduce
from re import split
from . import forms
from . import models
import operator

import json

class Post(GuardianView):
    """
    This view is supposed to be performed only if the user
    belongs to the timeline or if he is a worker of the post.
    """

    def get(self, request, post_id):
        post = models.Post.objects.get(
        Q(ancestor__users=self.me) | Q(workers=self.me), id=post_id, 
        ancestor__organization=self.me.default)

        if not post.ancestor:
            return HttpResponse("This post is on clipboard!\
                It can't be accessed now.", status=403)

        boardpins    = self.me.boardpin_set.filter(organization=self.me.default)
        listpins     = self.me.listpin_set.filter(organization=self.me.default)
        cardpins     = self.me.cardpin_set.filter(organization=self.me.default)
        timelinepins = self.me.timelinepin_set.filter(
        organization=self.me.default)

        return render(request, 'post_app/post.html', 
        {'post':post, 'boardpins': boardpins, 'listpins': listpins, 
        'cardpins': cardpins, 'tags': post.tags.all(), 
        'timelinepins': timelinepins, 'user': self.me, })

class PostLink(GuardianView):
    """
    This view worksk alike like Post in terms of permissions.
    """

    def get(self, request, post_id):
        post = models.Post.objects.get(
        Q(ancestor__users=self.me) | Q(workers=self.me), id=post_id, 
        ancestor__organization=self.me.default)

        if not post.ancestor:
            return HttpResponse("This post is on clipboard!\
                It can't be accessed now.", status=403)

        organizations = self.me.organizations.exclude(id=self.me.default.id)

        boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        listpins = self.me.listpin_set.filter(organization=self.me.default)
        cardpins = self.me.cardpin_set.filter(organization=self.me.default)
        timelinepins = self.me.timelinepin_set.filter(organization=self.me.default)

        return render(request, 'post_app/post-link.html', 
        {'post':post, 'boardpins': boardpins, 'listpins': listpins, 
        'timelinepins': timelinepins, 'cardpins': cardpins, 'user': self.me, 
        'default': self.me.default, 'organization': self.me.default, 
        'organizations': organizations, 'settings': settings})

class CreatePost(GuardianView):
    """
    The logged user can create a post on the timeline just if his default timeline
    contains the timeline and he belongs to the timeline.
    """

    def get(self, request, ancestor_id):
        ancestor   = self.me.timelines.get(id=ancestor_id, 
        organization=self.me.default)

        form = forms.PostForm()

        return render(request, 'post_app/create-post.html', 
        {'form':form, 'ancestor':ancestor})

    def post(self, request, ancestor_id):
        ancestor   = self.me.timelines.get(id=ancestor_id, 
        organization=self.me.default)

        form = forms.PostForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, 'post_app/create-post.html',
                        {'form': form, 'ancestor': ancestor}, status=400)

        post          = form.save(commit=False)
        post.user     = self.me
        post.ancestor = ancestor
        post.save()

        event = ECreatePost.objects.create(organization=self.me.default,
        timeline=ancestor, post=post, user=self.me)

        users = ancestor.users.all()
        event.dispatch(*users)

        return redirect('timeline_app:list-posts', 
        timeline_id=ancestor_id)

class UpdatePost(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)
        return render(request, 'post_app/update-post.html',
        {'post': post, 'form': forms.PostForm(instance=post)})

    def post(self, request, post_id):
        record  = models.Post.objects.get(id=post_id)

        if not record.ancestor:
            return HttpResponse("Can't update! On \
                someone clipboard.", status=403)

        form = forms.PostForm(request.POST, request.FILES, instance=record)

        if not form.is_valid():
            return render(request, 'post_app/update-post.html',
                   {'post': record, 'form': form}, status=400)
        record.save()

        event = EUpdatePost.objects.create(organization=self.me.default,
        timeline=record.ancestor, post=record, user=self.me)

        event.dispatch(*record.ancestor.users.all())

        # Notify workers of the event, in case the post
        # is on a timeline whose worker is not on.
        event.dispatch(*record.workers.all())

        return redirect('post_app:refresh-post', 
        post_id=record.id)


class AttachFile(GuardianView):
    """
    """

    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)
        attachments = post.postfilewrapper_set.all()
        form = forms.PostFileWrapperForm()
        return render(request, 'post_app/attach-file.html', 
        {'post':post, 'form': form, 'attachments': attachments})

    def post(self, request, post_id):
        post = models.Post.objects.get(id=post_id)

        if not post.ancestor:
            return HttpResponse("Post was put on clipboard!\
                can't attach file now.", status=403)

        attachments = post.postfilewrapper_set.all()
        form = forms.PostFileWrapperForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, 'post_app/attach-file.html', 
                {'post':post, 'form': form, 'attachments': attachments})
        record = form.save(commit = False)
        record.post = post
        form.save()

        event = models.EAttachPostFile.objects.create(
        organization=self.me.default, filewrapper=record, 
        post=post, user=self.me)

        event.dispatch(*post.ancestor.users.all())
        event.save()

        return self.get(request, post_id)

class DetachFile(GuardianView):
    """
    """

    def get(self, request, filewrapper_id):
        filewrapper = PostFileWrapper.objects.get(id=filewrapper_id)

        if not filewrapper.post.ancestor:
            return HttpResponse("Post was put on clipboard!\
                can't dettach file now.", status=403)

        attachments = filewrapper.post.postfilewrapper_set.all()

        form = forms.PostFileWrapperForm()

        event = models.EDettachPostFile.objects.create(
        organization=self.me.default, filename=filewrapper.file.name, 
        post=filewrapper.post, user=self.me)

        filewrapper.delete()

        event.dispatch(*filewrapper.post.ancestor.users.all())
        event.save()

        return render(request, 'post_app/attach-file.html', 
        {'post':filewrapper.post, 'form': form, 'attachments': attachments})

class DeletePost(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id = post_id)

        if not post.ancestor:
            return HttpResponse("On clipboard, can't \
                delete now!", status=403)

        event = EDeletePost.objects.create(organization=self.me.default,
        timeline=post.ancestor, post_label=post.label, user=self.me)
        users = post.ancestor.users.all()
        event.dispatch(*users)

        ancestor = post.ancestor
        post.delete()

        return redirect('timeline_app:list-posts', 
        timeline_id=ancestor.id)

class PostWorkerInformation(GuardianView):
    def get(self, request, peer_id, post_id):
        event = EAssignPost.objects.filter(post__id=post_id,
        peer__id=peer_id).last()

        active_posts = event.peer.assignments.filter(done=False)
        done_posts = event.peer.assignments.filter(done=True)

        active_cards = event.peer.tasks.filter(done=False)
        done_cards = event.peer.tasks.filter(done=True)

        active_tasks = active_posts.count() + active_cards.count()
        done_tasks = done_posts.count() + done_cards.count()

        return render(request, 
        'post_app/post-worker-information.html',  
        {'peer': event.peer, 'active_tasks': active_tasks, 
         'post': event.post,  'done_tasks': done_tasks,
        'created': event.created, 'user':event.user})

class PostTagInformation(GuardianView):
    def get(self, request, tag_id, post_id):
        event = EBindTagPost.objects.filter(post__id=post_id,
        tag__id=tag_id).last()

        return render(request, 'post_app/post-tag-information.html', 
        {'user': event.user, 'created': event.created, 'tag':event.tag})

class UnassignPostUser(GuardianView):
    def get(self, request, post_id, user_id):
        post = models.Post.objects.get(id=post_id)

        if not post.ancestor:
            return HttpResponse("On clipboard! Can't \
                unassign user.", status=403)

        user = User.objects.get(id=user_id)

        # me.ws_sound(post.ancestor)

        event = EUnassignPost.objects.create(
        organization=self.me.default, ancestor=post.ancestor, 
        post=post, user=self.me, peer=user)

        event.dispatch(*post.ancestor.users.all())
        
        # As posts can be assigned to users off the timeline.
        # We make sure them get the evvent.
        event.dispatch(*post.workers.all())
        event.save()

        post.workers.remove(user)
        post.save()

        return HttpResponse(status=200)

class AssignPostUser(GuardianView):
    def get(self, request, post_id, user_id):
        post = models.Post.objects.get(id=post_id)

        if not post.ancestor:
            return HttpResponse("On clipboard! Can't \
                assign user.", status=403)

        user = User.objects.get(id=user_id)

        post.workers.add(user)
        post.save()

        event = EAssignPost.objects.create(
        organization=self.me.default, ancestor=post.ancestor, 
        post=post, user=self.me, peer=user)

        event.dispatch(*post.ancestor.users.all())
        event.dispatch(*post.workers.all())
        event.save()

        return HttpResponse(status=200)

class ManagePostWorkers(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)

        included = post.workers.all()
        excluded = self.me.default.users.exclude(assignments=post)
        total    = included.count() + excluded.count()

        return render(request, 'post_app/manage-post-workers.html', 
        {'included': included, 'excluded': excluded, 'post': post,
        'count': total, 'total': total, 'me': self.me, 
        'form':forms.UserSearchForm()})

    def post(self, request, post_id):
        sqlike = User.from_sqlike()
        form = forms.UserSearchForm(request.POST, sqlike=sqlike)

        post = models.Post.objects.get(id=post_id)
        included = post.workers.all()
        excluded = self.me.default.users.exclude(assignments=post)
        total    = included.count() + excluded.count()

        if not form.is_valid():
            return render(request, 'post_app/manage-post-workers.html',  
                {'me': self.me, 'total': total, 'count': 0, 'post': post, 
                    'form':form}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)
        count = included.count() + excluded.count()

        return render(request, 'post_app/manage-post-workers.html', 
        {'included': included, 'excluded': excluded, 'post': post,
        'me': self.me, 'form':form, 'total': total, 'count': count,})

class SetupPostFilter(GuardianView):
    def get(self, request, timeline_id):
        filter = PostFilter.objects.get(
        user__id=self.user_id, timeline__id=timeline_id)
        timeline = Timeline.objects.get(id=timeline_id)

        return render(request, 'post_app/setup-post-filter.html', 
        {'form': forms.PostFilterForm(instance=filter), 
        'timeline': timeline})

    def post(self, request, timeline_id):
        record = PostFilter.objects.get(
        timeline__id=timeline_id, user__id=self.user_id)
        sqlike = models.Post.from_sqlike()

        form     = forms.PostFilterForm(request.POST, sqlike=sqlike, instance=record)
        timeline = Timeline.objects.get(id=timeline_id)

        if not form.is_valid():
            return render(request, 'post_app/setup-post-filter.html',
                   {'timeline': record, 'form': form}, status=400)
        form.save()
        return redirect('timeline_app:list-posts', timeline_id=timeline.id)

class Find(GuardianView):
    def get(self, request):
        filter, _ = GlobalPostFilter.objects.get_or_create(
        user=self.me, organization=self.me.default)
        form  = forms.GlobalPostFilterForm(instance=filter)

        posts = models.Post.get_allowed_posts(self.me)
        total = posts.count()

        sqlike = models.Post.from_sqlike()
        sqlike.feed(filter.pattern)

        posts = posts.filter(Q(done=filter.done))
        posts = sqlike.run(posts)

        count = posts.count()

        posts = posts.only('done', 'label', 'id').order_by('id')
        elems = JScroll(self.me.id, 'post_app/find-scroll.html', posts)

        return render(request, 'post_app/find.html', 
        {'form': form, 'elems':  elems.as_div(), 'total': total, 'count': count})

    def post(self, request):
        filter, _ = GlobalPostFilter.objects.get_or_create(
        user=self.me, organization=self.me.default)

        sqlike = models.Post.from_sqlike()
        form  = forms.GlobalPostFilterForm(request.POST, sqlike=sqlike, instance=filter)

        posts = models.Post.get_allowed_posts(self.me)
        total = posts.count()

        if not form.is_valid():
            return render(request, 'post_app/find.html', 
                {'form': form, 'total': total, 'count': 0}, status=400)
        form.save()

        posts  = posts.filter(Q(done=filter.done))
        posts  = sqlike.run(posts)
        count =  posts.count()

        posts = posts.only('done', 'label', 'id').order_by('id')
        elems = JScroll(self.me.id, 'post_app/find-scroll.html', posts)

        return render(request, 'post_app/find.html', 
        {'form': form, 'elems':  elems.as_div(), 'total': total, 'count': count})

class CutPost(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)

        if not post.ancestor:
            return HttpResponse("Already on someone \
                clipboard!", status=403)

        timeline = post.ancestor

        post.ancestor = None
        post.save()

        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)

        clipboard.posts.add(post)

        event = ECutPost.objects.create(organization=self.me.default,
        timeline=timeline, post=post, user=self.me)
        users = timeline.users.all()
        event.dispatch(*users)

        return redirect('timeline_app:list-posts', 
        timeline_id=timeline.id)

class CopyPost(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)

        if not post.ancestor:
            return HttpResponse("Already on someone \
                clipboard!", status=403)

        copy         = post.duplicate()
        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)
        clipboard.posts.add(copy)

        event = ECopyPost.objects.create(organization=self.me.default,
        timeline=post.ancestor, post=post, user=self.me)
        users = post.ancestor.users.all()
        event.dispatch(*users)

        return redirect('timeline_app:list-posts', 
        timeline_id=post.ancestor.id)

class Done(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)

        if not post.ancestor:
            return HttpResponse("Can't archive post now, \
                it is on clipboard.", status=403)

        post.done = True
        post.save()

        # posts in the clipboard cant be archived.
        event = EArchivePost.objects.create(organization=self.me.default,
        timeline=post.ancestor, post=post, user=self.me)

        users = post.ancestor.users.all()
        event.dispatch(*users)

        return redirect('post_app:refresh-post', 
        post_id=post.id)

class ManagePostTags(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)

        included = post.tags.all()
        excluded = self.me.default.tags.exclude(posts=post)
        total = included.count() + excluded.count()

        return render(request, 'post_app/manage-post-tags.html', 
        {'included': included, 'excluded': excluded, 'post': post,
        'organization': self.me.default,'form':forms.TagSearchForm(), 
        'total': total, 'count': total})

    def post(self, request, post_id):
        sqlike = Tag.from_sqlike()
        form = forms.TagSearchForm(request.POST, sqlike=sqlike)

        post = models.Post.objects.get(id=post_id)
        included = post.tags.all()
        excluded = self.me.default.tags.exclude(posts=post)
        total = included.count() + excluded.count()

        if not form.is_valid():
            return render(request, 'post_app/manage-post-tags.html', 
                {'total': total, 'organization': self.me.default, 
                    'post': post, 'form':form, 'count': 0}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)
        count = included.count() + excluded.count()

        return render(request, 'post_app/manage-post-tags.html', 
        {'included': included, 'excluded': excluded, 'post': post, 
        'total': total, 'count': count, 'me': self.me, 'form':form, 
        'organization': self.me.default, })

class UnbindPostTag(GuardianView):
    def get(self, request, post_id, tag_id):
        post = models.Post.objects.get(id=post_id)

        if not post.ancestor:
            return HttpResponse("Post on clipboard! \
                Can't unbind tag.", status=403)

        tag = Tag.objects.get(id=tag_id)
        post.tags.remove(tag)
        post.save()

        event = EUnbindTagPost.objects.create(
        organization=self.me.default, ancestor=post.ancestor, 
        post=post, tag=tag, user=self.me)
        event.dispatch(*post.ancestor.users.all())
        event.save()

        return HttpResponse(status=200)

class BindPostTag(GuardianView):
    def get(self, request, post_id, tag_id):
        post = models.Post.objects.get(id=post_id)

        if not post.ancestor:
            return HttpResponse("Post on clipboard! \
                Can't unbind tag.", status=403)

        tag = Tag.objects.get(id=tag_id)
        post.tags.add(tag)
        post.save()

        event = EBindTagPost.objects.create(
        organization=self.me.default, ancestor=post.ancestor, 
        post=post, tag=tag, user=self.me)
        event.dispatch(*post.ancestor.users.all())
        event.save()

        return HttpResponse(status=200)

class CancelPostCreation(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id = post_id)
        post.delete()

        return HttpResponse(status=200)

class Undo(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)

        if not post.ancestor:
            return HttpResponse("Post on clipboard! \
                Can't unarchive post.", status=403)

        post.done = False
        post.save()

        event = EUnarchivePost.objects.create(organization=self.me.default,
        timeline=post.ancestor, post=post, user=self.me)

        users = post.ancestor.users.all()
        event.dispatch(*users)

        return redirect('post_app:refresh-post', 
        post_id=post.id)


class RequestPostAttention(GuardianView):
    def get(self, request, peer_id, post_id):
        peer = User.objects.get(id=peer_id)
        post = models.Post.objects.get(id=post_id)

        form = forms.PostAttentionForm()
        return render(request, 'post_app/request-post-attention.html', 
        {'peer': peer,  'post': post, 'form': form})

    def post(self, request, peer_id, post_id):
        peer = User.objects.get(id=peer_id)
        post = models.Post.objects.get(id=post_id)
        form = forms.PostAttentionForm(request.POST)

        if not form.is_valid():
            return render(request, 'post_app/request-post-attention.html', 
                    {'peer': peer, 'post': post, 'form': form})    

        url  = reverse('post_app:post-link', 
            kwargs={'post_id': post.id})

        url = '%s%s' % (settings.LOCAL_ADDR, url)
        msg = '%s (%s) has requested your attention on\n%s\n\n%s' % (
        self.me.name, self.me.email, url, form.cleaned_data['message'])

        send_mail('%s %s' % (self.me.default.name, 
        self.me.name), msg, self.me.email, [peer.email], fail_silently=False)

        return redirect('post_app:post-worker-information', 
        peer_id=peer.id, post_id=post.id)

class AlertPostWorkers(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)

        form = forms.AlertPostWorkersForm()
        return render(request, 'post_app/alert-post-workers.html', 
        {'post': post, 'form': form, 'user': self.me})

    def post(self, request, post_id):
        post = models.Post.objects.get(id=post_id)
        form = forms.AlertPostWorkersForm(request.POST)

        if not form.is_valid():
            return render(request,'post_app/alert-post-workers.html', 
                    {'user': self.me, 'post': post, 'form': form})    

        url  = reverse('post_app:post-link', 
        kwargs={'post_id': post.id})

        url = '%s%s' % (settings.LOCAL_ADDR, url)
        msg = '%s (%s) has alerted you on\n%s\n\n%s' % (
        self.me.name, self.me.email, url, form.cleaned_data['message'])

        for ind in post.workers.values_list('email'):
            send_mail('%s %s' % (self.me.default.name, 
                self.me.name), msg, self.me.email, 
                    [ind[0]], fail_silently=False)

        return HttpResponse(status=200)

class ConfirmPostDeletion(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)
        return render(request, 'post_app/confirm-post-deletion.html', 
        {'post': post})


class UndoClipboard(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)
        event0 = post.e_copy_post1.last()
        event1 = post.e_cut_post1.last()

        # Then it is a copy because there is no event
        # mapped to it. A copy contains no e_copy_post1 nor
        # e_cut_post1.
        if not (event0 or event1):
            post.delete()
        else:
            self.undo_cut(event1)

        return redirect('core_app:list-clipboard')

    def undo_cut(self, event):
        event.post.ancestor = event.timeline
        event.post.save()

        event1 = EPastePost(organization=self.me.default, 
        timeline=event.timeline, user=self.me)

        event1.save(hcache=False)
        event1.posts.add(event.post)
        event1.dispatch(*event.timeline.users.all())
        event1.save()
        
        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)

        clipboard.posts.remove(event.post)

class PullCardContent(GuardianView):
    """
    """

    def get(self, request, ancestor_id, post_id):
        ancestor = List.objects.get(id=ancestor_id)
        post     = models.Post.objects.get(id=post_id)
        form     = CardForm(initial={'label': post.label, 'data': post.data})

        return render(request, 'post_app/create-fork.html', 
        {'form':form, 'post': post, 'ancestor': ancestor})

class CreateCardFork(GuardianView):
    """
    """

    def get(self, request, ancestor_id, post_id):
        post = models.Post.objects.get(id=post_id)

        if not post.ancestor:
            return HttpResponse("Post on clipboard! \
                Can't fork now.", status=403)

        ancestor = List.objects.get(id=ancestor_id)
        form = CardForm()

        return render(request, 'post_app/create-fork.html', 
        {'form':form, 'post': post, 'ancestor': ancestor})

    def post(self, request, ancestor_id, post_id):
        ancestor = List.objects.get(id=ancestor_id)
        post     = models.Post.objects.get(id=post_id)
        form     = CardForm(request.POST)

        if not form.is_valid():
            return render(request, 'post_app/create-fork.html', 
                {'form':form, 'ancestor': ancestor, 'post': post}, status=400)

        fork             = form.save(commit=False)
        fork.owner       = self.me
        fork.ancestor    = ancestor
        fork.parent_post = post
        fork.save()

        # # path = post.path.all()
        # fork.parent_post = post
        # # fork.path.add(*path, post)
        # fork.save()

        event = models.ECreateCardFork.objects.create(organization=self.me.default,
        ancestor=post.ancestor, post=post, card=fork, user=self.me)

        # The timeline users and the board users get the event.
        event.dispatch(*post.ancestor.users.all())
        event.dispatch(*fork.ancestor.ancestor.members.all())

        return redirect('card_app:view-data', card_id=fork.id)

class SelectForkList(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)
        form = ListSearchform()

        boards = self.me.boards.filter(organization=self.me.default)
        lists  = List.objects.filter(ancestor__in=boards)

        return render(request, 'post_app/select-fork-list.html', 
        {'form':form, 'post': post, 'elems': lists})

    def post(self, request, post_id):
        form = forms.ListSearchform(request.POST)
        post = models.Post.objects.get(id=post_id)

        lists = List.objects.filter(ancestor__in=self.me.boards.all())

        if not form.is_valid():
            return render(request, 'post_app/select-fork-list.html', 
                  {'form':form, 'elems': lists, 'post': post})

        lists = lists.annotate(text=Concat('ancestor__name', 'name'))

        # Not sure if its the fastest way to do it.
        chks = split(' *\++ *', form.cleaned_data['pattern'])
        lists = lists.filter(reduce(operator.and_, 
        (Q(text__contains=ind) for ind in chks))) 

        return render(request, 'post_app/select-fork-list.html', 
        {'form':form, 'post': post, 'elems': lists})

class PostEvents(GuardianView):
    def get(self, request, post_id):
        post  = models.Post.objects.get(id=post_id)

        query = Q(eunbindtagpost__post__id= post.id) | \
        Q(ecreatepost__post__id=post.id) | Q(eupdatepost__post__id= post.id) | \
        Q(eassignpost__post__id=post.id) | Q(ebindtagpost__post__id= post.id) |\
        Q(eunassignpost__post__id= post.id)| \
        Q(ecutpost__post__id = post.id) | Q(earchivepost__post__id=post.id) |\
        Q(ecopypost__post__id=post.id) | Q(ecreatepostfork__post__id=post.id) | \
        Q(epastepost__posts=post.id) | Q(ecreatesnippet__child__id=post.id) | \
        Q(eupdatesnippet__child__id=post.id) | Q(edeletesnippet__child__id=post.id) |\
        Q(eattachsnippetfile__snippet__post__id=post.id) | \
        Q(eattachpostfile__post__id=post.id) | \
        Q(edettachpostfile__post__id=post.id) | \
        Q(edettachsnippetfile__snippet__post__id=post.id)

        events = Event.objects.filter(query).order_by('-created').values('html')

        return render(request, 'post_app/post-events.html', 
        {'post': post, 'elems': events})


class ListAllAssignments(GuardianView):
    def get(self, request):
        filter, _ = GlobalAssignmentFilter.objects.get_or_create(
        user=self.me, organization=self.me.default)

        form  = forms.GlobalAssignmentFilterForm(instance=filter)

        posts = models.Post.get_allowed_posts(self.me)
        posts = posts.filter(Q(workers__isnull=False))
        total = posts.count()
        posts = filter.get_partial(posts)
        
        sqlike = models.Post.from_sqlike()
        sqlike.feed(filter.pattern)

        posts = sqlike.run(posts)

        count = posts.count()
        posts = posts.only('done', 'label', 'id').order_by('id')
        elems = JScroll(self.me.id, 'post_app/list-all-assignments-scroll.html', posts)

        return render(request, 'post_app/list-all-assignments.html', 
        {'total': total, 'count': count, 
        'form': form, 'elems': elems.as_div()})

    def post(self, request):
        filter, _ = GlobalAssignmentFilter.objects.get_or_create(
        user=self.me, organization=self.me.default)

        sqlike = models.Post.from_sqlike()
        form   = forms.GlobalAssignmentFilterForm(
            request.POST, sqlike=sqlike, instance=filter)

        posts = models.Post.get_allowed_posts(self.me)
        posts = posts.filter(Q(workers__isnull=False))
        total = posts.count()

        if not form.is_valid():
            return render(request, 'post_app/list-all-assignments.html', 
                {'form': form, 'total': total,
                    'count': 0}, status=400)

        form.save()

        posts = filter.get_partial(posts)
        posts = sqlike.run(posts)

        count = posts.count()
        posts = posts.only('done', 'label', 'id').order_by('id')
        elems = JScroll(self.me.id, 'post_app/list-all-assignments-scroll.html', posts)

        return render(request, 'post_app/list-all-assignments.html', 
        {'form': form, 'elems': elems.as_div(), 'total': total, 'count': count})

class PinPost(GuardianView):
    def get(self, request, post_id):
        post = Post.objects.get(id=post_id)
        pin   = PostPin.objects.create(user=self.me, 
        organization=self.me.default, post=post)
        return redirect('board_app:list-pins')

class Unpin(GuardianView):
    def get(self, request, pin_id):
        pin = PostPin.objects.get(id=pin_id)
        pin.delete()
        return redirect('board_app:list-pins')

class RefreshPost(GuardianView):
    """
    Used to update a post view after changing its data.
    """

    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)

        if not post.ancestor:
            return HttpResponse("This post is on clipboard!\
                It can't be accessed now.", status=400)

        # boardpins = user.boardpin_set.filter(organization=user.default)
        # listpins = user.listpin_set.filter(organization=user.default)
        # cardpins = user.cardpin_set.filter(organization=user.default)
        # timelinepins = user.timelinepin_set.filter(organization=user.default)

        return render(request, 'post_app/post-data.html', 
        {'post':post, 'tags': post.tags.all(), 'user': self.me, })











