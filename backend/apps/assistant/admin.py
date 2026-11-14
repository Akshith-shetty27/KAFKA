from django.contrib import admin

from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ["role", "mode", "hint_level", "status", "content", "model", "input_tokens", "output_tokens", "created_at"]
    readonly_fields = fields


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "question", "updated_at"]
    search_fields = ["title", "user__email"]
    list_select_related = ["user", "question"]
    raw_id_fields = ["user", "question"]
    inlines = [MessageInline]
