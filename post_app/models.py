from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
import timeline_app.models
from timeline_app.models import OpusEvent
from markdown.extensions.tables import TableExtension
from markdown import markdown

# Create your models here.

class PostMixin(object):
    def save(self, *args, **kwargs):
        self.html = markdown(self.description, 
        extensions=[TableExtension(), 
        'markdown.extensions.tables'])

        super(PostMixin, self).save(*args, **kwargs)

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

class EUpdatePostMixin(object):
    def get_absolute_url(self):
        return reverse('post_app:e-update-post', 
        kwargs={'event_id': self.id})

class Post(PostMixin, models.Model):
    user = models.ForeignKey('core_app.User', 
    null=True, blank=True)

    ancestor = models.ForeignKey(
    'timeline_app.Timeline', related_name='posts', 
    null=True, blank=True)

    created = models.DateTimeField(auto_now=True, 
    null=True)

    tags = models.ManyToManyField(
    'timeline_app.Tag', related_name='tags', 
    null=True, blank=True, symmetrical=False)

    label = models.CharField(null=True,
    blank=False, verbose_name=_("Label"), 
    help_text='Task, Post, OpusEvent, Thread, Bug, \
    Idea, Document, ..', max_length=30)

    workers = models.ManyToManyField('core_app.User', 
    related_name='assignments', blank=True, 
    symmetrical=False)

    description = models.TextField(null=True, default='',
    blank=True, verbose_name=_("Description"))

    done = models.BooleanField(blank=True, default=False)
    html = models.TextField(null=True, blank=True)

class PostFilter(models.Model):
    pattern = models.CharField(max_length=255, 
    blank=True, null=True)

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
    pattern = models.CharField(max_length=255, 
    blank=True, null=True)

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

    file = models.FileField(upload_to='media/', 
    verbose_name='', help_text='')

class ECreatePost(ECreatePostMixin, OpusEvent):
    timeline = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_create_post', blank=True)
    post = models.ForeignKey('Post', blank=True)

class EDeletePost(EDeletePostMixin, OpusEvent):
    timeline = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_delete_post', blank=True)

    post_label = models.CharField(null=True,
    blank=True, max_length=30)

class EUpdatePost(EUpdatePostMixin, OpusEvent):
    timeline = models.ForeignKey('timeline_app.Timeline', 
    related_name='e_update_post', blank=True)
    post = models.ForeignKey('Post', blank=True)







