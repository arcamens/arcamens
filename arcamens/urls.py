"""gnosis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic.base import RedirectView
# from django.conf.urls import handler404, handler500

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', RedirectView.as_view(pattern_name='site_app:index')),
     url(r'^core_app/', include('core_app.urls', namespace='core_app')), 
     url(r'^timeline_app/', include('timeline_app.urls', namespace='timeline_app')), 
     url(r'^board_app/', include('board_app.urls', namespace='board_app')), 
     url(r'^comment_app/', include('comment_app.urls', namespace='comment_app')), 
     url(r'^site_app/', include('site_app.urls', namespace='site_app')), 
     url(r'^post_app/', include('post_app.urls', namespace='post_app')), 
     url(r'^timeline_app/', include('timeline_app.urls', namespace='timeline_app')),
     url(r'^paybills/', include('paybills.urls', namespace='paybills')), 
     # url(r'^onesignal/', include('onesignal.urls', namespace='onesignal')), 
    url(r'^board_app/', include('board_app.urls', namespace='board_app')),
    url(r'^card_app/', include('card_app.urls', namespace='card_app')),
    url(r'^snippet_app/', include('snippet_app.urls', namespace='snippet_app')),
    url(r'^note_app/', include('note_app.urls', namespace='note_app')),
    url(r'^jsim/', include('jsim.urls', namespace='jsim')),
    url(r'^bitbucket_app/', include('bitbucket_app.urls', namespace='bitbucket_app')),

    url(r'^list_app/', include('list_app.urls', namespace='list_app')),

]


# handler500 = 'core_app.views.default_error'











