"""
admin.py

This page is used to register PMS models with admins site.
"""
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Comment, EmployeeKeyResult, Period, EmployeeObjective
from .models import (
    Question,
    QuestionTemplate,
    Feedback,
    Answer,
    KeyResultFeedback,
    QuestionOptions,
)


# Register your models here.

objective = [Period]
feedback = [Question, QuestionTemplate, Feedback, Answer, QuestionOptions]
admin.site.register(EmployeeObjective, SimpleHistoryAdmin)
admin.site.register(EmployeeKeyResult, SimpleHistoryAdmin)
admin.site.register(objective)
admin.site.register(feedback)
admin.site.register(KeyResultFeedback)
admin.site.register(Comment, SimpleHistoryAdmin)
