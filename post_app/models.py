from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
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

        post = cls.objects.filter(Q(ancestor__users=user),
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

    def duplicate(self, group=None):
        post          = Post.objects.get(id=self.id)
        post.pk       = None
        post.ancestor = group
        post.save()

        for ind in self.postfilewrapper_set.all():
            ind.duplicate(post)
        return post

    def __str__(self):
        return self.label

class PostSearchMixin(models.Model):
    class Meta:
        abstract = True

    def get_partial(self, posts):
        posts = posts.filter(Q(done=self.done))

        # if self.assigned:
            # posts = posts.filter(Q(workers__isnull=False))
        # if self.assigned_by_me:
            # posts = posts.filter(Q(posttaskship__assigner=self.user))
        # if self.assigned_to_me:
            # posts = posts.filter(workers=self.user)
        if self.created_by_me:
            posts = posts.filter(owner=self.user)
        return posts

class PostFilterMixin(models.Model):
    class Meta:
        abstract = True

    def from_sqpost(self, posts):
        from post_app.sqlikes import SqPost

        sqlike = SqPost()
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

class PostTagship(models.Model):
    """    
    """

    # When posts are deleted it should get its corresponding PostTagship
    # record deleted as well otherwise it would stay existing in the database
    # with no practical usage at all.i It could be useful for other purposes
    # like which were the tags most used by a given user etc
    post = models.ForeignKey('Post', null=True, on_delete=models.CASCADE)
    tag  = models.ForeignKey('core_app.Tag', 
    null=True, on_delete=models.CASCADE, related_name='post_tagship')

    tagger = models.ForeignKey('core_app.User', 
    null=True, on_delete=models.CASCADE, related_name='post_taggership')

    created = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ('post', 'tag', )

class Post(PostMixin):
    owner = models.ForeignKey('core_app.User', 
    null=True, on_delete=models.CASCADE)

    priority = models.IntegerField(default=0)

    # parent = models.ForeignKey('card_app.Card', 
    # related_name='post_forks', null=True, blank=True)

    ancestor = models.ForeignKey('group_app.Group', 
    related_name='posts', null=True, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True, null=True)

    tags = models.ManyToManyField('core_app.Tag', related_name='posts', 
    through=PostTagship, through_fields=('post', 'tag'),
    blank=True, symmetrical=False)

    likes = models.ManyToManyField('core_app.User', 
    related_name='post_likes', symmetrical=False)

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
    null=False, on_delete=models.CASCADE)

    status = models.BooleanField(blank=True, 
    default=False, help_text='Filter On/Off.')

    done = models.BooleanField(blank=True, 
    default=False, help_text='Done posts.')

    group = models.ForeignKey('group_app.Group', 
    null=False, on_delete=models.CASCADE)

    # It warrants there will exist only one user and organization
    # filter. If we decide to permit more filters..
    class Meta:
        unique_together = ('user', 'group', )

class PostSearch(PostSearchMixin):
    pattern = models.CharField(max_length=255, default='',
    blank=True, help_text='Example: worker:oliveira + group:backlog + tag:git')

    user = models.ForeignKey('core_app.User', 
    null=False, on_delete=models.CASCADE)

    organization = models.ForeignKey('core_app.Organization', 
    null=False, on_delete=models.CASCADE)

    status = models.BooleanField(blank=True, 
    default=False, help_text='Filter On/Off.')

    done = models.BooleanField(blank=True, default=False)

    # assigned = models.BooleanField(blank=False, default=True)
    # assigned_by_me = models.BooleanField(blank=False, default=True)
# 
    # assigned_to_me = models.BooleanField(blank=True, default=True)
    created_by_me = models.BooleanField(blank=True, default=False)

    class Meta:
        unique_together = ('user', 'organization', )

class PostFileWrapper(PostFileWrapperMixin, models.Model):
    organization = models.ForeignKey('core_app.Organization', 
    null=False, on_delete=models.CASCADE)

    post = models.ForeignKey('Post', 
    null=True, on_delete=models.CASCADE, blank=True)

    file = models.FileField(
    verbose_name='', help_text='')

