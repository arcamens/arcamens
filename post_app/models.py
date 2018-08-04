from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from markdown.extensions.tables import TableExtension
from django.db.models.signals import pre_delete
from mdx_gfm import GithubFlavoredMarkdownExtension
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from sqlike.parser import SqLike, SqNode
from markdown import markdown
from group_app.models import Group
from core_app.miscutils import disk_cleaner
from core_app.models import Event
from functools import reduce
from slock.views import RenderExc
from card_app.models import clean_disk
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
        post = post.first()

        if not post:
            return cls.access_error(post_id)
        return post

    @classmethod
    def access_error(cls, post_id):
        post = cls.objects.get(id=post_id)
        clipboard = post.post_clipboard_users.first()

        if clipboard: 
            raise RenderExc('post_app/post-on-clipboard.html', 
                {'post': post, 'user': clipboard.user} , status=403)

    def save(self, *args, **kwargs):
        self.html = markdown(self.data,
        extensions=[TableExtension(), GithubFlavoredMarkdownExtension()], safe_mode=True,  
        enable_attributes=False)

        if not self.pk and self.ancestor:
            self.set_priority()

        super(PostMixin, self).save(*args, **kwargs)

    def set_priority(self):
        post = self.ancestor.posts.order_by('-priority').first()
        self.priority = (post.priority + 1) if post else 0

    def get_absolute_url(self):
        return reverse('post_app:post', 
        kwargs={'post_id': self.id})

    def get_link_url(self):
        return reverse('post_app:post-link', 
                    kwargs={'post_id': self.id})

    def get_update_url(self):
        return reverse('post_app:update-post', 
        kwargs={'post_id': self.id})

    def duplicate(self, group=None):
        post          = Post.objects.get(id=self.id)
        post.pk       = None
        post.ancestor = group
        post.save()

        for ind in self.postfilewrapper_set.all():
            ind.duplicate(post)
        return post

    @classmethod
    def get_allowed_posts(cls, user):
        """
        Return all posts that the user is a worker
        or a member of the group
        """

        posts = Post.objects.filter(Q(ancestor__organization=user.default) &
            (Q(ancestor__users=user) | Q(workers=user))).distinct()
        return posts

    @classmethod
    def from_sqlike(cls):
        user = lambda ind: Q(user__name__icontains=ind) | Q(
        user__email__icontains=ind)
        not_user = lambda ind: ~user(ind)

        worker = lambda ind: Q(workers__name__icontains=ind) | Q(    
        workers__email__icontains=ind)
        not_worker = lambda ind: ~worker(ind)

        created_gt = lambda ind: Q(created__gt=ind)
        created_lt = lambda ind: Q(created__lt=ind)
        created = lambda ind: Q(created__date=ind)

        label    = lambda ind: Q(label__icontains=ind)
        not_label = lambda ind: ~label(ind)

        data    = lambda ind: Q(data__icontains=ind)
        not_data    = lambda ind: ~data(ind)

        tag      = lambda ind: Q(tags__name__icontains=ind)
        not_tag   = lambda ind: ~tag(ind)

        file     = lambda ind: Q(postfilewrapper__file__icontains=ind)
        group = lambda ind: Q(ancestor__name__icontains=ind)
        not_group = lambda ind: ~group(ind)

        snippet  = lambda ind: Q(snippets__title__icontains=ind) | Q(
        snippets__data__icontains=ind)
        not_snippet = lambda ind: ~snippet(ind)

        snippet_owner  = lambda ind: Q(snippets__owner__name__icontains=ind) |\
        Q(snippets__owner__email__icontains=ind)
        not_snippet_owner = lambda ind: ~snippet_owner(ind)

        snippet_title  = lambda ind: Q(snippets__title__icontains=ind)
        not_snippet_title = lambda ind: ~snippet_title(ind)

        snippet_data  = lambda ind: Q(snippets__data__icontains=ind)
        not_snippet_data = lambda ind: ~snippet_data(ind)

        snippet_file  = lambda ind: Q(snippets__snippetfilewrapper__file__icontains=ind)
        default = lambda ind: Q(label__icontains=ind) | Q(data__icontains=ind)

        fork   = lambda ind: Q(card_forks__children__label__icontains=ind)|\
        Q(card_forks__children__data__icontains=ind) |\
        Q(card_forks__label__icontains=ind)|\
        Q(card_forks__data__icontains=ind)
        not_fork = lambda ind: ~fork(ind)

        fork_label   = lambda ind: Q(card_forks__children__label__icontains=ind)|\
        Q(card_forks__label__icontains=ind)

        not_fork_label = lambda ind: ~fork_label(ind)

        fork_data   = lambda ind: Q(card_forks__children__data__icontains=ind)|\
        Q(card_forks__data__icontains=ind)

        not_fork_data = lambda ind: ~fork_data(ind)

        fork_tag   = lambda ind: Q(
        card_forks__children__tags__name__icontains=ind)|\
        Q(card_forks__tags__name__icontains=ind)

        not_fork_tag   = lambda ind: ~fork_tag(ind)

        fork_worker   = lambda ind: Q(
        card_forks__children__workers__name__icontains=ind)|\
        Q(card_forks__workers__name__icontains=ind)

        not_fork_worker   = lambda ind: ~fork_worker(ind)

        sqlike = SqLike(cls, SqNode(None, default),
        SqNode(('o', 'owner'), user),
        SqNode(('!o', '!owner'), not_user),

        SqNode(('f', 'file'), file, chain=True),
        SqNode(('w', 'worker'), worker, chain=True), 
        SqNode(('!w', '!worker'), not_worker, chain=True), 
        SqNode(('c>', 'created>'), created_gt),
        SqNode(('c<', 'created<'), created_lt),
        SqNode(('c', 'created'), created),

        SqNode(('l', 'label'), label),
        SqNode(('!l', '!label'), not_label),

        SqNode(('d', 'data'), data),
        SqNode(('!d', '!data'), not_data),

        SqNode(('t', 'tag'), tag, chain=True),
        SqNode(('!t', '!tag'), not_tag, chain=True),

        SqNode(('s', 'snippet'), snippet, chain=True),
        SqNode(('!s', '!snippet'), not_snippet, chain=True),

        SqNode(('so', 'snippet.owner'), snippet_owner, chain=True),
        SqNode(('!so', '!snippet.owner'), not_snippet_owner, chain=True),

        SqNode(('st', 'snippet.title'), snippet_title, chain=True),
        SqNode(('!st', '!snippet.title'), not_snippet_title, chain=True),

        SqNode(('sd', 'snippet.data'), snippet_data, chain=True),
        SqNode(('!sd', '!snippet.data'), not_snippet_data, chain=True),
        SqNode(('k', 'fork'), fork),
        SqNode(('!k', '!fork'), not_fork),

        SqNode(('kl', 'fork.label'), fork_label),
        SqNode(('!kl', '!fork.label'), not_fork_label),

        SqNode(('kd', 'fork.data'), fork_data),
        SqNode(('!kd', '!fork.data'), not_fork_data),

        SqNode(('kt', 'fork.tag'), fork_tag, chain=True),
        SqNode(('!kt', '!fork.tag'), not_fork_tag, chain=True),

        SqNode(('kw', 'fork.worker'), fork_worker, chain=True),
        SqNode(('!kw', '!fork.worker'), not_fork_worker, chain=True),

        SqNode(('sf', 'snippet.file'), snippet_file, chain=True),
        SqNode(('i', 'group'), group),
        SqNode(('!i', '!group'), not_group),)

        return sqlike

    def __str__(self):
        return self.label

