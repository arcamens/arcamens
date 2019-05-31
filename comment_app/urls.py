from django.urls import path
from . import views

app_name = 'comment_app'

urlpatterns = [
    path('create-comment/<int:post_id>/', views.CreateComment.as_view(), name='create-comment'),
    path('update-comment/<int:comment_id>/', views.UpdateComment.as_view(), name='update-comment'),
    path('comment/<int:comment_id>/', views.Comment.as_view(), name='comment'),
    path('delete-comment/<int:comment_id>/', views.DeleteComment.as_view(), name='delete-comment'),

    path('attach-file/<int:comment_id>/', views.AttachFile.as_view(), name='attach-file'),
    path('detach-file/<int:filewrapper_id>/', views.DetachFile.as_view(), name='detach-file'),
    path('comment-file-download/<int:filewrapper_id>/', views.CommentFileDownload.as_view(), name='comment-file-download'),
    path('comment-diff/<int:event_id>/', views.CommentDiff.as_view(), name='comment-diff'),
    path('restore-comment/<int:event_id>/', views.RestoreComment.as_view(), name='restore-comment'),
    path('comment-events/<int:comment_id>/', views.CommentEvents.as_view(), name='comment-events'),

    path('comment-link/<int:comment_id>/', views.CommentLink.as_view(), name='comment-link'),
    path('find/', views.Find.as_view(), name='find'),

]



