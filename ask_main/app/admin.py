from django.contrib import admin
from app import models

admin.site.register(models.Profile)
admin.site.register(models.LikeQuestion)
admin.site.register(models.DislikeQuestion)
admin.site.register(models.DislikeAnswer)
admin.site.register(models.LikeAnswer)
admin.site.register(models.Tag)
admin.site.register(models.Question)
admin.site.register(models.Answer)