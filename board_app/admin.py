from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Board)
admin.site.register(models.Boardship)
admin.site.register(models.BoardPin)
admin.site.register(models.EBindBoardUser)
admin.site.register(models.EUnbindBoardUser)
admin.site.register(models.EUpdateBoard)
admin.site.register(models.ECreateBoard)
admin.site.register(models.EDeleteBoard)
admin.site.register(models.EPasteList)






