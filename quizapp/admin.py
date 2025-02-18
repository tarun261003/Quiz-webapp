from django.contrib import admin
from . import models
from .models import ExamControl
admin.site.register(ExamControl)

admin.site.register(models.question)
admin.site.register(models.fraud_model)
admin.site.register(models.leaderboard)