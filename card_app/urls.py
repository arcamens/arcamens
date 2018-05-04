from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^list-cards/(?P<list_id>.+)/', views.ListCards.as_view(), name='list-cards'),
    url(r'^cut-card/(?P<card_id>.+)/', views.CutCard.as_view(), name='cut-card'),
    url(r'^done/(?P<card_id>.+)/', views.Done.as_view(), name='done'),
    url(r'^undo/(?P<card_id>.+)/', views.Undo.as_view(), name='undo'),
    url(r'^card-worker-information/(?P<peer_id>.+)/(?P<card_id>.+)/', views.CardWorkerInformation.as_view(), name='card-worker-information'),
    url(r'^card-tag-information/(?P<tag_id>.+)/(?P<card_id>.+)/', views.CardTagInformation.as_view(), name='card-tag-information'),
    url(r'^card-link/(?P<card_id>.+)/', views.CardLink.as_view(), name='card-link'),
    url(r'^select-fork-list/(?P<card_id>.+)/', views.SelectForkList.as_view(), name='select-fork-list'),
    # url(r'^select-fork-timeline/(?P<card_id>.+)/', views.SelectForkTimeline.as_view(), name='select-fork-timeline'),

    url(r'^create-card/(?P<ancestor_id>.+)/(?P<card_id>.+)/', views.CreateCard.as_view(), name='create-card'),
    url(r'^create-card/(?P<ancestor_id>.+)/', views.CreateCard.as_view(), name='create-card'),
    url(r'^create-fork/(?P<ancestor_id>.+)/(?P<card_id>.+)/(?P<fork_id>.+)/', views.CreateFork.as_view(), name='create-fork'),
    url(r'^create-fork/(?P<ancestor_id>.+)/(?P<card_id>.+)/', views.CreateFork.as_view(), name='create-fork'),
    # url(r'^pull-post-content/(?P<card_id>.+)/(?P<fork_id>.+)/', views.PullPostContent.as_view(), name='pull-post-content'),
    url(r'^pull-card-content/(?P<card_id>.+)/(?P<fork_id>.+)/', views.PullCardContent.as_view(), name='pull-card-content'),

    # url(r'^create-post-fork-/(?P<ancestor_id>.+)/(?P<card_id>.+)/(?P<fork_id>.+)/', views.CreatePostFork.as_view(), name='create-post-fork'),
    # url(r'^create-post-fork/(?P<ancestor_id>.+)/(?P<card_id>.+)/', views.CreatePostFork.as_view(), name='create-post-fork'),

    url(r'^attach-image/(?P<card_id>.+)/', views.AttachImage.as_view(), name='attach-image'),
    url(r'^attach-file/(?P<card_id>.+)/', views.AttachFile.as_view(), name='attach-file'),
    url(r'^detach-file/(?P<filewrapper_id>.+)/', views.DetachFile.as_view(), name='detach-file'),
    url(r'^delete-card/(?P<card_id>.+)/', views.DeleteCard.as_view(), name='delete-card'),
    url(r'^cancel-card-creation/(?P<card_id>.+)/', views.CancelCardCreation.as_view(), name='cancel-card-creation'),
    url(r'^view-data/(?P<card_id>.+)/', views.ViewData.as_view(), name='view-data'),
    url(r'^confirm-card-deletion/(?P<card_id>.+)/', views.ConfirmCardDeletion.as_view(), name='confirm-card-deletion'),

    url(r'^update-card/(?P<card_id>.+)/', views.UpdateCard.as_view(), name='update-card'),
    url(r'^alert-card-workers/(?P<card_id>.+)/', views.AlertCardWorkers.as_view(), name='alert-card-workers'),


    url(r'^cut-card/(?P<card_id>.+)/', views.CutCard.as_view(), name='cut-card'),
    url(r'^copy-card/(?P<card_id>.+)/', views.CopyCard.as_view(), name='copy-card'),
    url(r'^setup-card-filter/(?P<list_id>.+)', views.SetupCardFilter.as_view(), name='setup-card-filter'),
    url(r'^manage-card-workers/(?P<card_id>.+)/', views.ManageCardWorkers.as_view(), name='manage-card-workers'),
    url(r'^bind-card-worker/(?P<card_id>.+)/(?P<user_id>.+)', views.BindCardWorker.as_view(), name='bind-card-worker'),
    url(r'^unbind-card-worker/(?P<card_id>.+)/(?P<user_id>.+)', views.UnbindCardWorker.as_view(), name='unbind-card-worker'),
    url(r'^pin-card/(?P<card_id>.+)/', views.PinCard.as_view(), name='pin-card'),
    url(r'^relate-card/(?P<card0_id>.+)/(?P<card1_id>.+)/', views.RelateCard.as_view(), name='relate-card'),
    url(r'^unrelate-card/(?P<card0_id>.+)/(?P<card1_id>.+)/', views.UnrelateCard.as_view(), name='unrelate-card'),
    url(r'^manage-card-relations/(?P<card_id>.+)/', views.ManageCardRelations.as_view(), name='manage-card-relations'),
    url(r'^manage-card-tags/(?P<card_id>.+)/', views.ManageCardTags.as_view(), name='manage-card-tags'),
    url(r'^bind-card-tag/(?P<card_id>.+)/(?P<tag_id>.+)', views.BindCardTag.as_view(), name='bind-card-tag'),
    url(r'^unbind-card-tag/(?P<card_id>.+)/(?P<tag_id>.+)', views.UnbindCardTag.as_view(), name='unbind-card-tag'),
    url(r'^request-card-attention/(?P<peer_id>.+)/(?P<card_id>.+)', views.RequestCardAttention.as_view(), name='request-card-attention'),
    url(r'^card/(?P<card_id>.+)/', views.Card.as_view(), name='card'),
    url(r'^undo-clipboard/(?P<card_id>.+)/', views.UndoClipboard.as_view(), name='undo-clipboard'),
    url(r'^list-all-tasks/', views.ListAllTasks.as_view(), name='list-all-tasks'),
    url(r'^find/', views.Find.as_view(), name='find'),
    url(r'^card-events/(?P<card_id>.+)/', views.CardEvents.as_view(), name='card-events'),

]