class ECreatePost(Event):
    group = models.ForeignKey('group_app.Group', 
    related_name='e_create_post0', null=True, on_delete=models.CASCADE)

    post = models.ForeignKey('Post', blank=True,
    related_name='e_create_post1', null=True, on_delete=models.CASCADE)

    html_template = 'post_app/e-create-post.html'

class EArchivePost(Event):
    group = models.ForeignKey('group_app.Group', 
    related_name='e_archive_post0', null=True, on_delete=models.CASCADE)

    post = models.ForeignKey('Post', null=True, 
    on_delete=models.CASCADE, related_name='e_archive_post1')
    html_template = 'post_app/e-archive-post.html'

class EUnarchivePost(Event):
    group = models.ForeignKey('group_app.Group', 
    related_name='e_unarchive_post0', null=True, on_delete=models.CASCADE)

    post = models.ForeignKey('Post', null=True, 
    on_delete=models.CASCADE, related_name='e_unarchive_post1')
    html_template = 'post_app/e-unarchive-post.html'

class EDeletePost(Event):
    group = models.ForeignKey('group_app.Group', 
    related_name='e_delete_post', null=True, on_delete=models.CASCADE)

    post_label    = models.CharField(max_length=626)
    html_template = 'post_app/e-delete-post.html'

class ECutPost(Event):
    group = models.ForeignKey('group_app.Group', 
    related_name='e_cut_post0', null=True, on_delete=models.CASCADE)

    post = models.ForeignKey('Post', 
    related_name='e_cut_post1', null=True, on_delete=models.CASCADE)

    html_template = 'post_app/e-cut-post.html'

class ECopyPost(Event):
    group = models.ForeignKey('group_app.Group',
    related_name='e_copy_post0', null=True, on_delete=models.CASCADE)

    post = models.ForeignKey('Post', 
    related_name='e_copy_post1', null=True, on_delete=models.CASCADE)

    html_template = 'post_app/e-copy-post.html'

class EUpdatePost(Event):
    group = models.ForeignKey('group_app.Group', 
    related_name='e_update_post0', null=True, on_delete=models.CASCADE)

    post = models.ForeignKey('Post', null=True, on_delete=models.CASCADE)

    post_label = models.CharField(null=True, blank=False,
    verbose_name=_("Label"), help_text='Label, Deadline, ...', 
    max_length=626)

    post_html = models.TextField(null=True, blank=True)
    post_data = models.TextField(blank=True, verbose_name=_("Data"), 
    help_text='Markdown content.', default='')

    html_template = 'post_app/e-update-post.html'

class ERestorePost(Event):
    """
    """

    ancestor = models.ForeignKey('group_app.Group', 
    related_name='e_restore_post0', null=True, on_delete=models.CASCADE)

    post = models.ForeignKey('Post', 
    related_name='e_restore_post1', null=True, on_delete=models.CASCADE)

    event_html    = models.TextField(null=True, blank=True)
    html_template = 'post_app/e-restore-post.html'

class ELikePost(Event):
    """
    """

    ancestor = models.ForeignKey('group_app.Group',
    related_name='e_like_post0', null=True, on_delete=models.CASCADE)

    post = models.ForeignKey('Post',
    related_name='e_like_post1', null=True, on_delete=models.CASCADE)

    status = models.CharField(max_length=626, null=True)
    html_template = 'post_app/e-like-post.html'

class EUnlikePost(Event):
    """
    """

    ancestor = models.ForeignKey('group_app.Group',
    related_name='e_unlike_post0', null=True, on_delete=models.CASCADE)

    post = models.ForeignKey('Post',
    related_name='e_unlike_post1', null=True, on_delete=models.CASCADE)

    status = models.CharField(max_length=626, null=True)
    html_template = 'post_app/e-unlike-post.html'

class EBindTagPost(Event):
    """
    """

    ancestor = models.ForeignKey('group_app.Group', 
    related_name='e_bind_tag_post0', null=True, on_delete=models.CASCADE)

    post = models.ForeignKey('Post', 
    related_name='e_bind_tag_post1', null=True, on_delete=models.CASCADE)

    tag = models.ForeignKey('core_app.Tag', 
    related_name='e_bind_tag_post2', null=True, on_delete=models.CASCADE)

    html_template = 'post_app/e-bind-tag-post.html'


