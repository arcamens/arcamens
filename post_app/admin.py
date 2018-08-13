from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Post)
admin.site.register(models.GlobalPostFilter)
admin.site.register(models.PostTaskship)
admin.site.register(models.PostTagship)
admin.site.register(models.PostFilter)
admin.site.register(models.PostFileWrapper)
admin.site.register(models.ECreatePost)
admin.site.register(models.EArchivePost)
admin.site.register(models.EUnarchivePost)
admin.site.register(models.EDeletePost)
admin.site.register(models.ECutPost)
admin.site.register(models.ECopyPost)
admin.site.register(models.EUpdatePost)
admin.site.register(models.EAssignPost)
admin.site.register(models.EUnassignPost)
admin.site.register(models.EBindTagPost)
admin.site.register(models.EUnbindTagPost)
admin.site.register(models.ECreatePostFork)
admin.site.register(models.PostPin)
admin.site.register(models.EAttachPostFile)
admin.site.register(models.EDettachPostFile)
admin.site.register(models.ESetPostPriorityUp)
admin.site.register(models.ESetPostPriorityDown)



