from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.ListPin)
admin.site.register(models.List)
admin.site.register(models.ECreateList)
admin.site.register(models.EUpdateList)
admin.site.register(models.EDeleteList)
admin.site.register(models.ECutList)
admin.site.register(models.ECopyList)
admin.site.register(models.EPasteCard)


