from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from markdown.extensions.tables import TableExtension
from markdown import markdown
from timeline_app.models import Timeline
from core_app.models import Event, GlobalFilterMixin
from core_app.utils import splittokens
from functools import reduce
import operator

# Create your models here.

class PostMixin(object):
    def save(self, *args, **kwargs):
        self.html = markdown(self.data, 
            extensions=[TableExtension(),
                'markdown.extensions.tables'])
        super(PostMixin, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('post_app:post', 
        kwargs={'post_id': self.id})

    def get_absolute_url(self):
        return reverse('post_app:post', 
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
        Return all posts that a given user has access 
        regardless if it is the owner.
        """

        timelines = Timeline.get_user_timelines(user)
        posts  = Post.objects.none()

        for ind in timelines:
            posts = posts | ind.posts.all()
        return posts

    @classmethod
    def collect_posts(cls, posts, pattern, done=False):
        """
        Return all posts from a timeline that match pattern.
        """
        chks, tags = splittokens(pattern)
        posts = posts.filter(Q(done=done))

        for ind in tags:
            posts = posts.filter(Q(tags__name__startswith=ind))

        posts = posts.filter(reduce(operator.and_, 
        (Q(label__contains=ind) | Q(user__name__contains=ind) 
        for ind in chks))) if chks else posts

        return posts

    def __str__(self):
        return self.description

class PostFileWrapperMixin(object):
    def duplicate(self, post=None):
        wrapper       = PostFileWrapper.objects.get(id=self.id)
        wrapper.pk    = None
        wrapper.post  = post
        wrapper.save()
        return wrapper

class ECreatePostMixin(object):
    def get_absolute_url(self):
        return reverse('post_app:e-create-post', 
        kwargs={'event_id': self.id})

class EDeletePostMixin(object):
    def get_absolute_url(self):
        return reverse('post_app:e-delete-post', 
        kwargs={'event_id': self.id})

class EArchivePostMixin(object):
    def get_absolute_url(self):
        return reverse('post_app:e-archive-post', 
        kwargs={'event_id': self.id})

class EUpdatePostMixin(object):
    def get_absolute_url(self):
        return reverse('post_app:e-update-post', 
        kwargs={'event_id': self.id})

class ECutPostMixin(object):
    def get_absolute_url(self):
        return reverse('post_app:e-cut-post', 
        kwargs={'event_id': self.id})

class Post(PostMixin, models.Model):
    user = models.ForeignKey('core_app.User', 
    null=True, blank=True)

    parent = models.ForeignKey('card_app.Card', 
    related_name='posts', null=True, blank=True)

    ancestor = models.ForeignKey(
    'timeline_app.Timeline', related_name='posts', 
    null=True, blank=True)

    created = models.DateTimeField(auto_now=True, 
    null=True)

    tags = models.ManyToManyField(
    'core_app.Tag', related_name='posts', 
    null=True, blank=True, symmetrical=False)

    # workers = models.ManyToManyField('core_app.User', 
    # related_name='assignments', blank=True, 
    # symmetrical=False)

    label = models.CharField(null=True, blank=False, 
    verbose_name=_("Label"), help_text='Short description ...', 
    max_length=626)

    html = models.TextField(null=True, blank=True)

    data = models.TextField(blank=True, verbose_name=_("Data"), 
    help_text='Markdown content.', default='')

    task = models.BooleanField(blank=False, default=False)

    done = models.BooleanField(blank=True, default=False)
    html = models.TextField(null=True, blank=True)

class PostFilter(GlobalFilterMixin, models.Model):
    pattern = models.CharField(max_length=255, default='',
    blank=True, help_text='Example: victor + \
    #arcamens + #suggestion ...')

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

class GlobalPostFilter(GlobalFilterMixin, models.Model):
    pattern = models.CharField(max_length=255, default='',
    blank=True, help_text='Example: victor + \
    #arcamens + #suggestion ...')

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

class PostFileWrapper(PostFileWrapperMixin, models.Model):
    post = models.ForeignKey('Post', 
    null=True, on_delete=models.CASCADE, blank=True)

    file = models.FileField(
    verbose_name='', help_text='')

class ECreatePost(ECreatePostMixin, Event):
    timeline = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_create_post', blank=True)
    post = models.ForeignKey('Post', blank=True)
    html_template = 'post_app/e-create-post.html'

class EArchivePost(EArchivePostMixin, Event):
    timeline = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_archive_post', blank=True)
    post = models.ForeignKey('Post', blank=True)
    html_template = 'post_app/e-archive-post.html'

class EDeletePost(EDeletePostMixin, Event):
    timeline = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_delete_post', blank=True)

    post_label = models.CharField(null=True,
    blank=True, max_length=30)
    html_template = 'post_app/e-delete-post.html'
    task = models.BooleanField(blank=False, default=False)

class ECutPost(ECutPostMixin, Event):
    timeline = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_cut_post', blank=True)

    post = models.ForeignKey('Post', 
    related_name='e_cut_post1', blank=True)
    html_template = 'post_app/e-cut-post.html'


class EUpdatePost(EUpdatePostMixin, Event):
    timeline = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_update_post', blank=True)
    post = models.ForeignKey('Post', blank=True)
    html_template = 'post_app/e-update-post.html'

class EBindTagPost(Event):
    """
    """

    ancestor = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_bind_tag_post0', blank=True)

    post = models.ForeignKey('Post', 
    related_name='e_bind_tag_post0', blank=True)

    tag = models.ForeignKey('core_app.Tag', 
    related_name='e_bind_tag_post0', blank=True)

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