class GlobalPostFilterMixin(models.Model):
    class Meta:
        abstract = True

    def get_partial(self, posts):
        posts = posts.filter(Q(done=self.done))

        if self.assigned:
            posts = posts.filter(Q(workers__isnull=False))
        if self.assigned_to_me:
            posts = posts.filter(workers=self.user)
        if self.created_by_me:
            posts = posts.filter(user=self.user)
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

class PostTaskship(models.Model):
    """    
    """
    post = models.ForeignKey('Post', null=True, blank=True)
    worker = models.ForeignKey('core_app.User', null=True, 
    related_name='post_workership', blank=True)

    assigner = models.ForeignKey('core_app.User', null=True, 
    related_name='post_assingership', blank=True)

    created  = models.DateTimeField(auto_now_add=True, null=True)

class PostTagship(models.Model):
    """    
    """
    post = models.ForeignKey('Post', null=True, blank=True)
    tag = models.ForeignKey('core_app.Tag', null=True, blank=True)

    tagger = models.ForeignKey('core_app.User', null=True, 
    related_name='post_taggership', blank=True)

    created  = models.DateTimeField(auto_now_add=True, null=True)

class Post(PostMixin):
    user = models.ForeignKey('core_app.User', 
    null=True, blank=True)

    priority = models.IntegerField(default=0)

    # parent = models.ForeignKey('card_app.Card', 
    # related_name='post_forks', null=True, blank=True)

    ancestor = models.ForeignKey(
    'group_app.Group', related_name='posts', 
    null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True, 
    null=True)

    tags = models.ManyToManyField('core_app.Tag', related_name='posts', 
    through=PostTagship, through_fields=('post', 'tag'), null=True, 
    blank=True, symmetrical=False)

    workers = models.ManyToManyField('core_app.User', 
    related_name='assignments', blank=True, through=PostTaskship,
    through_fields=('post', 'worker'), symmetrical=False)

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

    group = models.ForeignKey(
    'group_app.Group', blank=True, null=True)

    # It warrants there will exist only one user and organization
    # filter. If we decide to permit more filters..
    class Meta:
        unique_together = ('user', 'group', )