class EUnbindTagPost(Event):
    """
    """

    ancestor = models.ForeignKey('group_app.Group', 
    related_name='e_unbind_tag_post0', null=True, on_delete=models.CASCADE)

    post = models.ForeignKey('Post', 
    related_name='e_unbind_tag_post1', null=True, on_delete=models.CASCADE)

    tag = models.ForeignKey('core_app.Tag', 
    related_name='e_unbind_tag_post2', null=True, on_delete=models.CASCADE)

    html_template = 'post_app/e-unbind-tag-post.html'

class ECreatePostFork(Event):
    """
    """

    list = models.ForeignKey('list_app.List', 
    related_name='e_create_post_fork0', null=True, on_delete=models.CASCADE)

    card = models.ForeignKey('card_app.Card', 
    related_name='e_create_post_fork1', null=True, on_delete=models.CASCADE)

    post = models.ForeignKey('post_app.Post', 
    related_name='e_create_post_fork2', null=True, on_delete=models.CASCADE)

    group = models.ForeignKey('group_app.Group', 
    related_name='e_create_post_fork3', null=True, on_delete=models.CASCADE)

    board = models.ForeignKey('board_app.Board', 
    related_name='e_create_post_fork4', default=None, 
    null=True, on_delete=models.SET_NULL)

    html_template = 'post_app/e-create-post-fork.html'

class PostPinMixin(models.Model):
    class Meta:
        abstract = True

    def get_absolute_url(self):
        return reverse('post_app:post', 
            kwargs={'post_id': self.post.id})

class PostPin(PostPinMixin):
    user = models.ForeignKey('core_app.User', 
    null=False, on_delete=models.CASCADE)

    organization = models.ForeignKey('core_app.Organization',
    null=False, on_delete=models.CASCADE)

    post = models.ForeignKey('post_app.Post', 
    null=False, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'organization', 'post')

class EAttachPostFile(Event):
    """
    """

    filewrapper = models.ForeignKey('PostFileWrapper',
    related_name='e_attach_post_file0', null=True, on_delete=models.CASCADE)

    post = models.ForeignKey('Post',
    related_name='e_attach_post_file1', null=False, on_delete=models.CASCADE)

    html_template = 'post_app/e-attach-post-file.html'

class EDettachPostFile(Event):
    """
    """
    filename = models.CharField(null=True, blank=False, 
    max_length=626)

    post = models.ForeignKey('Post', 
    related_name='e_dettach_post_file1', null=False, on_delete=models.CASCADE)

    html_template = 'post_app/e-dettach-post-file.html'

class ESetPostPriorityUp(Event):
    """
    """

    ancestor = models.ForeignKey('group_app.Group', 
    related_name='e_set_post_priority_up0', null=False, on_delete=models.CASCADE)

    post0 = models.ForeignKey('Post', 
    related_name='e_set_post_priority_up1', null=False, on_delete=models.CASCADE)

    post1 = models.ForeignKey('Post', 
    related_name='e_set_post_priority_up2', null=False, on_delete=models.CASCADE)

    html_template = 'post_app/e-set-priority-up.html'

class ESetPostPriorityDown(Event):
    """
    """

    ancestor = models.ForeignKey('group_app.Group', 
    related_name='e_set_post_priority_down0', null=False, on_delete=models.CASCADE)

    post0 = models.ForeignKey('Post', 
    related_name='e_set_post_priority_down1', null=False, on_delete=models.CASCADE)

    post1 = models.ForeignKey('Post', 
    related_name='e_set_post_priority_down2', null=False, on_delete=models.CASCADE)

    html_template = 'post_app/e-set-priority-down.html'

# For some reason i cant abstract it and place it outside models.
@receiver(pre_delete, sender=PostFileWrapper)
def on_filewrapper_deletion(sender, instance, **kwargs):
    is_unique = PostFileWrapper.objects.filter(file=instance.file)
    is_unique = is_unique.count() == 1
    if is_unique: 
        clean_disk(instance)








