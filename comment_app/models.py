# Models for Comment post type.

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from markdown.extensions.tables import TableExtension
from mdx_gfm import GithubFlavoredMarkdownExtension
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from sqlike.parser import SqLike, SqNode
from markdown import markdown
from board_app.models import Event
from post_app.models import Post
from card_app.models import clean_disk

class CommentMixin(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.html = markdown(self.data,
        extensions=[TableExtension(), GithubFlavoredMarkdownExtension()], safe_mode=True,  
        enable_attributes=False)

        super(CommentMixin, self).save(*args, **kwargs)

    def get_absolute_url(self):
        url = reverse('comment_app:comment', 
        kwargs={'comment_id': self.id})
        return url

    def get_link_url(self):
        return reverse('comment_app:comment-link', 
                    kwargs={'comment_id': self.id})

    @classmethod
    def from_sqlike(cls):
        owner = lambda ind: Q(owner__name__icontains=ind) |\
        Q(owner__email__icontains=ind)

        not_owner = lambda ind: ~owner(ind)
        data      = lambda ind: Q(data__icontains=ind)
        not_data  = lambda ind: ~data(ind)

        title     = lambda ind: Q(title__icontains=ind)
        not_title = lambda ind: ~title(ind)
        default   = lambda ind: Q(title__icontains=ind) |\
        Q(data__icontains=ind)

        sqlike = SqLike(cls, SqNode(None, default),
        SqNode(('t', 'title'), title),
        SqNode(('!t', '!title'), not_title),
        SqNode(('o', 'owner'), owner),
        SqNode(('!o', '!owner'), not_owner),
        SqNode(('d', 'data'), data),
        SqNode(('!d', '!data'), not_data),)
        return sqlike

    @classmethod
    def locate(cls, user, organization, comment_id):
        """
        Return the requested comment only if the user has access to the comment
        by belonging to the comment's post group or being a worker of the post.

        It also checks if the comment is on someone's clipboard, if it is
        then the comment is not supposed to be viewable.
        """

        comment = cls.objects.filter(
        Q(post__ancestor__users=user), 
        post__ancestor__organization=organization, id=comment_id,
        post__post_clipboard_users__isnull=True).distinct()

        return comment.first()

    def __str__(self):
        return self.data

class CommentFileWrapperMixin(object):
    def duplicate(self, post=None):
        wrapper       = CommentFileWrapper.objects.get(id=self.id)
        wrapper.pk    = None
        wrapper.post  = post
        wrapper.save()
        return wrapper

class CommentFileWrapper(CommentFileWrapperMixin, models.Model):
    """
    """
    organization = models.ForeignKey('core_app.Organization', 
    null=False, on_delete=models.CASCADE)

    comment = models.ForeignKey('Comment', null=True, 
    on_delete=models.CASCADE, blank=True)

    file = models.FileField(
    verbose_name='', help_text='')

class Comment(CommentMixin, models.Model):
    post = models.ForeignKey('post_app.Post', 
    null=False, on_delete=models.CASCADE, related_name='comments')

    owner = models.ForeignKey('core_app.User', 
    null=True, on_delete=models.CASCADE)

    title = models.CharField(null=True, blank=False, 
    default='', verbose_name=_("Title"), 
    max_length=626)

    data = models.TextField(null=True, 
    blank=True, verbose_name=_("Data"), 
    help_text='Markdown content.', default='')

    created = models.DateTimeField(
    auto_now_add=True, null=True)

    html = models.TextField(null=True, blank=True)

class CommentSearchMixin(models.Model):
    class Meta:
        abstract = True

class CommentSearch(CommentSearchMixin):
    pattern  = models.CharField(max_length=255, 
    blank=True, default='', help_text='')

    organization = models.ForeignKey('core_app.Organization', 
    null=False, on_delete=models.CASCADE)

    user = models.ForeignKey('core_app.User',
    null=False, on_delete=models.CASCADE)

    done = models.BooleanField(blank=True, default=False)

    class Meta:
        unique_together = ('user', 'organization', )

class ECreateComment(Event):
    child = models.ForeignKey('post_app.Post', 
    null=True, on_delete=models.CASCADE)

    comment = models.ForeignKey('Comment', 
    null=True, on_delete=models.CASCADE)

    html_template = 'comment_app/e-create-comment.html'

    def __str__(self):
        return self.user.name

class EDeleteComment(Event):
    child = models.ForeignKey('post_app.Post', 
    null=True, on_delete=models.CASCADE)

    comment = models.CharField(null=True, max_length=626)
    html_template = 'comment_app/e-delete-comment.html'

    def __str__(self):
        return self.user.name

class EUpdateComment(Event):
    child = models.ForeignKey('post_app.Post', 
    null=True, on_delete=models.CASCADE)

    comment = models.ForeignKey('Comment', 
    null=True, on_delete=models.CASCADE)

    comment_title = models.CharField(null=True, blank=False, 
    verbose_name=_("Label"), max_length=626)

    comment_html = models.TextField(null=True, blank=True)
    comment_data = models.TextField(blank=True, 
    verbose_name=_("Data"), help_text='Markdown content.', default='')

    html_template = 'comment_app/e-update-comment.html'

    def __str__(self):
        return self.user.name

class ERestoreComment(Event):
    """
    """

    post = models.ForeignKey('post_app.Post', 
    related_name='e_restore_comment0', null=True, on_delete=models.CASCADE)

    comment = models.ForeignKey('Comment', 
    related_name='e_restore_comment1', null=True, on_delete=models.CASCADE)

    event_html    = models.TextField(null=True, blank=True)
    html_template = 'comment_app/e-restore-comment.html'

class EAttachCommentFile(Event):
    """
    """

    filewrapper = models.ForeignKey('CommentFileWrapper', 
    related_name='e_attach_comment_file0', null=True, on_delete=models.CASCADE)

    comment = models.ForeignKey('Comment', 
    related_name='e_attach_comment_file1', null=True, on_delete=models.CASCADE)

    html_template = 'comment_app/e-attach-comment-file.html'

class EDettachCommentFile(Event):
    """
    """
    filename = models.CharField(null=True, max_length=626)

    comment = models.ForeignKey('Comment', 
    related_name='e_dettach_comment_file1', null=True, on_delete=models.CASCADE)

    html_template = 'comment_app/e-dettach-comment-file.html'

# It is not necessary at all bacause comments arent
# copied altogether with posts but it might be necessary
# in the future..
@receiver(pre_delete, sender=CommentFileWrapper)
def delete_filewrapper(sender, instance, **kwargs):
    is_unique = CommentFileWrapper.objects.filter(file=instance.file)
    is_unique = is_unique.count() == 1
    if is_unique: 
        clean_disk(instance)








