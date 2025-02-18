from django.contrib import admin
from . import models
from .models import ExamControl
from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Question

@admin.register(Question)
class QuestionAdmin(MarkdownxModelAdmin):
    pass
admin.site.register(ExamControl)
admin.site.unregister(Question)
admin.site.register(models.Question)
admin.site.register(models.fraud_model)
admin.site.register(models.leaderboard)