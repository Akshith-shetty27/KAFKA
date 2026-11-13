from django.contrib import admin

from .models import ActivityEvent, QuestionProgress


@admin.register(QuestionProgress)
class QuestionProgressAdmin(admin.ModelAdmin):
    list_display = ["user", "question", "status", "answer_count", "is_correct", "updated_at"]
    list_filter = ["status"]
    search_fields = ["user__email", "question__title"]
    list_select_related = ["user", "question"]
    raw_id_fields = ["user", "question", "selected_option"]


@admin.register(ActivityEvent)
class ActivityEventAdmin(admin.ModelAdmin):
    list_display = ["user", "event_type", "question", "is_correct", "created_at"]
    list_filter = ["event_type"]
    search_fields = ["user__email"]
    list_select_related = ["user", "question"]
    raw_id_fields = ["user", "question"]
    date_hierarchy = "created_at"
