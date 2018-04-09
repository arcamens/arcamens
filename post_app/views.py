from post_app.models import EUnbindTagPost, ECreatePost, EUpdatePost, \
PostFileWrapper, EDeletePost, EAssignPost, EBindTagPost, EUnassignPost, \
PostFilter, GlobalPostFilter, ECutPost, EArchivePost, ECopyPost, AssignmentFilter
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
    """

    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)

        if not post.ancestor:
            return HttpResponse("This post is on clipboard!\
                It can't be accessed now.", status=400)

        # attachments = post.postfilewrapper_set.all()
        # workers = post.workers.all()
        return render(request, 'post_app/post.html', 
        {'post':post, })

class PostLink(GuardianView):
    """
    """

    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)

        if not post.ancestor:
            return HttpResponse("This post is on clipboard!\
                It can't be accessed now.", status=400)

        attachments = post.postfilewrapper_set.all()
        workers = post.workers.all()

        user = User.objects.get(id=self.user_id)
        organizations = user.organizations.exclude(id=user.default.id)

        return render(request, 'post_app/post-link.html', 
        {'post':post, 'attachments': attachments, 
        'tags': post.tags.all(), 'workers': workers,
        'user': user, 'default': user.default, 'organization': user.default,
        'organizations': organizations, 'settings': settings})

class CreatePost(GuardianView):
    """
    """

    def get(self, request, ancestor_id, post_id=None):
        ancestor   = Timeline.objects.get(id=ancestor_id)
        user       = User.objects.get(id=self.user_id)
        post       = models.Post.objects.create(user=user, ancestor=ancestor)
        form       = forms.PostForm(instance=post)
        post.label = 'Draft.'
        post.save()
        return render(request, 'post_app/create-post.html', 
        {'form':form, 'post': post, 'ancestor':ancestor})

    def post(self, request, ancestor_id, post_id):
        post     = models.Post.objects.get(id=post_id)
        ancestor = Timeline.objects.get(id=ancestor_id)

        form = forms.PostForm(request.POST, request.FILES, instance=post)
        if not form.is_valid():
            return render(request, 'post_app/create-post.html',
                        {'form': form, 'post':post, 
                                'ancestor': ancestor}, status=400)

        post.save()
        user  = User.objects.get(id=self.user_id)
        event = ECreatePost.objects.create(organization=user.default,
        timeline=ancestor, post=post, user=user)

        users = ancestor.users.all()
        event.users.add(*users)

        user.ws_sound(post.ancestor)

        return redirect('timeline_app:list-posts', 
        timeline_id=ancestor_id)

class UpdatePost(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)
        return render(request, 'post_app/update-post.html',
        {'post': post, 'form': forms.PostForm(instance=post)})

    def post(self, request, post_id):
        record  = models.Post.objects.get(id=post_id)
        form    = forms.PostForm(request.POST, request.FILES, instance=record)

        if not form.is_valid():
            return render(request, 'post_app/update-post.html',
                   {'post': record, 'form': form}, status=400)
        record.save()

        user  = User.objects.get(id=self.user_id)
        event = EUpdatePost.objects.create(organization=user.default,
        timeline=record.ancestor, post=record, user=user)

        event.users.add(*record.ancestor.users.all())

        # Notify workers of the event, in case the post
        # is on a timeline whose worker is not on.
        event.users.add(*record.workers.all())

        user.ws_sound(record.ancestor)

        return redirect('post_app:post', 
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
        attachments = post.postfilewrapper_set.all()
        form = forms.PostFileWrapperForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, 'post_app/attach-file.html', 
                {'post':post, 'form': form, 'attachments': attachments})
        record = form.save(commit = False)
        record.post = post
        form.save()
        return self.get(request, post_id)

class DetachFile(GuardianView):
    """
    """

    def get(self, request, filewrapper_id):
        filewrapper = PostFileWrapper.objects.get(id=filewrapper_id)
        filewrapper.delete()
        attachments = filewrapper.post.postfilewrapper_set.all()

        form = forms.PostFileWrapperForm()
        return render(request, 'post_app/attach-file.html', 
        {'post':filewrapper.post, 'form': form, 'attachments': attachments})

class DeletePost(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id = post_id)
        # post.delete()

        user  = User.objects.get(id=self.user_id)

        event = EDeletePost.objects.create(organization=user.default,
        timeline=post.ancestor, post_label=post.label, user=user)
        users = post.ancestor.users.all()
        event.users.add(*users)

        ancestor = post.ancestor
        post.delete()

        user.ws_sound(post.ancestor)

        return redirect('timeline_app:list-posts', 
        timeline_id=ancestor.id)

class ListAssignments(GuardianView):
    def get(self, request, user_id):
        user = User.objects.get(id=self.user_id)

        filter, _ = AssignmentFilter.objects.get_or_create(
        user=user, organization=user.default)

        posts      = user.assignments.all()
        total      = posts.count()

        posts      = models.Post.collect_posts(posts, 
        filter.pattern, filter.done) if filter.status \
        else posts.filter(done=False)

        posts = posts.order_by('id')
        count = posts.count()
        elems = JScroll(user.id, 'post_app/list-assignments-scroll.html', posts)

        return render(request, 'post_app/list-assignments.html', 
        {'elems': elems.as_window(), 'user':user, 'total': total, 'count': count})

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
        user = User.objects.get(id=user_id)
        post = models.Post.objects.get(id=post_id)
        me   = User.objects.get(id=self.user_id)

        me.ws_sound(post.ancestor)

        event = EUnassignPost.objects.create(
        organization=me.default, ancestor=post.ancestor, 
        post=post, user=me, peer=user)

        event.users.add(*post.ancestor.users.all())
        
        # As posts can be assigned to users off the timeline.
        # We make sure them get the evvent.
        event.users.add(*post.workers.all())
        event.save()

        post.workers.remove(user)
        post.save()

        return HttpResponse(status=200)

class AssignPostUser(GuardianView):
    def get(self, request, post_id, user_id):
        user = User.objects.get(id=user_id)
        post = models.Post.objects.get(id=post_id)
        me = User.objects.get(id=self.user_id)

        post.workers.add(user)
        post.save()

        event = EAssignPost.objects.create(
        organization=me.default, ancestor=post.ancestor, 
        post=post, user=me, peer=user)

        event.users.add(*post.ancestor.users.all())
        event.users.add(*post.workers.all())
        event.save()

        me.ws_sound(post.ancestor)

        return HttpResponse(status=200)

class ManagePostWorkers(GuardianView):
    def get(self, request, post_id):
        me = User.objects.get(id=self.user_id)
        post = models.Post.objects.get(id=post_id)

        included = post.workers.all()
        excluded = me.default.users.exclude(assignments=post)
        total    = included.count() + excluded.count()

        return render(request, 'post_app/manage-post-workers.html', 
        {'included': included, 'excluded': excluded, 'post': post,
        'count': total, 'total': total, 'me': me, 
        'form':forms.UserSearchForm()})

    def post(self, request, post_id):
        sqlike = User.from_sqlike()
        form = forms.UserSearchForm(request.POST, sqlike=sqlike)

        me = User.objects.get(id=self.user_id)
        post = models.Post.objects.get(id=post_id)
        included = post.workers.all()
        excluded = me.default.users.exclude(assignments=post)
        total    = included.count() + excluded.count()

        if not form.is_valid():
            return render(request, 'post_app/manage-post-workers.html',  
                {'me': me, 'total': total, 'count': 0, 'post': post, 
                    'form':form}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)
        count = included.count() + excluded.count()

        return render(request, 'post_app/manage-post-workers.html', 
        {'included': included, 'excluded': excluded, 'post': post,
        'me': me, 'form':form, 'total': total, 'count': count,})

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

class SetupGlobalPostFilter(GuardianView):
    def get(self, request):
        user   = User.objects.get(id=self.user_id)
        filter = GlobalPostFilter.objects.get(organization=user.default,
        user__id=self.user_id)

        return render(request, 'post_app/setup-global-post-filter.html', 
        {'form': forms.GlobalPostFilterForm(instance=filter)})

    def post(self, request):
        user   = User.objects.get(id=self.user_id)
        record = GlobalPostFilter.objects.get(
        user__id=self.user_id, organization=user.default)

        sqlike = models.Post.from_sqlike()
        form = forms.GlobalPostFilterForm(request.POST, sqlike=sqlike, instance=record)

        if not form.is_valid():
            return render(request, 'post_app/setup-global-post-filter.html',
                   {'form': form}, status=400)
        form.save()
        return redirect('timeline_app:list-all-posts', user_id=user.id)

class CutPost(GuardianView):
    def get(self, request, post_id):
        post          = models.Post.objects.get(id=post_id)
        user          = User.objects.get(id=self.user_id)
        timeline      = post.ancestor

        user.ws_sound(post.ancestor)

        post.ancestor = None
        post.save()

        clipboard, _ = Clipboard.objects.get_or_create(
        user=user, organization=user.default)

        clipboard.posts.add(post)

        event = ECutPost.objects.create(organization=user.default,
        timeline=timeline, post=post, user=user)
        users = timeline.users.all()
        event.users.add(*users)

        return redirect('timeline_app:list-posts', 
        timeline_id=timeline.id)

class CopyPost(GuardianView):
    def get(self, request, post_id):
        post         = models.Post.objects.get(id=post_id)
        user         = User.objects.get(id=self.user_id)
        copy         = post.duplicate()
        clipboard, _ = Clipboard.objects.get_or_create(
        user=user, organization=user.default)
        clipboard.posts.add(copy)

        event = ECopyPost.objects.create(organization=user.default,
        timeline=post.ancestor, post=post, user=user)
        users = post.ancestor.users.all()
        event.users.add(*users)

        user.ws_sound(post.ancestor)

        return redirect('timeline_app:list-posts', 
        timeline_id=post.ancestor.id)

class Done(GuardianView):
    def get(self, request, post_id):
        post      = models.Post.objects.get(id=post_id)
        post.done = True
        post.save()

        user = User.objects.get(id=self.user_id)

        # posts in the clipboard cant be archived.
        event = EArchivePost.objects.create(organization=user.default,
        timeline=post.ancestor, post=post, user=user)

        users = post.ancestor.users.all()
        event.users.add(*users)

        user.ws_sound(post.ancestor)

        return redirect('post_app:post', 
        post_id=post.id)

class ManagePostTags(GuardianView):
    def get(self, request, post_id):
        me = User.objects.get(id=self.user_id)
        post = models.Post.objects.get(id=post_id)

        included = post.tags.all()
        excluded = me.default.tags.exclude(posts=post)

        return render(request, 'post_app/manage-post-tags.html', 
        {'included': included, 'excluded': excluded, 'post': post,
        'organization': me.default,'form':forms.TagSearchForm()})

    def post(self, request, post_id):
        sqlike = Tag.from_sqlike()
        form = forms.TagSearchForm(request.POST, sqlike=sqlike)

        me = User.objects.get(id=self.user_id)
        post = models.Post.objects.get(id=post_id)
        included = post.tags.all()
        excluded = me.default.tags.exclude(posts=post)

        if not form.is_valid():
            return render(request, 'post_app/manage-post-tags.html', 
                {'included': included, 'excluded': excluded,
                    'organization': me.default, 'post': post,
                        'form':form}, status=400)

        included = sqlike.run(included)
        excluded = sqlike.run(excluded)

        return render(request, 'post_app/manage-post-tags.html', 
        {'included': included, 'excluded': excluded, 'post': post,
        'me': me, 'organization': me.default,'form':form})

class UnbindPostTag(GuardianView):
    def get(self, request, post_id, tag_id):
        tag = Tag.objects.get(id=tag_id)
        post = models.Post.objects.get(id=post_id)
        post.tags.remove(tag)
        post.save()

        me = User.objects.get(id=self.user_id)

        event = EUnbindTagPost.objects.create(
        organization=me.default, ancestor=post.ancestor, 
        post=post, tag=tag, user=me)
        event.users.add(*post.ancestor.users.all())
        event.save()

        me.ws_sound(post.ancestor)

        return HttpResponse(status=200)

class BindPostTag(GuardianView):
    def get(self, request, post_id, tag_id):
        tag = Tag.objects.get(id=tag_id)
        post = models.Post.objects.get(id=post_id)
        post.tags.add(tag)
        post.save()

        me = User.objects.get(id=self.user_id)

        event = EBindTagPost.objects.create(
        organization=me.default, ancestor=post.ancestor, 
        post=post, tag=tag, user=me)
        event.users.add(*post.ancestor.users.all())
        event.save()

        me.ws_sound(post.ancestor)

        return HttpResponse(status=200)

class CancelPostCreation(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id = post_id)
        post.delete()

        return HttpResponse(status=200)

class Undo(GuardianView):
    def get(self, request, post_id):
        post      = models.Post.objects.get(id=post_id)
        post.done = False
        post.save()

        user = User.objects.get(id=self.user_id)

        user.ws_sound(post.ancestor)

        return redirect('post_app:post', 
        post_id=post.id)


class RequestPostAttention(GuardianView):
    def get(self, request, peer_id, post_id):
        peer = User.objects.get(id=peer_id)
        post = models.Post.objects.get(id=post_id)

        form = forms.PostAttentionForm()
        return render(request, 'post_app/request-post-attention.html', 
        {'peer': peer,  'post': post, 'form': form})

    def post(self, request, peer_id, post_id):
        user = User.objects.get(id=self.user_id)
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
        user.name, user.email, url, form.cleaned_data['message'])

        send_mail('%s %s' % (user.default.name, 
        user.name), msg, user.email, [peer.email], fail_silently=False)

        return redirect('post_app:post-worker-information', 
        peer_id=peer.id, post_id=post.id)

class AlertPostWorkers(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)
        user = User.objects.get(id=self.user_id)

        form = forms.AlertPostWorkersForm()
        return render(request, 'post_app/alert-post-workers.html', 
        {'post': post, 'form': form, 'user': user})

    def post(self, request, post_id):
        user = User.objects.get(id=self.user_id)
        post = models.Post.objects.get(id=post_id)
        form = forms.AlertPostWorkersForm(request.POST)

        if not form.is_valid():
            return render(request,'post_app/alert-post-workers.html', 
                    {'user': user, 'post': post, 'form': form})    

        url  = reverse('post_app:post-link', 
        kwargs={'post_id': post.id})

        url = '%s%s' % (settings.LOCAL_ADDR, url)
        msg = '%s (%s) has alerted you on\n%s\n\n%s' % (
        user.name, user.email, url, form.cleaned_data['message'])

        for ind in post.workers.values_list('email'):
            send_mail('%s %s' % (user.default.name, 
                user.name), msg, user.email, 
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
        user = User.objects.get(id=self.user_id)
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
        user = User.objects.get(id=self.user_id)

        event.post.ancestor = event.timeline
        event.post.save()

        event1 = EPastePost(organization=user.default, 
        timeline=event.timeline, user=user)

        event1.save(hcache=False)
        event1.posts.add(event.post)
        event1.users.add(*event.timeline.users.all())
        event1.save()
        
        clipboard, _ = Clipboard.objects.get_or_create(
        user=user, organization=user.default)

        clipboard.posts.remove(event.post)

class SetupAssignmentFilter(GuardianView):
    def get(self, request):
        user = User.objects.get(id=self.user_id)

        filter = AssignmentFilter.objects.get(
        user__id=self.user_id, organization=user.default)

        return render(request, 'post_app/setup-assignment-filter.html', 
        {'form': forms.AssignmentFilterForm(instance=filter), 
        'user': user})

    def post(self, request):
        user = User.objects.get(id=self.user_id)

        record = AssignmentFilter.objects.get(
        user__id=self.user_id, organization=user.default)

        sqlike = models.Post.from_sqlike()
        form = forms.AssignmentFilterForm(request.POST, sqlike=sqlike, instance=record)

        if not form.is_valid():
            return render(request, 'post_app/setup-assignment-filter.html',
                   {'user': user, 'form': form}, status=400)
        form.save()
        return redirect('post_app:list-assignments', user_id=user.id)


class PullCardContent(GuardianView):
    """
    """

    def get(self, request, post_id, fork_id=None):
        post       = models.Post.objects.get(id=post_id)
        user       = User.objects.get(id=self.user_id)
        fork       = Card.objects.get(id=fork_id)

        fork.label = post.label
        fork.data  = post.data
        # fork.save()
        form       = CardForm(instance=fork)

        return render(request, 'post_app/create-fork.html', 
        {'form':form, 'post': post, 'ancestor': fork.ancestor, 'card':fork})

class CreateCardFork(GuardianView):
    """
    """

    def get(self, request, ancestor_id, post_id, fork_id=None):
        post = models.Post.objects.get(id=post_id)
        user = User.objects.get(id=self.user_id)
        ancestor = List.objects.get(id=ancestor_id)
        fork = Card.objects.create(owner=user, 
        ancestor=ancestor, parent_post=post)

        form = CardForm(instance=fork)
        fork.label = 'Draft.'

        # path = post.path.all()
        fork.parent_post = post
        # fork.path.add(*path, post)
        fork.save()

        return render(request, 'post_app/create-fork.html', 
        {'form':form, 'post': post, 'ancestor': ancestor, 'card':fork})

    def post(self, request, ancestor_id, post_id, fork_id):
        post = models.Post.objects.get(id=post_id)
        fork = Card.objects.get(id=fork_id)
        form = CardForm(request.POST, instance=fork)
        user = User.objects.get(id=self.user_id)

        if not form.is_valid():
            return render(request, 'post_app/create-fork.html', 
                {'form':form, 'ancestor': post.ancestor, 
                    'post': post, 'card':fork}, status=400)

        fork.save()

        event = models.ECreateCardFork.objects.create(organization=user.default,
        ancestor=post.ancestor, post=post, card=fork, user=user)

        # The timeline users and the board users get the event.
        event.users.add(*post.ancestor.users.all())
        event.users.add(*fork.ancestor.ancestor.members.all())

        # In this case, it would play sound twice if you're
        # in both timeline and board.
        user.ws_sound(fork.ancestor.ancestor)
        user.ws_sound(post.ancestor)

        return redirect('card_app:view-data', card_id=fork.id)

class SelectForkList(GuardianView):
    def get(self, request, post_id):
        user = User.objects.get(id=self.user_id)
        post = models.Post.objects.get(id=post_id)
        form = ListSearchform()
        lists = List.objects.filter(ancestor__in=user.boards.all())

        return render(request, 'post_app/select-fork-list.html', 
        {'form':form, 'post': post, 'elems': lists})

    def post(self, request, post_id):
        form = forms.ListSearchform(request.POST)
        post = models.Post.objects.get(id=post_id)

        user  = User.objects.get(id=self.user_id)
        lists = List.objects.filter(ancestor__in=user.boards.all())

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

        rule = Q(eunbindtagpost__post__id= post.id) | \
        Q(ecreatepost__post__id=post.id) | Q(eupdatepost__post__id= post.id) | \
        Q(eassignpost__post__id=post.id) | \
        Q(ebindtagpost__post__id= post.id) | Q(eunassignpost__post__id= post.id)| \
        Q(ecutpost__post__id = post.id) | Q(earchivepost__post__id=post.id) |\
        Q(ecopypost__post__id=post.id) | Q(ecreatepostfork__post__id=post.id) | \
        Q(epastepost__posts=post.id)
    
        events = Event.objects.filter(rule).order_by('-created').values('html')

        return render(request, 'post_app/post-events.html', 
        {'post': post, 'elems': events})













