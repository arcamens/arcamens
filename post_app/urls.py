from django.urls import path
from . import views

app_name = 'post_app'
urlpatterns = [
    path('post/<int:post_id>/', views.Post.as_view(), name='post'),

    path('refresh-post/<int:post_id>/', views.RefreshPost.as_view(), name='refresh-post'),

    path('post-link/<int:post_id>/', views.PostLink.as_view(), name='post-link'),

    path('done/<int:post_id>/', views.Done.as_view(), name='done'),
    path('undo/<int:post_id>/', views.Undo.as_view(), name='undo'),

    path('create-post/<int:ancestor_id>/', views.CreatePost.as_view(), name='create-post'),
    path('update-post/<int:post_id>/', views.UpdatePost.as_view(), name='update-post'),
    path('post-diff/<int:event_id>/', views.PostDiff.as_view(), name='post-diff'),

    path('attach-file/<int:post_id>/', views.AttachFile.as_view(), name='attach-file'),
    path('detach-file/<int:filewrapper_id>/', views.DetachFile.as_view(), name='detach-file'),
    path('post-file-download/<int:filewrapper_id>/', views.PostFileDownload.as_view(), name='post-file-download'),

    path('delete-post/<int:post_id>/', views.DeletePost.as_view(), name='delete-post'),
    path('delete-post/<int:post_id>/', views.DeletePost.as_view(), name='delete-post'),
    path('post-link/<int:post_id>/', views.PostLink.as_view(), name='post-link'),

    path('post-tag-information/(?P<tag_id>.+)/<int:post_id>/', views.PostTagInformation.as_view(), name='post-tag-information'),
    path('like-post/<int:post_id>/', views.LikePost.as_view(), name='like-post'),
    path('unlike-post/<int:post_id>/', views.UnlikePost.as_view(), name='unlike-post'),

    path('unbind-post-tags/<int:post_id>/', views.UnbindPostTags.as_view(), name='unbind-post-tags'),
    path('bind-post-tags/<int:post_id>/', views.BindPostTags.as_view(), name='bind-post-tags'),
    path('create-post-tagship/<int:post_id>/<int:tag_id>/', views.CreatePostTagship.as_view(), name='create-post-tagship'),
    path('delete-post-tagship/<int:post_id>/<int:tag_id>/', views.DeletePostTagship.as_view(), name='delete-post-tagship'),

    path('setup-post-filter/(?P<group_id>.+)', views.SetupPostFilter.as_view(), name='setup-post-filter'),
    path('find/', views.Find.as_view(), name='find'),

    path('cut-post/<int:post_id>/', views.CutPost.as_view(), name='cut-post'),
    path('copy-post/<int:post_id>/', views.CopyPost.as_view(), name='copy-post'),
    path('confirm-post-deletion/<int:post_id>/', views.ConfirmPostDeletion.as_view(), name='confirm-post-deletion'),
    path('select-fork-list/<int:post_id>/', views.SelectForkList.as_view(), name='select-fork-list'),
    path('create-post-fork/<int:ancestor_id>/<int:post_id>/', views.CreatePostFork.as_view(), name='create-post-fork'),
    path('pull-card-content/<int:ancestor_id>/<int:post_id>/', views.PullCardContent.as_view(), name='pull-card-content'),
    path('post-events/<int:post_id>/', views.PostEvents.as_view(), name='post-events'),
    path('pin-post/<int:post_id>/', views.PinPost.as_view(), name='pin-post'),
    path('unpin/<int:pin_id>/', views.Unpin.as_view(), name='unpin'),
    path('set-post-priority-down/<int:post0_id>/<int:post1_id>/', views.SetPostPriorityDown.as_view(), name='set-post-priority-down'),
    path('set-post-priority-up/<int:post0_id>/<int:post1_id>/', views.SetPostPriorityUp.as_view(), name='set-post-priority-up'),
    path('post-priority/<int:post_id>/', views.PostPriority.as_view(), name='post-priority'),
    path('restore-post/(?P<event_id>.+)/', views.RestorePost.as_view(), name='restore-post'),

]