class GlobalPostFilter(GlobalPostFilterMixin):
    pattern = models.CharField(max_length=255, default='',
    blank=True, help_text='Example: worker:oliveira + group:backlog + tag:git')

    user = models.ForeignKey('core_app.User', 
    null=True, blank=True)

    organization = models.ForeignKey('core_app.Organization', 
    null=True, blank=True)

    status = models.BooleanField(blank=True, 
    default=False, help_text='Filter On/Off.')

    done = models.BooleanField(blank=True, 
    default=False, help_text='Done posts.')

    assigned = models.BooleanField(blank=False, 
    default=True, help_text='Only tasks.')

    assigned_to_me = models.BooleanField(blank=True, 
    default=True, help_text='Only your tasks.')

    created_by_me = models.BooleanField(blank=True, 
    default=False, help_text='Only posts you created.')

    class Meta:
        unique_together = ('user', 'organization', )

class PostFileWrapper(PostFileWrapperMixin, models.Model):
    organization = models.ForeignKey('core_app.Organization', 
    null=True, blank=True)

    post = models.ForeignKey('Post', 
    null=True, on_delete=models.CASCADE, blank=True)

    file = models.FileField(
    verbose_name='', help_text='')

class ECreatePost(Event):
    group = models.ForeignKey('group_app.Group', 
    related_name='e_create_post0', blank=True)

    post = models.ForeignKey('Post', blank=True,
    related_name='e_create_post1')

    html_template = 'post_app/e-create-post.html'

class EArchivePost(Event):
    group = models.ForeignKey('group_app.Group', 
    related_name='e_archive_post0', blank=True)
    post = models.ForeignKey('Post', blank=True,
    related_name='e_archive_post1')
    html_template = 'post_app/e-archive-post.html'

class EUnarchivePost(Event):
    group = models.ForeignKey('group_app.Group', 
    related_name='e_unarchive_post0', blank=True)
    post = models.ForeignKey('Post', blank=True,
    related_name='e_unarchive_post1')
    html_template = 'post_app/e-unarchive-post.html'

class EDeletePost(Event):
    group = models.ForeignKey('group_app.Group', 
    related_name='e_delete_post', blank=True)

    post_label = models.CharField(null=True, 
    blank=False, max_length=626)

    html_template = 'post_app/e-delete-post.html'

class ECutPost(Event):
    group = models.ForeignKey('group_app.Group', 
    related_name='e_cut_post0', blank=True)

    post = models.ForeignKey('Post', 
    related_name='e_cut_post1', blank=True)
    html_template = 'post_app/e-cut-post.html'

