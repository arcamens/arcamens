from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^post/(?P<post_id>.+)/', views.Post.as_view(), name='post'),
    url(r'^post-link/(?P<post_id>.+)/', views.PostLink.as_view(), name='post-link'),
    url(r'^alert-post-workers/(?P<post_id>.+)/', views.AlertPostWorkers.as_view(), name='alert-post-workers'),

    url(r'^done/(?P<post_id>.+)/', views.Done.as_view(), name='done'),
    url(r'^undo/(?P<post_id>.+)/', views.Undo.as_view(), name='undo'),

    url(r'^create-post/(?P<ancestor_id>.+)/(?P<post_id>.+)/', views.CreatePost.as_view(), name='create-post'),
    url(r'^create-post/(?P<ancestor_id>.+)/', views.CreatePost.as_view(), name='create-post'),
    url(r'^update-post/(?P<post_id>.+)/', views.UpdatePost.as_view(), name='update-post'),
    url(r'^attach-file/(?P<post_id>.+)/', views.AttachFile.as_view(), name='attach-file'),
    url(r'^detach-file/(?P<filewrapper_id>.+)/', views.DetachFile.as_view(), name='detach-file'),
    url(r'^delete-post/(?P<post_id>.+)/', views.DeletePost.as_view(), name='delete-post'),
    url(r'^delete-post/(?P<post_id>.+)/', views.DeletePost.as_view(), name='delete-post'),
    url(r'^post-link/(?P<post_id>.+)/', views.PostLink.as_view(), name='post-link'),

    url(r'^list-assignments/(?P<user_id>.+)/', views.ListAssignments.as_view(), name='list-assignments'),
    url(r'^post-worker-information/(?P<peer_id>.+)/(?P<post_id>.+)/', views.PostWorkerInformation.as_view(), name='post-worker-information'),
    url(r'^post-tag-information/(?P<tag_id>.+)/(?P<post_id>.+)/', views.PostTagInformation.as_view(), name='post-tag-information'),

    url(r'^manage-post-workers/(?P<post_id>.+)/', views.ManagePostWorkers.as_view(), name='manage-post-workers'),
    url(r'^assign-post-user/(?P<post_id>.+)/(?P<user_id>.+)', views.AssignPostUser.as_view(), name='assign-post-user'),
    url(r'^unassign-post-user/(?P<post_id>.+)/(?P<user_id>.+)', views.UnassignPostUser.as_view(), name='unassign-post-user'),
    url(r'^setup-post-filter/(?P<timeline_id>.+)', views.SetupPostFilter.as_view(), name='setup-post-filter'),
    url(r'^setup-global-posts-filter/', views.SetupGlobalPostFilter.as_view(), name='setup-global-post-filter'),
    url(r'^setup-assignment-filter/', views.SetupAssignmentFilter.as_view(), name='setup-assignment-filter'),

    url(r'^cut-post/(?P<post_id>.+)/', views.CutPost.as_view(), name='cut-post'),
    url(r'^copy-post/(?P<post_id>.+)/', views.CopyPost.as_view(), name='copy-post'),
    url(r'^manage-post-tags/(?P<post_id>.+)/', views.ManagePostTags.as_view(), name='manage-post-tags'),
    url(r'^bind-post-tag/(?P<post_id>.+)/(?P<tag_id>.+)', views.BindPostTag.as_view(), name='bind-post-tag'),
    url(r'^unbind-post-tag/(?P<post_id>.+)/(?P<tag_id>.+)', views.UnbindPostTag.as_view(), name='unbind-post-tag'),
    url(r'^cancel-post-creation/(?P<post_id>.+)/', views.CancelPostCreation.as_view(), name='cancel-post-creation'),
    url(r'^request-post-attention/(?P<peer_id>.+)/(?P<post_id>.+)', views.RequestPostAttention.as_view(), name='request-post-attention'),
    url(r'^confirm-post-deletion/(?P<post_id>.+)/', views.ConfirmPostDeletion.as_view(), name='confirm-post-deletion'),
    url(r'^undo-clipboard/(?P<post_id>.+)/', views.UndoClipboard.as_view(), name='undo-clipboard'),
    url(r'^select-fork-list/(?P<post_id>.+)/', views.SelectForkList.as_view(), name='select-fork-list'),
    url(r'^create-fork/(?P<ancestor_id>.+)/(?P<post_id>.+)/(?P<fork_id>.+)/', views.CreateFork.as_view(), name='create-fork'),
    url(r'^create-fork/(?P<ancestor_id>.+)/(?P<post_id>.+)/', views.CreateFork.as_view(), name='create-fork'),

]






