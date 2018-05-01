from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Organization)
admin.site.register(models.Invite)
admin.site.register(models.NodeFilter)




