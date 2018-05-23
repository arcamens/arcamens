from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.EBitbucketCommit)
admin.site.register(models.BitbucketHook)






