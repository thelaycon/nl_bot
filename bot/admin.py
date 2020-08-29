from django.contrib import admin
from . import models



admin.site.register(models.BoardReplyJob)
admin.site.register(models.FrontPageMonitorJob)
admin.site.register(models.ThreadReplyJob)
admin.site.register(models.Profile)
admin.site.register(models.NairalandAccount)

