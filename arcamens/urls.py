from django.urls import path, include
from django.contrib import admin
from django.views.generic.base import RedirectView

urlpatterns = [
    path(r'admin/', admin.site.urls),
     path(r'core_app/', include('core_app.urls')),
     path(r'group_app/', include('group_app.urls')),
     path(r'board_app/', include('board_app.urls')),
     path(r'feedback_app/', include('feedback_app.urls')),
     path(r'site_app/', include('site_app.urls')),
     path(r'cash_app/', include('cash_app.urls')),

     path(r'post_app/', include('post_app.urls', namespace='post_app')),
     path(r'paybills/', include('paybills.urls')),
     path(r'onesignal/', include('onesignal.urls')),
    path(r'card_app/', include('card_app.urls')),
    path(r'comment_app/', include('comment_app.urls')),
    path(r'note_app/', include('note_app.urls')),
    path(r'jscroll/', include('jscroll.urls')),

    path(r'bitbucket_app/', include('bitbucket_app.urls')),
    path(r'github_app/', include('github_app.urls')),

    path(r'list_app/', include('list_app.urls')),

    path(r'', RedirectView.as_view(pattern_name='site_app:index')),
]


# handler500 = 'core_app.views.default_error'


















