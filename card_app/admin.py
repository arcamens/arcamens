from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Card)
admin.site.register(models.ECreateCard)
admin.site.register(models.EUpdateCard)
admin.site.register(models.CardPin)
admin.site.register(models.CardTagship)
admin.site.register(models.CardTaskship)
admin.site.register(models.CardSearch)
admin.site.register(models.CardClipboard)
admin.site.register(models.CardFileWrapper)
admin.site.register(models.ERelateCard)
admin.site.register(models.EUnrelateCard)
admin.site.register(models.EBindCardWorker)
admin.site.register(models.EUnbindCardWorker)
admin.site.register(models.ECreateFork)
admin.site.register(models.EAttachCardFile)
admin.site.register(models.EDettachCardFile)
admin.site.register(models.EDeleteCard)
admin.site.register(models.CardFilter)
admin.site.register(models.EBindTagCard)
admin.site.register(models.EUnbindTagCard)
admin.site.register(models.ECutCard)
admin.site.register(models.ESetCardPriorityUp)
admin.site.register(models.ESetCardPriorityDown)
admin.site.register(models.EArchiveCard)
admin.site.register(models.EUnarchiveCard)
admin.site.register(models.ECopyCard)
admin.site.register(models.ESetCardDeadline)
admin.site.register(models.EArrivedCardDeadline)





