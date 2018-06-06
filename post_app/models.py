from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from markdown.extensions.tables import TableExtension
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from mdx_gfm import GithubFlavoredMarkdownExtension
from sqlike.parser import SqLike, SqNode
from markdown import markdown
from timeline_app.models import Timeline
from core_app.models import Event
from functools import reduce
import operator

# Create your models here.

class PostMixin(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def locate(cls, user, organization, post_id):
        """
        Supposed to retrieve a given post only if the post matches
        the required constraints.
        """

        post = cls.objects.filter(
        Q(ancestor__users=user) | Q(workers=user),
        ancestor__organization=organization, id=post_id).distinct()
        return post.first()

    def save(self, *args, **kwargs):
        self.html = markdown(self.data,
        extensions=[TableExtension(), GithubFlavoredMarkdownExtension()], safe_mode=True,  
        enable_attributes=False)
        super(PostMixin, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('post_app:post', 
        kwargs={'post_id': self.id})

    def get_link_url(self):
        return reverse('post_app:post-link', 
                    kwargs={'post_id': self.id})

    def get_update_url(self):
        return reverse('post_app:update-post', 
        kwargs={'post_id': self.id})

    def duplicate(self, timeline=None):
        post          = Post.objects.get(id=self.id)
        post.pk       = None
        post.ancestor = timeline
        post.save()

        for ind in self.postfilewrapper_set.all():
            ind.duplicate(post)
        return post

    @classmethod
    def get_allowed_posts(cls, user):
        """
        Return all posts that the user is a worker
        or a member of the timeline
        """

        posts = Post.objects.filter(Q(ancestor__organization=user.default) &
            (Q(ancestor__users=user) | Q(workers=user))).distinct()
        return posts

    @classmethod
    def from_sqlike(cls):
        user = lambda ind: Q(user__name__icontains=ind) | Q(
        user__email__icontains=ind)

        worker = lambda ind: Q(workers__name__icontains=ind) | Q(    
        workers__email__icontains=ind)

        created  = lambda ind: Q(created__icontains=ind)
        label    = lambda ind: Q(label__icontains=ind)
        tag      = lambda ind: Q(tags__name__icontains=ind)
        file     = lambda ind: Q(postfilewrapper__file__icontains=ind)
        timeline = lambda ind: Q(ancestor__name__icontains=ind)
        comment  = lambda ind: Q(postcomment__data__icontains=ind)
        snippet  = lambda ind: Q(snippets__title__icontains=ind) | Q(
        snippets__data__icontains=ind)

        default = lambda ind: Q(label__icontains=ind) | Q(data__icontains=ind)

        sqlike = SqLike(SqNode(None, default),
        SqNode(('o', 'owner'), user),
        SqNode(('f', 'file'), file, chain=True),
        SqNode(('w', 'worker'), worker, chain=True), 
        SqNode(('c', 'created'), created),
        SqNode(('l', 'label'), label),
        SqNode(('t', 'tag'), tag, chain=True),
        SqNode(('s', 'snippet'), snippet),
        SqNode(('i', 'timeline'), timeline),)
        return sqlike

    def __str__(self):
        return self.label

class GlobalAssignmentsFilterMixin(models.Model):
    class Meta:
        abstract = True

    def get_partial(self, posts):
        posts = posts.filter(Q(done=self.done))
        if self.options == '0':
            return posts.filter(workers=self.user)
        elif self.options == '1':
            return posts.filter(user=self.user)
        return posts

class PostFilterMixin(models.Model):
    class Meta:
        abstract = True

    def collect(self, posts):
        posts = posts.filter(done=False)

        if not self.status:
            return posts

        sqlike = Post.from_sqlike()
        sqlike.feed(self.pattern)
        posts = sqlike.run(posts)

        return posts

class PostFileWrapperMixin(models.Model):
    class Meta:
        abstract = True

    def duplicate(self, post=None):
        wrapper       = PostFileWrapper.objects.get(id=self.id)
        wrapper.pk    = None
        wrapper.post  = post
        wrapper.save()
        return wrapper

class Post(PostMixin):
    user = models.ForeignKey('core_app.User', 
    null=True, blank=True)

    # parent = models.ForeignKey('card_app.Card', 
    # related_name='post_forks', null=True, blank=True)

    ancestor = models.ForeignKey(
    'timeline_app.Timeline', related_name='posts', 
    null=True, blank=True)

    created = models.DateTimeField(auto_now=True, 
    null=True)

    tags = models.ManyToManyField(
    'core_app.Tag', related_name='posts', 
    null=True, blank=True, symmetrical=False)

    workers = models.ManyToManyField('core_app.User', 
    related_name='assignments', blank=True, 
    symmetrical=False)

    label = models.CharField(null=True, blank=False, 
    verbose_name=_("Label"), help_text='Short description,', 
    max_length=626)

    done = models.BooleanField(blank=True, default=False)
    html = models.TextField(null=True, blank=True)

    data = models.TextField(blank=True, verbose_name=_("Data"), 
    help_text='Markdown content.', default='')

class PostFilter(PostFilterMixin):
    pattern = models.CharField(max_length=255, default='',
    blank=True, help_text='Example: tag:bug + tag:python')

    user = models.ForeignKey('core_app.User', 
    null=True, blank=True)

    status = models.BooleanField(blank=True, 
    default=False, help_text='Filter On/Off.')

    done = models.BooleanField(blank=True, 
    default=False, help_text='Done posts.')

    timeline = models.ForeignKey(
    'timeline_app.Timeline', blank=True, null=True)

    # It warrants there will exist only one user and organization
    # filter. If we decide to permit more filters..
    class Meta:
        unique_together = ('user', 'timeline', )

class GlobalPostFilter(models.Model):
    pattern = models.CharField(max_length=255, default='',
    blank=True, help_text='Example: worker:oliveira + timeline:backlog + tag:git')

    user = models.ForeignKey('core_app.User', 
    null=True, blank=True)

    organization = models.ForeignKey('core_app.Organization', 
    null=True, blank=True)

    status = models.BooleanField(blank=True, 
    default=False, help_text='Filter On/Off.')

    done = models.BooleanField(blank=True, 
    default=False, help_text='Done posts.')

    class Meta:
        unique_together = ('user', 'organization', )

class GlobalAssignmentFilter(GlobalAssignmentsFilterMixin):
    pattern = models.CharField(max_length=255, default='',
    blank=True, help_text='Example: tag:arcamens + tag:urgent')

    user = models.ForeignKey('core_app.User', 
    null=True, blank=True)

    organization = models.ForeignKey('core_app.Organization', 
    null=True, blank=True)

    status = models.BooleanField(blank=True, 
    default=False, help_text='Filter On/Off.')

    CHOICES = (
        ('0', 'Assigned to Me'),
        ('1', 'Created by Me'),
        ('2', 'All Tasks')


    )

    options = models.CharField(max_length=6, 
    choices=CHOICES, default='0')

    done = models.BooleanField(blank=True, 
    default=False, help_text='Done posts.')

    class Meta:
        unique_together = ('user', 'organization', )


class PostFileWrapper(PostFileWrapperMixin, models.Model):
    post = models.ForeignKey('Post', 
    null=True, on_delete=models.CASCADE, blank=True)

    file = models.FileField(
    verbose_name='', help_text='')

class ECreatePost(Event):
    timeline = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_create_post0', blank=True)

    post = models.ForeignKey('Post', blank=True,
    related_name='e_create_post1')

    html_template = 'post_app/e-create-post.html'

class EArchivePost(Event):
    timeline = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_archive_post0', blank=True)
    post = models.ForeignKey('Post', blank=True,
    related_name='e_archive_post1')
    html_template = 'post_app/e-archive-post.html'

class EUnarchivePost(Event):
    timeline = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_unarchive_post0', blank=True)
    post = models.ForeignKey('Post', blank=True,
    related_name='e_unarchive_post1')
    html_template = 'post_app/e-unarchive-post.html'

class EDeletePost(Event):
    timeline = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_delete_post', blank=True)

    post_label = models.CharField(null=True, 
    blank=False, max_length=626)

    html_template = 'post_app/e-delete-post.html'

class ECutPost(Event):
    timeline = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_cut_post0', blank=True)

    post = models.ForeignKey('Post', 
    related_name='e_cut_post1', blank=True)
    html_template = 'post_app/e-cut-post.html'

class ECopyPost(Event):
    timeline = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_copy_post0', blank=True)

    post = models.ForeignKey('Post', 
    related_name='e_copy_post1', blank=True)
    html_template = 'post_app/e-copy-post.html'

class EUpdatePost(Event):
    timeline = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_update_post0', blank=True)
    post = models.ForeignKey('Post', blank=True)
    html_template = 'post_app/e-update-post.html'

class EAssignPost(Event):
    """
    """

    ancestor = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_assign_post0', blank=True)

    post = models.ForeignKey('Post', 
    related_name='e_assign_post1', blank=True)

    peer = models.ForeignKey('core_app.User', 
    related_name='e_assign_post2', blank=True)

    html_template = 'post_app/e-assign-post.html'

class EUnassignPost(Event):
    """
    """

    ancestor = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_unassign_post0', blank=True)

    post = models.ForeignKey('Post', 
    related_name='e_unassign_post1', blank=True)

    peer = models.ForeignKey('core_app.User', 
    related_name='e_unassign_post2', blank=True)

    html_template = 'post_app/e-unassign-post.html'

class EBindTagPost(Event):
    """
    """

    ancestor = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_bind_tag_post0', blank=True)

    post = models.ForeignKey('Post', 
    related_name='e_bind_tag_post1', blank=True)

    tag = models.ForeignKey('core_app.Tag', 
    related_name='e_bind_tag_post2', blank=True)

    html_template = 'post_app/e-bind-tag-post.html'


class EUnbindTagPost(Event):
    """
    """

    ancestor = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_unbind_tag_post0', blank=True)

    post = models.ForeignKey('Post', 
    related_name='e_unbind_tag_post1', blank=True)

    tag = models.ForeignKey('core_app.Tag', 
    related_name='e_unbind_tag_post2', blank=True)

    html_template = 'post_app/e-unbind-tag-post.html'

class ECreateCardFork(Event):
    """
    """

    ancestor = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_create_card_fork0', blank=True)

    post = models.ForeignKey('Post', 
    related_name='e_create_card_fork1', blank=True)

    card = models.ForeignKey('card_app.Card', 
    related_name='e_create_card_fork2', blank=True)

    html_template = 'post_app/e-create-card-fork.html'

# Signals.
@receiver(pre_delete, sender=PostFileWrapper)
def delete_filewrapper(sender, instance, **kwargs):
    instance.file.delete(save=False)

class PostPinMixin(models.Model):
    class Meta:
        abstract = True

    def get_absolute_url(self):
        return reverse('post_app:post', 
            kwargs={'post_id': self.post.id})

class PostPin(PostPinMixin):
    user = models.ForeignKey('core_app.User', null=True, blank=True)

    organization = models.ForeignKey('core_app.Organization', 
    blank=True, null=True)

    post = models.ForeignKey('post_app.Post', null=True, blank=True)

    class Meta:
        unique_together = ('user', 'organization', 'post')

class EAttachPostFile(Event):
    """
    """

    filewrapper = models.ForeignKey('PostFileWrapper', 
    related_name='e_attach_post_file0', blank=True)

    post = models.ForeignKey('Post', 
    related_name='e_attach_post_file1', blank=True)

    html_template = 'post_app/e-attach-post-file.html'

class EDettachPostFile(Event):
    """
    """
    filename = models.CharField(null=True, blank=False, 
    max_length=626)

    post = models.ForeignKey('Post', 
    related_name='e_dettach_post_file1', blank=True)

    html_template = 'post_app/e-dettach-post-file.html'






