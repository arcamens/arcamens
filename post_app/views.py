from django.views.generic import View
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from timeline_app.views import GuardianView
import timeline_app.models
import core_app.models
from . import forms
from . import models
from core_app import ws
from core_app.models import User

class Post(GuardianView):
    """
    """

    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)

        if not post.ancestor:
            return HttpResponse("This post is on clipboard!\
                It can't be accessed now.", status=400)

        attachments = post.postfilewrapper_set.all()
        workers = post.workers.all()
        return render(request, 'post_app/post.html', 
        {'post':post, 'attachments': attachments, 
        'tags': post.tags.all(), 'workers': workers})

class CreatePost(GuardianView):
    """
    """

    def get(self, request, ancestor_id, post_id=None):
        ancestor = timeline_app.models.Timeline.objects.get(id=ancestor_id)
        user     = timeline_app.models.User.objects.get(id=self.user_id)
        post = models.Post.objects.create(user=user, ancestor=ancestor)
        form     = forms.PostForm(instance=post)
        return render(request, 'post_app/create-post.html', 
        {'form':form, 'post': post, 'ancestor':ancestor})

    def post(self, request, ancestor_id, post_id):
        post     = models.Post.objects.get(id=post_id)
        ancestor = timeline_app.models.Timeline.objects.get(id=ancestor_id)

        form = forms.PostForm(request.POST, request.FILES, instance=post)
        if not form.is_valid():
            return render(request, 'post_app/create-post.html',
                        {'form': form, 'post':post, 
                                'ancestor': ancestor}, status=400)

        post.save()
        user     = timeline_app.models.User.objects.get(id=self.user_id)

        event    = models.ECreatePost.objects.create(organization=user.default,
        timeline=ancestor, post=post, user=user)

        users = ancestor.users.all()
        event.users.add(*users)

        ws.client.publish('timeline%s' % ancestor.id, 
            'sound', 0, False)


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

        user     = timeline_app.models.User.objects.get(id=self.user_id)
        event    = models.EUpdatePost.objects.create(organization=user.default,
        timeline=record.ancestor, post=record, user=user)

        event.users.add(*record.ancestor.users.all())

        # Notify workers of the event, in case the post
        # is on a timeline whose worker is not on.
        event.users.add(*record.workers.all())

        ws.client.publish('timeline%s' % record.ancestor.id, 
            'sound', 0, False)

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
        attachments = post.PostFileWrapperForm.all()
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
        filewrapper = models.PostFileWrapper.objects.get(id=filewrapper_id)
        filewrapper.delete()
        attachments = filewrapper.post.filewrapper_set.all()

        form = forms.PostFileWrapperForm()
        return render(request, 'post_app/attach-file.html', 
        {'post':filewrapper.post, 'form': form, 'attachments': attachments})

class DeletePost(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id = post_id)
        # post.delete()

        user  = timeline_app.models.User.objects.get(id=self.user_id)

        event = models.EDeletePost.objects.create(organization=user.default,
        timeline=post.ancestor, post_label=post.label, user=user)
        users = post.ancestor.users.all()
        event.users.add(*users)

        ancestor = post.ancestor
        post.delete()

        ws.client.publish('timeline%s' % post.ancestor.id, 
            'sound', 0, False)

        return redirect('timeline_app:list-posts', 
        timeline_id=ancestor.id)

class ListAssignments(GuardianView):
    def get(self, request, user_id):
        user = timeline_app.models.User.objects.get(id=self.user_id)
        total = user.assignments.all()

        posts = user.assignments.filter(done=False)

        return render(request, 'post_app/list-assignments.html', 
        {'posts': posts, 'user':user, 'total': total})

class UnassignPostUser(GuardianView):
    def get(self, request, post_id, user_id):
        user = User.objects.get(id=user_id)
        post = models.Post.objects.get(id=post_id)
        post.workers.remove(user)
        post.save()

        me = User.objects.get(id=self.user_id)

        event = models.EUnassignPost.objects.create(
        organization=me.default, ancestor=post.ancestor, 
        post=post, user=me, peer=user)
        event.users.add(*post.ancestor.users.all())
        event.save()

        ws.client.publish('timeline%s' % post.ancestor.id, 
            'sound', 0, False)

        return HttpResponse(status=200)

class AssignPostUser(GuardianView):
    def get(self, request, post_id, user_id):
        user = User.objects.get(id=user_id)
        post = models.Post.objects.get(id=post_id)
        post.workers.add(user)
        post.save()
        me = User.objects.get(id=self.user_id)

        event = models.EAssignPost.objects.create(
        organization=me.default, ancestor=post.ancestor, 
        post=post, user=me, peer=user)
        event.users.add(*post.ancestor.users.all())
        event.save()

        ws.client.publish('timeline%s' % post.ancestor.id, 
            'sound', 0, False)

        return HttpResponse(status=200)


