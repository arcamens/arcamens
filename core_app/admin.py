from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Organization)
admin.site.register(models.Invite)
admin.site.register(models.EventFilter)
admin.site.register(models.EDisabledAccount)
admin.site.register(models.ERemoveOrganizationUser)
admin.site.register(models.EUpdateOrganization)
admin.site.register(models.Clipboard)
admin.site.register(models.UserFilter)
admin.site.register(models.EUnbindUserTag)
admin.site.register(models.EDeleteTag)
admin.site.register(models.ECreateTag)
admin.site.register(models.EBindUserTag)
admin.site.register(models.EJoinOrganization)
admin.site.register(models.EShout)
admin.site.register(models.EInviteUser)
admin.site.register(models.Tag)
admin.site.register(models.Event)
admin.site.register(models.UserTagship)
admin.site.register(models.Period)
admin.site.register(models.Membership)