class ECopyPost(Event):
    group = models.ForeignKey('group_app.Group', 
    related_name='e_copy_post0', blank=True)

    post = models.ForeignKey('Post', 
    related_name='e_copy_post1', blank=True)
    html_template = 'post_app/e-copy-post.html'

class EUpdatePost(Event):
    group = models.ForeignKey('group_app.Group', 
    related_name='e_update_post0', blank=True)
    post = models.ForeignKey('Post', blank=True)
    html_template = 'post_app/e-update-post.html'

class EAssignPost(Event):
    """
    """

    ancestor = models.ForeignKey('group_app.Group', 
    related_name='e_assign_post0', blank=True)

    post = models.ForeignKey('Post', 
    related_name='e_assign_post1', blank=True)

    peer = models.ForeignKey('core_app.User', 
    related_name='e_assign_post2', blank=True)

    html_template = 'post_app/e-assign-post.html'

class EUnassignPost(Event):
    """
    """

    ancestor = models.ForeignKey('group_app.Group', 
    related_name='e_unassign_post0', blank=True)

    post = models.ForeignKey('Post', 
    related_name='e_unassign_post1', blank=True)

    peer = models.ForeignKey('core_app.User', 
    related_name='e_unassign_post2', blank=True)

    html_template = 'post_app/e-unassign-post.html'

class EBindTagPost(Event):
    """
    """

    ancestor = models.ForeignKey('group_app.Group', 
    related_name='e_bind_tag_post0', blank=True)

    post = models.ForeignKey('Post', 
    related_name='e_bind_tag_post1', blank=True)

    tag = models.ForeignKey('core_app.Tag', 
    related_name='e_bind_tag_post2', blank=True)

    html_template = 'post_app/e-bind-tag-post.html'


class EUnbindTagPost(Event):
    """
    """

    ancestor = models.ForeignKey('group_app.Group', 
    related_name='e_unbind_tag_post0', blank=True)

    post = models.ForeignKey('Post', 
    related_name='e_unbind_tag_post1', blank=True)

    tag = models.ForeignKey('core_app.Tag', 
    related_name='e_unbind_tag_post2', blank=True)

    html_template = 'post_app/e-unbind-tag-post.html'

class ECreatePostFork(Event):
    """
    """

    list = models.ForeignKey('list_app.List', 
    related_name='e_create_post_fork0', blank=True)

    card = models.ForeignKey('card_app.Card', 
    related_name='e_create_post_fork1', blank=True)

    post = models.ForeignKey('post_app.Post', 
    related_name='e_create_post_fork2', blank=True)

    group = models.ForeignKey('group_app.Group', 
    related_name='e_create_post_fork3', blank=True)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_create_post_fork4', default=None, 
    blank=True)

    html_template = 'post_app/e-create-post-fork.html'

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

class ESetPostPriorityUp(Event):
    """
    """

    ancestor = models.ForeignKey('group_app.Group', 
    related_name='e_set_post_priority_up0', blank=True)

    post0 = models.ForeignKey('Post', 
    related_name='e_set_post_priority_up1', blank=True)

    post1 = models.ForeignKey('Post', 
    related_name='e_set_post_priority_up2', blank=True)

    html_template = 'post_app/e-set-priority-up.html'

class ESetPostPriorityDown(Event):
    """
    """

    ancestor = models.ForeignKey('group_app.Group', 
    related_name='e_set_post_priority_down0', blank=True)

    post0 = models.ForeignKey('Post', 
    related_name='e_set_post_priority_down1', blank=True)

    post1 = models.ForeignKey('Post', 
    related_name='e_set_post_priority_down2', blank=True)

    html_template = 'post_app/e-set-priority-down.html'

# For some reason i cant abstract it and place it outside models.
@receiver(pre_delete, sender=PostFileWrapper)
def on_filewrapper_deletion(sender, instance, **kwargs):
    is_unique = PostFileWrapper.objects.filter(file=instance.file)
    is_unique = is_unique.count() == 1
    if is_unique: 
        clean_disk(instance)