class ManagePostWorkers(GuardianView):
    def get(self, request, post_id):
        me = User.objects.get(id=self.user_id)
        post = models.Post.objects.get(id=post_id)

        included = post.workers.all()
        excluded = User.objects.exclude(assignments=post)

        return render(request, 'post_app/manage-post-workers.html', 
        {'included': included, 'excluded': excluded, 'post': post,
        'me': me, 'organization': me.default,'form':forms.UserSearchForm()})

    def post(self, request, post_id):
        form = forms.UserSearchForm(request.POST)

        me = User.objects.get(id=self.user_id)
        post = models.Post.objects.get(id=post_id)
        included = post.workers.all()
        excluded = User.objects.exclude(assignments=post)

        if not form.is_valid():
            return render(request, 'post_app/manage-post-workers.html', 
                {'included': included, 'excluded': excluded,
                    'me': me, 'organization': me.default, 'post': post,
                        'form':forms.UserSearchForm()}, status=400)

        included = included.filter(
        name__contains=form.cleaned_data['name'])

        excluded = excluded.filter(
        name__contains=form.cleaned_data['name'])

        return render(request, 'post_app/manage-post-workers.html', 
        {'included': included, 'excluded': excluded, 'post': post,
        'me': me, 'organization': me.default,'form':forms.UserSearchForm()})

class SetupPostFilter(GuardianView):
    def get(self, request, timeline_id):
        filter = models.PostFilter.objects.get(
        user__id=self.user_id, timeline__id=timeline_id)
        timeline = timeline_app.models.Timeline.objects.get(id=timeline_id)

        return render(request, 'post_app/setup-post-filter.html', 
        {'form': forms.PostFilterForm(instance=filter), 
        'timeline': timeline})

    def post(self, request, timeline_id):
        record = models.PostFilter.objects.get(
        timeline__id=timeline_id, user__id=self.user_id)

        form     = forms.PostFilterForm(request.POST, instance=record)
        timeline = timeline_app.models.Timeline.objects.get(id=timeline_id)

        if not form.is_valid():
            return render(request, 'post_app/setup-post-filter.html',
                   {'timeline': record, 'form': form}, status=400)
        form.save()
        return redirect('timeline_app:list-posts', timeline_id=timeline.id)

class SetupGlobalPostFilter(GuardianView):
    def get(self, request):
        user   = User.objects.get(id=self.user_id)
        filter = models.GlobalPostFilter.objects.get(organization=user.default,
        user__id=self.user_id)

        return render(request, 'post_app/setup-global-post-filter.html', 
        {'form': forms.GlobalPostFilterForm(instance=filter)})

    def post(self, request):
        user   = User.objects.get(id=self.user_id)
        record = models.GlobalPostFilter.objects.get(
        user__id=self.user_id)

        form = forms.GlobalPostFilterForm(request.POST, instance=record)

        if not form.is_valid():
            return render(request, 'post_app/setup-global-postfilter.html',
                   {'form': form}, status=400)
        form.save()
        return redirect('timeline_app:list-all-posts', user_id=user.id)

class CutPost(GuardianView):
    def get(self, request, post_id):
        post          = models.Post.objects.get(id=post_id)
        user          = timeline_app.models.User.objects.get(id=self.user_id)
        timeline      = post.ancestor

        # Should have an event, missing creating event.
        ws.client.publish('timeline%s' % post.ancestor.id, 
            'sound', 0, False)

        post.ancestor = None
        post.save()

        clipboard = timeline_app.models.Clipboard.objects.create(
        timeline=timeline, post=post)

        user.clipboard.add(clipboard)

        event    = models.ECutPost.objects.create(organization=user.default,
        timeline=timeline, post=post, user=user)
        users = timeline.users.all()
        event.users.add(*users)

        return redirect('timeline_app:list-posts', 
        timeline_id=timeline.id)

class CopyPost(GuardianView):
    def get(self, request, post_id):
        post = models.Post.objects.get(id=post_id)
        user = timeline_app.models.User.objects.get(id=self.user_id)
        copy = post.duplicate()
        clipboard = timeline_app.models.Clipboard.objects.create(
        timeline=post.ancestor, post=copy)
        user.clipboard.add(clipboard)

        # should have event, missing creation of event.
        ws.client.publish('timeline%s' % post.ancestor.id, 
            'sound', 0, False)

        return redirect('timeline_app:list-posts', 
        timeline_id=post.ancestor.id)

class Done(GuardianView):
    def get(self, request, post_id):
        post      = models.Post.objects.get(id=post_id)
        post.done = True
        post.save()

        user = timeline_app.models.User.objects.get(id=self.user_id)

        # posts in the clipboard cant be archived.
        event    = models.EArchivePost.objects.create(organization=user.default,
        timeline=post.ancestor, post=post, user=user)

        users = post.ancestor.users.all()
        event.users.add(*users)

        # Missing event.
        ws.client.publish('timeline%s' % post.ancestor.id, 
            'sound', 0, False)

        return redirect('timeline_app:list-posts', 
        timeline_id=post.ancestor.id)

