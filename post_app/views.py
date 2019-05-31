from post_app.models import EUnbindTagPost, ECreatePost, EUpdatePost, \
PostFileWrapper, EDeletePost, EBindTagPost, ELikePost, EUnlikePost, \
PostFilter, PostSearch, ECutPost, EArchivePost, ECopyPost, \
EUnarchivePost, PostPin, PostTagship
from post_app.sqlikes import SqPost
from django.db.models import Q, F, Exists, OuterRef, Count, Sum
from core_app.models import Clipboard, Tag, User, Event
from core_app.sqlikes import SqUser, SqTag
from django.db.models.functions import Concat
from django.shortcuts import render, redirect
from core_app.views import GuardianView, FileDownload
from django.urls import reverse
from django.views.generic import View
from django.core.mail import send_mail
from django.http import HttpResponse
from list_app.models import List
from group_app.models import Group, EPastePost
from django.conf import settings
from jscroll.wrappers import JScroll
from card_app.models import Card
from django.db import transaction
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
        post = models.Post.locate(self.me, self.me.default, post_id)
        boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        listpins  = self.me.listpin_set.filter(organization=self.me.default)
        cardpins  = self.me.cardpin_set.filter(organization=self.me.default)
        grouppins = self.me.grouppin_set.filter(organization=self.me.default)
        postpins  = self.me.postpin_set.filter(organization=self.me.default)

        return render(request, 'post_app/post.html', 
        {'post':post, 'boardpins': boardpins, 'listpins': listpins, 
        'cardpins': cardpins, 'tags': post.tags.all(), 
        'grouppins': grouppins, 'postpins': postpins, 'user': self.me, })

class PostLink(GuardianView):
    """
    This view worksk alike like Post in terms of permissions.
    """

    def get(self, request, post_id):
        post = models.Post.locate(self.me, self.me.default, post_id)
        organizations = self.me.organizations.exclude(id=self.me.default.id)

        boardpins = self.me.boardpin_set.filter(organization=self.me.default)
        listpins = self.me.listpin_set.filter(organization=self.me.default)
        cardpins = self.me.cardpin_set.filter(organization=self.me.default)
        grouppins = self.me.grouppin_set.filter(organization=self.me.default)

        return render(request, 'post_app/post-link.html', 
        {'post':post, 'boardpins': boardpins, 'listpins': listpins, 
        'grouppins': grouppins, 'cardpins': cardpins, 'user': self.me, 
        'default': self.me.default, 'organization': self.me.default, 
        'organizations': organizations, 'settings': settings})

class CreatePost(GuardianView):
    """
    The logged user can create a post on the group just if his default organization
    contains the group and he belongs to the group.
    """

    def get(self, request, ancestor_id):
        ancestor   = self.me.groups.get(id=ancestor_id, 
        organization=self.me.default)

        form = forms.PostForm()

        return render(request, 'post_app/create-post.html', 
        {'form':form, 'ancestor':ancestor})

    def post(self, request, ancestor_id):
        ancestor   = self.me.groups.get(id=ancestor_id, 
        organization=self.me.default)

        groupship = self.me.user_groupship.get(group=ancestor)
        if groupship.status == '2' and not ancestor.open:
            return HttpResponse("The group is not opened, you're a guest\
                you can't create posts!", status=403)

        form = forms.PostForm(request.POST, request.FILES)
        print('fooo')

        if not form.is_valid():
            return render(request, 'post_app/create-post.html',
                        {'form': form, 'ancestor': ancestor}, status=400)

        post          = form.save(commit=False)
        post.owner     = self.me
        post.ancestor = ancestor
        post.save()

        event = ECreatePost.objects.create(organization=self.me.default,
        group=ancestor, post=post, user=self.me)

        users = ancestor.users.all()
        event.dispatch(*users)

        return redirect('group_app:list-posts', 
        group_id=ancestor_id)

