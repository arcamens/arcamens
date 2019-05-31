from django.conf.urls import re_path
from . import views

app_name = 'card_app'
urlpatterns = [
    re_path('list-cards/(?P<list_id>.+)/', views.ListCards.as_view(), name='list-cards'),
    re_path('cut-card/(?P<card_id>.+)/', views.CutCard.as_view(), name='cut-card'),
    re_path('refresh-card-label/(?P<card_id>.+)/', views.RefreshCardLabel.as_view(), name='refresh-card-label'),

    re_path('done/(?P<card_id>.+)/', views.Done.as_view(), name='done'),
    re_path('undo/(?P<card_id>.+)/', views.Undo.as_view(), name='undo'),
    re_path('archive-all/(?P<list_id>.+)/', views.ArchiveAll.as_view(), name='archive-all'),

    re_path('card-worker-information/(?P<peer_id>.+)/(?P<card_id>.+)/', views.CardWorkerInformation.as_view(), name='card-worker-information'),
    re_path('card-tag-information/(?P<tag_id>.+)/(?P<card_id>.+)/', views.CardTagInformation.as_view(), name='card-tag-information'),
    re_path('card-link/(?P<card_id>.+)/', views.CardLink.as_view(), name='card-link'),
    re_path('select-fork-list/(?P<card_id>.+)/', views.SelectForkList.as_view(), name='select-fork-list'),

    re_path('create-card/(?P<ancestor_id>.+)/', views.CreateCard.as_view(), name='create-card'),

    re_path('create-fork/(?P<ancestor_id>.+)/(?P<card_id>.+)/', views.CreateFork.as_view(), name='create-fork'),
    re_path('pull-card-content/(?P<ancestor_id>.+)/(?P<card_id>.+)/', views.PullCardContent.as_view(), name='pull-card-content'),

    re_path('attach-file/(?P<card_id>.+)/', views.AttachFile.as_view(), name='attach-file'),
    re_path('detach-file/(?P<filewrapper_id>.+)/', views.DetachFile.as_view(), name='detach-file'),
    re_path('card-file-download/(?P<filewrapper_id>.+)/', views.CardFileDownload.as_view(), name='card-file-download'),

    re_path('delete-card/(?P<card_id>.+)/', views.DeleteCard.as_view(), name='delete-card'),
    re_path('view-data/(?P<card_id>.+)/', views.ViewData.as_view(), name='view-data'),
    re_path('card-diff/(?P<event_id>.+)/', views.CardDiff.as_view(), name='card-diff'),

    re_path('confirm-card-deletion/(?P<card_id>.+)/', views.ConfirmCardDeletion.as_view(), name='confirm-card-deletion'),
    re_path('set-deadline/(?P<card_id>.+)/', views.SetDeadline.as_view(), name='set-deadline'),

    re_path('update-card/(?P<card_id>.+)/', views.UpdateCard.as_view(), name='update-card'),
    re_path('restore-card/(?P<event_id>.+)/', views.RestoreCard.as_view(), name='restore-card'),

    re_path('alert-card-workers/(?P<card_id>.+)/', views.AlertCardWorkers.as_view(), name='alert-card-workers'),


    re_path('cut-card/(?P<card_id>.+)/', views.CutCard.as_view(), name='cut-card'),
    re_path('copy-card/(?P<card_id>.+)/', views.CopyCard.as_view(), name='copy-card'),
    re_path('setup-card-filter/(?P<list_id>.+)', views.SetupCardFilter.as_view(), name='setup-card-filter'),
    re_path('pin-card/(?P<card_id>.+)/', views.PinCard.as_view(), name='pin-card'),
    re_path('request-card-attention/(?P<peer_id>.+)/(?P<card_id>.+)', views.RequestCardAttention.as_view(), name='request-card-attention'),
    re_path('find/', views.Find.as_view(), name='find'),
    re_path('card-events/(?P<card_id>.+)/', views.CardEvents.as_view(), name='card-events'),
    re_path('unpin/(?P<pin_id>.+)/', views.Unpin.as_view(), name='unpin'),
    re_path('card-priority/(?P<card_id>.+)/', views.CardPriority.as_view(), name='card-priority'),

    re_path('set-card-priority-down/(?P<card0_id>.+)/(?P<card1_id>.+)/', views.SetCardPriorityDown.as_view(), name='set-card-priority-down'),
    re_path('set-card-priority-up/(?P<card0_id>.+)/(?P<card1_id>.+)/', views.SetCardPriorityUp.as_view(), name='set-card-priority-up'),

    re_path('unbind-card-workers/(?P<card_id>.+)/', views.UnbindCardWorkers.as_view(), name='unbind-card-workers'),
    re_path('bind-card-users/(?P<card_id>.+)/', views.BindCardWorkers.as_view(), name='bind-card-workers'),
    re_path('create-card-taskship-user/(?P<card_id>.+)/(?P<user_id>.+)/', views.CreateCardTaskshipUser.as_view(), name='create-card-taskship-user'),
    re_path('delete-card-taskship-user/(?P<card_id>.+)/(?P<user_id>.+)/', views.DeleteCardTaskshipUser.as_view(), name='delete-card-taskship-user'),

    re_path('unbind-card-tags/(?P<card_id>.+)/', views.UnbindCardTags.as_view(), name='unbind-card-tags'),
    re_path('bind-card-tags/(?P<card_id>.+)/', views.BindCardTags.as_view(), name='bind-card-tags'),
    re_path('create-card-tagship/(?P<card_id>.+)/(?P<tag_id>.+)/', views.CreateCardTagship.as_view(), name='create-card-tagship'),
    re_path('delete-card-tagship/(?P<card_id>.+)/(?P<tag_id>.+)/', views.DeleteCardTagship.as_view(), name='delete-card-tagship'),

]