class Undo(GuardianView):
    def get(self, request, post_id):
        post      = models.Post.objects.get(id=post_id)
        post.done = False
        post.save()

        user = timeline_app.models.User.objects.get(id=self.user_id)

        # posts in the clipboard cant be archived.
        # event    = models.EArchivePost.objects.create(organization=user.default,
        # timeline=post.ancestor, post=post, user=user)

        # users = post.ancestor.users.all()
        # event.users.add(*users)

        # Missing event.
        ws.client.publish('timeline%s' % post.ancestor.id, 
            'sound', 0, False)

        return redirect('timeline_app:list-posts', 
        timeline_id=post.ancestor.id)

class ECreatePost(GuardianView):
    def get(self, request, event_id):
        event = models.ECreatePost.objects.get(id=event_id)
        return render(request, 'post_app/e-create-post.html', 
        {'event':event})

class EArchivePost(GuardianView):
    def get(self, request, event_id):
        event = models.EArchivePost.objects.get(id=event_id)
        return render(request, 'post_app/e-archive-post.html', 
        {'event':event})

class EDeletePost(GuardianView):
    def get(self, request, event_id):
        event = models.EDeletePost.objects.get(id=event_id)
        return render(request, 'post_app/e-delete-post.html', 
        {'event':event})

class ECutPost(GuardianView):
    def get(self, request, event_id):
        event = models.ECutPost.objects.get(id=event_id)
        return render(request, 'post_app/e-cut-post.html', 
        {'event':event})

class EUpdatePost(GuardianView):
    def get(self, request, event_id):
        event = models.EUpdatePost.objects.get(id=event_id)
        return render(request, 'post_app/e-update-post.html', 
        {'event':event})

class ManagePostTags(GuardianView):
    def get(self, request, post_id):
        me = User.objects.get(id=self.user_id)
        post = models.Post.objects.get(id=post_id)

        included = post.tags.all()
        excluded = core_app.models.Tag.objects.exclude(posts=post)

        return render(request, 'post_app/manage-post-tags.html', 
        {'included': included, 'excluded': excluded, 'post': post,
        'organization': me.default,'form':forms.TagSearchForm()})

    def post(self, request, post_id):
        form = forms.TagSearchForm(request.POST)

        me = User.objects.get(id=self.user_id)
        post = models.Post.objects.get(id=post_id)
        included = post.tags.all()
        excluded = core_app.models.Tag.objects.exclude(posts=post)

        if not form.is_valid():
            return render(request, 'post_app/manage-post-tags.html', 
                {'included': included, 'excluded': excluded,
                    'organization': me.default, 'post': post,
                        'form':form}, status=400)

        included = included.filter(
        name__contains=form.cleaned_data['name'])

        excluded = excluded.filter(
        name__contains=form.cleaned_data['name'])

        return render(request, 'post_app/manage-post-tags.html', 
        {'included': included, 'excluded': excluded, 'post': post,
        'me': me, 'organization': me.default,'form':form})

class UnbindPostTag(GuardianView):
    def get(self, request, post_id, tag_id):
        tag = core_app.models.Tag.objects.get(id=tag_id)
        post = models.Post.objects.get(id=post_id)
        post.tags.remove(tag)
        post.save()

        # me = User.objects.get(id=self.user_id)

        # event = models.EUnbindPostTag.objects.create(
        # organization=me.default, ancestor=post.ancestor, 
        # post=post, user=me, peer=user)
        # event.users.add(*post.ancestor.users.all())
        # event.save()

        me = User.objects.get(id=self.user_id)

        event = models.EUnbindTagPost.objects.create(
        organization=me.default, ancestor=post.ancestor, 
        post=post, tag=tag, user=me)
        event.users.add(*post.ancestor.users.all())
        event.save()

        ws.client.publish('timeline%s' % post.ancestor.id, 
            'sound', 0, False)

        return HttpResponse(status=200)

class BindPostTag(GuardianView):
    def get(self, request, post_id, tag_id):
        tag = core_app.models.Tag.objects.get(id=tag_id)
        post = models.Post.objects.get(id=post_id)
        post.tags.add(tag)
        post.save()

        me = User.objects.get(id=self.user_id)

        event = models.EBindTagPost.objects.create(
        organization=me.default, ancestor=post.ancestor, 
        post=post, tag=tag, user=me)
        event.users.add(*post.ancestor.users.all())
        event.save()

        ws.client.publish('timeline%s' % post.ancestor.id, 
            'sound', 0, False)

        return HttpResponse(status=200)

class EBindTagPost(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.EBindTagPost.objects.get(id=event_id)
        return render(request, 'post_app/e-bind-tag-post.html', 
        {'event':event})

class EUnbindTagPost(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.EUnbindTagPost.objects.get(id=event_id)
        return render(request, 'post_app/e-unbind-tag-post.html', 
        {'event':event})

class EUnassignPost(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.EUnassignPost.objects.get(id=event_id)
        return render(request, 'post_app/e-unassign-post.html', 
        {'event':event})

class EAssignPost(GuardianView):
    """
    """

    def get(self, request, event_id):
        event = models.EAssignPost.objects.get(id=event_id)
        return render(request, 'post_app/e-assign-post.html', 
        {'event':event})














