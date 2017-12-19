from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^post/(?P<post_id>.+)/', views.Post.as_view(), name='post'),
    url(r'^done/(?P<post_id>.+)/', views.Done.as_view(), name='done'),
    url(r'^create-post/(?P<ancestor_id>.+)/(?P<post_id>.+)/', views.CreatePost.as_view(), name='create-post'),
    url(r'^create-post/(?P<ancestor_id>.+)/', views.CreatePost.as_view(), name='create-post'),
    url(r'^update-post/(?P<post_id>.+)/', views.UpdatePost.as_view(), name='update-post'),
    url(r'^attach-file/(?P<post_id>.+)/', views.AttachFile.as_view(), name='attach-file'),
    url(r'^detach-file/(?P<filewrapper_id>.+)/', views.DetachFile.as_view(), name='detach-file'),
    url(r'^delete-post/(?P<post_id>.+)/', views.DeletePost.as_view(), name='delete-post'),
    url(r'^delete-post/(?P<post_id>.+)/', views.DeletePost.as_view(), name='delete-post'),
    url(r'^e-create-post/(?P<event_id>.+)/', views.ECreatePost.as_view(), name='e-create-post'),
    url(r'^e-update-post/(?P<event_id>.+)/', views.EUpdatePost.as_view(), name='e-update-post'),
    url(r'^e-delete-post/(?P<event_id>.+)/', views.EDeletePost.as_view(), name='e-delete-post'),
    url(r'^list-assignments/(?P<user_id>.+)/', views.ListAssignments.as_view(), name='list-assigments'),
    url(r'^manage-post-workers/(?P<post_id>.+)/', views.ManagePostWorkers.as_view(), name='manage-post-workers'),
    url(r'^assign-post-user/(?P<post_id>.+)/(?P<user_id>.+)', views.AssignPostUser.as_view(), name='assign-post-user'),
    url(r'^unassign-post-user/(?P<post_id>.+)/(?P<user_id>.+)', views.UnassignPostUser.as_view(), name='unassign-post-user'),
    url(r'^setup-post-filter/(?P<timeline_id>.+)', views.SetupPostFilter.as_view(), name='setup-post-filter'),
    url(r'^setup-global-posts-filter/', views.SetupGlobalPostFilter.as_view(), name='setup-global-post-filter'),
    url(r'^cut-post/(?P<post_id>.+)/', views.CutPost.as_view(), name='cut-post'),
    url(r'^copy-post/(?P<post_id>.+)/', views.CopyPost.as_view(), name='copy-post'),
    url(r'^bind-tag/(?P<post_id>.+)/', views.BindTag.as_view(), name='bind-tag'),

]