class UpdatePost(GuardianView):
    """
    """

    def get(self, request, post_id):
        post = models.Post.locate(self.me, self.me.default, post_id)

        return render(request, 'post_app/update-post.html',
        {'post': post, 'form': forms.PostForm(instance=post)})

    def post(self, request, post_id):
        record = models.Post.locate(self.me, self.me.default, post_id)

        groupship = self.me.user_groupship.get(group=record.ancestor)
        if groupship.status == '2' and not record.ancestor.open:
            return HttpResponse("The group is not opened, you're a guest\
                you can't update posts!", status=403)

        form = forms.PostForm(request.POST, request.FILES, instance=record)
        if not form.is_valid():
            return render(request, 'post_app/update-post.html',
                   {'post': record, 'form': form}, status=400)

        record.save()

        event = EUpdatePost.objects.create(organization=self.me.default,
        group=record.ancestor, post=record, user=self.me, post_label=record.label,
        post_data=record.data, post_html=record.html)

        event.dispatch(*record.ancestor.users.all())

        return redirect('post_app:refresh-post', 
        post_id=record.id)


class AttachFile(GuardianView):
    """
    It follows the same permission scheme for update-post view.
    """

    def get(self, request, post_id):
        post = models.Post.locate(self.me, self.me.default, post_id)

        attachments = post.postfilewrapper_set.all()
        form = forms.PostFileWrapperForm()
        return render(request, 'post_app/attach-file.html', 
        {'post':post, 'form': form, 'attachments': attachments})

    def post(self, request, post_id):
        post = models.Post.locate(self.me, self.me.default, post_id)
        attachments = post.postfilewrapper_set.all()

        form = forms.PostFileWrapperForm(request.POST, 
        request.FILES, user=self.me)

        if not form.is_valid():
            return render(request, 'post_app/attach-file.html', 
                {'post':post, 'form': form, 'attachments': attachments})

        record = form.save(commit = False)
        record.organization = self.me.default
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
    The same permission scheme for attach-file view.
    """

    def get(self, request, filewrapper_id):
        filewrapper = PostFileWrapper.objects.filter(
        Q(post__ancestor__users=self.me), id=filewrapper_id, 
        post__ancestor__organization=self.me.default)

        filewrapper = filewrapper.distinct().first()
        attachments = filewrapper.post.postfilewrapper_set.all()

        groupship = self.me.user_groupship.get(group=filewrapper.post.ancestor)
        if groupship.status == '2':
            return HttpResponse("You're a group guest,\
                you can't dettach post files!", status=403)

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
    """
    The same permission scheme for update-post view.
    """

    def post(self, request, post_id):
        post = models.Post.locate(self.me, self.me.default, post_id)
        groupship = self.me.user_groupship.get(group=post.ancestor)
        if groupship.status == '2':
            return HttpResponse("Group guests can't delete posts!", status=403)

        event = EDeletePost.objects.create(organization=self.me.default,
        group=post.ancestor, post_label=post.label, user=self.me)
        users = post.ancestor.users.all()
        event.dispatch(*users)

        ancestor = post.ancestor
        post.delete()

        return redirect('group_app:list-posts', group_id=ancestor.id)

class PostTagInformation(GuardianView):
    """
    """

    def get(self, request, tag_id, post_id):
        post    = models.Post.locate(self.me, self.me.default, post_id)
        tag     = Tag.objects.get(id=tag_id, organization=self.me.default)
        tagship = models.PostTagship.objects.get(post=post, tag=tag)

        return render(request, 'post_app/post-tag-information.html', 
        {'tagger': tagship.tagger, 'created': tagship.created, 'tag':tag})


class SetupPostFilter(GuardianView):
    """
    Makes sure the user can have a filter only if he belongs
    to the group in fact. 

    Notice that when the user is removed from the group the 
    filter remains in the db.
    """

    def get(self, request, group_id):
        group = self.me.groups.get(id=group_id, 
        organization=self.me.default)

        filter = PostFilter.objects.get(
        user__id=self.user_id, group__id=group_id)

        return render(request, 'post_app/setup-post-filter.html', 
        {'form': forms.PostFilterForm(instance=filter), 'group': group})

    def post(self, request, group_id):
        record = PostFilter.objects.get(
        group__id=group_id, user__id=self.user_id)

        sqlike = SqPost()
        form   = forms.PostFilterForm(
        request.POST, sqlike=sqlike, instance=record)

        group = self.me.groups.get(id=group_id, 
        organization=self.me.default)

        if not form.is_valid():
            return render(request, 'post_app/setup-post-filter.html',
                   {'group': record, 'form': form}, status=400)
        form.save()

        return redirect('group_app:list-posts', group_id=group.id)

class Find(GuardianView):
    """
    This view is already secured for default due to the way of how
    it is implemented.
    """

    def get(self, request):
        filter, _ = PostSearch.objects.get_or_create(
        user=self.me, organization=self.me.default)

        form   = forms.PostSearchForm(instance=filter)
        q0     = Q(ancestor__organization=self.me.default)
        q1     = Q(ancestor__users=self.me) 
        posts  = models.Post.objects.filter(q0 & q1)

        posts  = posts.distinct()
        total  = posts.count()
        sqlike = SqPost()
        posts  = filter.get_partial(posts)

        sqlike.feed(filter.pattern)

        posts = sqlike.run(posts)
        count = posts.count()
        posts = posts.only('done', 'label', 'id').order_by('id')
        elems = JScroll(self.me.id, 'post_app/find-scroll.html', posts)

        return render(request, 'post_app/find.html', {'form': form, 
        'elems':  elems.as_div(), 'total': total, 'count': count})

    def post(self, request):
        filter, _ = PostSearch.objects.get_or_create(
        user=self.me, organization=self.me.default)

        sqlike = SqPost()
        form   = forms.PostSearchForm(
        request.POST, sqlike=sqlike, instance=filter)

        q0     = Q(ancestor__organization=self.me.default)
        q1     = Q(ancestor__users=self.me) 
        posts  = models.Post.objects.filter(q0 & q1)

        posts  = posts.distinct()
        total  = posts.count()

        if not form.is_valid():
            return render(request, 'post_app/find.html', 
                {'form': form, 'total': total, 'count': 0}, status=400)
        form.save()

        posts = filter.get_partial(posts)
        posts = sqlike.run(posts)

        count = posts.count()
        posts = posts.only('done', 'label', 'id').order_by('id')
        elems = JScroll(self.me.id, 'post_app/find-scroll.html', posts)

        return render(request, 'post_app/find.html', {'form': form, 
        'elems':  elems.as_div(), 'total': total, 'count': count})

class CutPost(GuardianView):
    """
    Same as in update-post view permission scheme.
    """

    def post(self, request, post_id):
        post = models.Post.locate(self.me, self.me.default, post_id)

        groupship = self.me.user_groupship.get(group=post.ancestor)
        if groupship.status == '2':
            return HttpResponse("Group guests can't cut posts!", status=403)

        group = post.ancestor


        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)

        post.ancestor = None
        post.priority = clipboard.posts.count() + 1
        post.save()

        clipboard.posts.add(post)

        event = ECutPost.objects.create(organization=self.me.default,
        group=group, post=post, user=self.me)
        users = group.users.all()
        event.dispatch(*users)

        return redirect('group_app:list-posts', 
        group_id=group.id)

class CopyPost(GuardianView):
    """
    Same as in CutPost view.
    """

    def post(self, request, post_id):
        post = models.Post.locate(self.me, self.me.default, post_id)

        groupship = self.me.user_groupship.get(group=post.ancestor)
        if groupship.status == '2':
            return HttpResponse("Group guests can't copy posts!", status=403)

        copy = post.duplicate()
        clipboard, _ = Clipboard.objects.get_or_create(
        user=self.me, organization=self.me.default)

        copy.priority = clipboard.posts.count() + 1
        copy.save()

        clipboard.posts.add(copy)

        event = ECopyPost.objects.create(organization=self.me.default,
        group=post.ancestor, post=post, user=self.me)
        users = post.ancestor.users.all()
        event.dispatch(*users)

        return redirect('group_app:list-posts', 
        group_id=post.ancestor.id)

class Done(GuardianView):
    """
    Same as in copy-post view.
    """

    def get(self, request, post_id):
        post = models.Post.locate(self.me, self.me.default, post_id)
        groupship = self.me.user_groupship.get(group=post.ancestor)
        if groupship.status == '2':
            return HttpResponse("Group guests can't archive posts!", status=403)

        can_archive = all(post.card_forks.values_list('done', flat=True))
        if not can_archive:
            return HttpResponse("It has unarchived forks\
                    cards. Can't archive it now", status=403)

        post.done = True
        post.save()

        # posts in the clipboard cant be archived.
        event = EArchivePost.objects.create(organization=self.me.default,
        group=post.ancestor, post=post, user=self.me)

        users = post.ancestor.users.all()
        event.dispatch(*users)

        return redirect('post_app:refresh-post', 
        post_id=post.id)


class Undo(GuardianView):
    """
    Same as in update-post view.
    """

    def get(self, request, post_id):
        post = models.Post.locate(self.me, self.me.default, post_id)
        groupship = self.me.user_groupship.get(group=post.ancestor)
        if groupship.status == '2':
            return HttpResponse("Group guests can't unarchive posts!", status=403)

        post.done = False
        post.save()
        event = EUnarchivePost.objects.create(organization=self.me.default,
        group=post.ancestor, post=post, user=self.me)

        users = post.ancestor.users.all()
        event.dispatch(*users)

        return redirect('post_app:refresh-post', 
        post_id=post.id)

class ConfirmPostDeletion(GuardianView):
    """
    It enforces his default organization contains the post's group
    as well.
    """

    def get(self, request, post_id):
        post = models.Post.locate(self.me, self.me.default, post_id)

        return render(request, 'post_app/confirm-post-deletion.html', 
        {'post': post})


class PullCardContent(GuardianView):
    """
    The user has to be related to the post either by
    belonging to the group/being a worker. 

    The user has to be in the list's board that the 
    post is forked into as well.
    """

    def get(self, request, ancestor_id, post_id):
        # Make sure i belong to the board and the board belongs
        # to my default organization.
        ancestor = List.objects.get(id=ancestor_id, 
        ancestor__organization=self.me.default, 
        ancestor__members=self.me)

        post = models.Post.locate(self.me, self.me.default, post_id)
        form = CardForm(initial={'label': post.label, 'data': post.data})

        return render(request, 'post_app/create-fork.html', 
        {'form':form, 'post': post, 'ancestor': ancestor})

class CreatePostFork(GuardianView):
    """
    """

    def get(self, request, ancestor_id, post_id):
        post = models.Post.locate(self.me, self.me.default, post_id)
        ancestor = List.objects.get(id=ancestor_id)
        form = CardForm()

        return render(request, 'post_app/create-fork.html', 
        {'form':form, 'post': post, 'ancestor': ancestor})

    def post(self, request, ancestor_id, post_id):
        ancestor = List.objects.get(id=ancestor_id, 
        ancestor__organization=self.me.default, 
        ancestor__members=self.me)

        post = models.Post.locate(self.me, self.me.default, post_id)
        form = CardForm(request.POST)

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

        event = models.ECreatePostFork.objects.create(organization=self.me.default,
        group=post.ancestor, list=fork.ancestor, post=post, card=fork, 
        board=fork.ancestor.ancestor, user=self.me)

        # The group users and the board users get the event.
        event.dispatch(*post.ancestor.users.all(), 
        *fork.ancestor.ancestor.members.all())

        return redirect('card_app:view-data', card_id=fork.id)

class SelectForkList(GuardianView):
    """
    The user is supposed to view the dialog just if matches
    the same permission criterea in create-fork view view.
    """

    def get(self, request, post_id):
        post = models.Post.locate(self.me, self.me.default, post_id)

        form = ListSearchform()

        boards = self.me.boards.filter(organization=self.me.default)
        lists  = List.objects.filter(ancestor__in=boards)

        return render(request, 'post_app/select-fork-list.html', 
        {'form':form, 'post': post, 'elems': lists})

    def post(self, request, post_id):
        sqlike = List.from_sqlike()
        form = forms.ListSearchform(request.POST, sqlike=sqlike)

        post = models.Post.locate(self.me, self.me.default, post_id)

        if not form.is_valid():
            return render(request, 'post_app/select-fork-list.html', 
                  {'form':form, 'post': post})

        boards = self.me.boards.filter(organization=self.me.default)
        lists  = List.objects.filter(ancestor__in=boards)
        lists  = sqlike.run(lists)

        return render(request, 'post_app/select-fork-list.html', 
        {'form':form, 'post': post, 'elems': lists})

class PostEvents(GuardianView):
    def get(self, request, post_id):
        post = models.Post.locate(self.me, self.me.default, post_id)

        query = Q(eunbindtagpost__post__id= post.id) |\
        Q(ecreatepost__post__id=post.id) | Q(eupdatepost__post__id= post.id) |\
        Q(elikepost__post__id=post.id) | Q(ebindtagpost__post__id= post.id) |\
        Q(ecutpost__post__id = post.id) | Q(earchivepost__post__id=post.id) |\
        Q(ecopypost__post__id=post.id) | Q(ecreatepostfork__post__id=post.id) | \
        Q(epastepost__posts=post.id) | Q(ecreatecomment__child__id=post.id) | \
        Q(eupdatecomment__child__id=post.id) | Q(edeletecomment__child__id=post.id) |\
        Q(eattachcommentfile__comment__post__id=post.id) | \
        Q(eattachpostfile__post__id=post.id) | \
        Q(edettachpostfile__post__id=post.id) | \
        Q(edettachcommentfile__comment__post__id=post.id)|\
        Q(esetpostpriorityup__post0__id=post.id)|\
        Q(esetpostprioritydown__post0__id=post.id)|\
        Q(esetpostpriorityup__post1__id=post.id)|\
        Q(esetpostprioritydown__post1__id=post.id)|\
        Q(erestorepost__post__id=post.id)|\
        Q(eunarchivepost__post__id=post.id)|\
        Q(erestorecomment__post__id=post.id)

        events = Event.objects.filter(query).order_by('-created').values('html')
        count = events.count()

        return render(request, 'post_app/post-events.html', 
        {'post': post, 'elems': events, 'count': count})


class PinPost(GuardianView):
    def get(self, request, post_id):
        post = models.Post.locate(self.me, self.me.default, post_id)

        pin   = PostPin.objects.create(user=self.me, 
        organization=self.me.default, post=post)
        return redirect('board_app:list-pins')

class Unpin(GuardianView):
    def get(self, request, pin_id):
        pin = self.me.postpin_set.get(id=pin_id)
        pin.delete()
        return redirect('board_app:list-pins')

class RefreshPost(GuardianView):
    """
    Used to update a post view after changing its data.
    """

    def get(self, request, post_id):
        post = models.Post.locate(self.me, self.me.default, post_id)

        # Some workaround to not need to rewrite the post_app/post-data.html template.
        post.in_likers = post.likes.filter(id=self.me.id).exists()
        return render(request, 'post_app/post-data.html', 
        {'post':post, 'tags': post.tags.all(), 'user': self.me, })


class PostPriority(GuardianView):
    def get(self, request, post_id):
        post  = models.Post.locate(self.me, self.me.default, post_id)
        posts = post.ancestor.posts.filter(done=False)
        posts = posts.order_by('-priority')
        total = posts.count()

        return render(request, 'post_app/post-priority.html', 
        {'post': post, 'total': total, 'count': total, 'me': self.me,
        'posts': posts, 'form': forms.PostPriorityForm()})

    def post(self, request, post_id):
        sqlike = SqPost()
        post   = models.Post.locate(self.me, self.me.default, post_id)
        posts  = post.ancestor.posts.filter(done=False)
        total  = posts.count()
        form   = forms.PostPriorityForm(request.POST, sqlike=sqlike)

        if not form.is_valid():
            return render(request, 'post_app/post-priority.html', 
                {'me': self.me, 'organization': self.me.default, 'post': post,
                     'total': total, 'count': 0, 'form':form}, status=400)

        posts = sqlike.run(posts)
        posts = posts.order_by('-priority')

        count = posts.count()

        return render(request, 'post_app/post-priority.html', 
        {'post': post, 'total': total, 'count': count, 'me': self.me,
        'posts': posts, 'form': form})

class SetPostPriorityUp(GuardianView):
    @transaction.atomic
    def get(self, request, post0_id, post1_id):
        post0  = models.Post.locate(self.me, self.me.default, post0_id)
        post1  = models.Post.locate(self.me, self.me.default, post1_id)
        dir    = -1 if post0.priority < post1.priority else 1
        flag   = 0 if post0.priority <= post1.priority else 1

        q0     = Q(priority__lte=post1.priority, priority__gt=post0.priority)
        q1     = Q(priority__gt=post1.priority, priority__lt=post0.priority)
        query  = q0 if post0.priority < post1.priority else q1
        posts  = post0.ancestor.posts.filter(query)

        posts.update(priority=F('priority') + dir)
        post0.priority = post1.priority + flag
        post0.save()

        event = models.ESetPostPriorityUp.objects.create(organization=self.me.default,
        ancestor=post0.ancestor, post0=post0, post1=post1, user=self.me)

        event.dispatch(*post0.ancestor.users.all())
        print('Priority', [[ind.label, ind.priority] for ind in post0.ancestor.posts.all().order_by('-priority')])

        return redirect('group_app:list-posts', group_id=post0.ancestor.id)

class SetPostPriorityDown(GuardianView):
    @transaction.atomic
    def get(self, request, post0_id, post1_id):
        post0  = models.Post.locate(self.me, self.me.default, post0_id)
        post1  = models.Post.locate(self.me, self.me.default, post1_id)
        dir    = -1 if post0.priority < post1.priority else 1
        flag   = -1 if post0.priority < post1.priority else 0

        q0     = Q(priority__lt=post1.priority, priority__gt=post0.priority)
        q1     = Q(priority__gte=post1.priority, priority__lt=post0.priority)
        query  =  q0 if post0.priority < post1.priority else q1
        posts  = post0.ancestor.posts.filter(query)

        posts.update(priority=F('priority') + dir)
        post0.priority = post1.priority + flag
        post0.save()

        event = models.ESetPostPriorityDown.objects.create(organization=self.me.default,
        ancestor=post0.ancestor, post0=post0, post1=post1, user=self.me)


        event.dispatch(*post0.ancestor.users.all())
        print('Priority', [[ind.label, ind.priority] for ind in post0.ancestor.posts.all().order_by('-priority')])

        return redirect('group_app:list-posts', group_id=post0.ancestor.id)

class PostFileDownload(FileDownload):
    def get(self, request, filewrapper_id):
        filewrapper = PostFileWrapper.objects.filter(
        Q(post__ancestor__users=self.me),
        id=filewrapper_id, post__ancestor__organization=self.me.default)
        filewrapper = filewrapper.distinct().first()

        return self.get_file_url(filewrapper.file)

class LikePost(GuardianView):
    def post(self, request, post_id):
        post = models.Post.locate(self.me, self.me.default, post_id)
        post.likes.add(self.me)

        event = ELikePost.objects.create(organization=self.me.default, 
        ancestor=post.ancestor, post=post, user=self.me)

        event.dispatch(*post.ancestor.users.all())
        event.save()

        return redirect('post_app:refresh-post', post_id=post.id)

class UnlikePost(GuardianView):
    def post(self, request, post_id):
        post = models.Post.locate(self.me, self.me.default, post_id)
        post.likes.remove(self.me)

        event = EUnlikePost.objects.create(organization=self.me.default, 
        ancestor=post.ancestor, post=post, user=self.me)

        event.dispatch(*post.ancestor.users.all())
        event.save()

        return redirect('post_app:refresh-post', post_id=post.id)

class UnbindPostTags(GuardianView):
    """
    """

    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)
        included = post.tags.all()
        total    = included.count() 

        return render(request, 'post_app/unbind-post-tags.html', {
        'included': included, 'post': post, 'organization': self.me.default,
        'form':forms.TagSearchForm(), 'me': self.me, 
        'count': total, 'total': total,})

    def post(self, request, post_id):
        sqlike   = SqTag()
        form     = forms.TagSearchForm(request.POST, sqlike=sqlike)
        post     = models.Post.objects.get(id=post_id)
        included = post.tags.all()
        tags     = self.me.default.tags.all()
        total    = included.count() 
        
        if not form.is_valid():
            return render(request, 'post_app/unbind-post-tags.html', 
                {'me': self.me, 'post': post, 'count': 0, 'total': total,
                        'form':form}, status=400)

        included = sqlike.run(included)
        count = included.count() 

        return render(request, 'post_app/unbind-post-tags.html', 
        {'included': included, 'post': post, 'me': self.me, 
        'organization': self.me.default,'form':form, 
        'count': count, 'total': total,})

class BindPostTags(GuardianView):
    """
    The listed tags are supposed to belong to the logged tag default
    organization. It also checks if the tag belongs to the post
    in order to list its tags.
    """

    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)

        tags  = self.me.default.tags.all()
        excluded = tags.exclude(posts=post)
        total    = excluded.count()

        return render(request, 'post_app/bind-post-tags.html', 
        {'excluded': excluded, 'post': post, 'me': self.me, 
        'organization': self.me.default,'form':forms.TagSearchForm(), 
        'count': total, 'total': total,})

    def post(self, request, post_id):
        sqlike   = SqTag()
        form     = forms.TagSearchForm(request.POST, sqlike=sqlike)
        post     = models.Post.objects.get(id=post_id)
        tags     = self.me.default.tags.all()
        excluded = tags.exclude(posts=post)

        total = excluded.count()
        
        if not form.is_valid():
            return render(request, 'post_app/bind-post-tags.html', 
                {'me': self.me, 'post': post, 'count': 0, 'total': total,
                        'form':form}, status=400)

        excluded = sqlike.run(excluded)
        count = excluded.count()

        return render(request, 'post_app/bind-post-tags.html', 
        {'excluded': excluded, 'post': post, 'me': self.me, 
        'organization': self.me.default,'form':form, 
        'count': count, 'total': total,})

class CreatePostTagship(GuardianView):
    """
    """

    def get(self, request, post_id, tag_id):
        tag  = Tag.objects.get(id=tag_id, organization=self.me.default)
        post = models.Post.objects.get(id=post_id)
        form  = forms.PostTagshipForm()

        return render(request, 'post_app/create-post-tagship.html', {
        'tag': tag, 'post': post, 'form': form})

    def post(self, request, post_id, tag_id):
        tag  = Tag.objects.get(id=tag_id, organization=self.me.default)
        post = models.Post.objects.get(id=post_id)

        form = forms.PostTagshipForm(request.POST)
        if not form.is_valid():
            return render(request, 'post_app/create-post-tagship.html', {
                'tag': tag, 'post': post, 'form': form})

        record        = form.save(commit=False)
        record.tag   = tag
        record.tagger = self.me
        record.post  = post
        record.save()

        event = EBindTagPost.objects.create(
        organization=self.me.default, ancestor=post.ancestor, 
        post=post, tag=tag, user=self.me)
        event.dispatch(*post.ancestor.users.all())
        event.save()



        return redirect('post_app:bind-post-tags', post_id=post.id)

class DeletePostTagship(GuardianView):
    def post(self, request, post_id, tag_id):
        tag  = Tag.objects.get(id=tag_id, organization=self.me.default)
        post = models.Post.objects.get(id=post_id)

        event = EUnbindTagPost.objects.create(
        organization=self.me.default, ancestor=post.ancestor, 
        post=post, tag=tag, user=self.me)
        event.dispatch(*post.ancestor.users.all())
        event.save()

        PostTagship.objects.get(post=post, tag=tag).delete()
        return redirect('post_app:unbind-post-tags', post_id=post.id)

class PostDiff(GuardianView):
    def get(self, request, event_id):
        event = EUpdatePost.objects.get(id=event_id)
        post = models.Post.locate(self.me, self.me.default, event.post.id)

        return render(request, 'post_app/post-diff.html', 
        {'post': post, 'event': event})

class RestorePost(GuardianView):
    def post(self, request, event_id):
        event = EUpdatePost.objects.get(id=event_id)
        post  = models.Post.locate(self.me, self.me.default, event.post.id)

        groupship = self.me.user_groupship.get(group=post.ancestor)
        error    = "The group is not opened, you're a guest\
        you can't update posts!"

        if groupship.status == '2' and not post.ancestor.open:
            return HttpResponse(error, status=403)

        post.label = event.post_label
        post.data = event.post_data
        post.save()

        event = models.ERestorePost.objects.create(
        event_html=event.html, organization=self.me.default, 
        ancestor=post.ancestor,post=post, user=self.me)

        event.dispatch(*post.ancestor.users.all())
        event.save()
        return redirect('post_app:post', post_id=post.id)






