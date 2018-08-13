from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Group)
admin.site.register(models.ECreateGroup)
admin.site.register(models.EDeleteGroup)
admin.site.register(models.GroupPin)
admin.site.register(models.Groupship)
admin.site.register(models.EUpdateGroup)
admin.site.register(models.EBindGroupUser)
admin.site.register(models.EUnbindGroupUser)
admin.site.register(models.EPastePost)

