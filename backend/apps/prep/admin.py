from django.contrib import admin

from .models import PlanItem, PlanPhase, PreparationPlan


class PlanPhaseInline(admin.TabularInline):
    model = PlanPhase
    extra = 0
    fields = ("order", "kind", "title")
    show_change_link = True


@admin.register(PreparationPlan)
class PreparationPlanAdmin(admin.ModelAdmin):
    list_display = ("role", "company", "user", "created_at", "model")
    list_filter = ("provider",)
    search_fields = ("role", "company", "user__email")
    raw_id_fields = ("user",)
    readonly_fields = ("created_at", "updated_at", "input_tokens", "output_tokens")
    inlines = [PlanPhaseInline]


class PlanItemInline(admin.StackedInline):
    model = PlanItem
    extra = 0
    filter_horizontal = ("topics", "patterns")


@admin.register(PlanPhase)
class PlanPhaseAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "plan", "order")
    inlines = [PlanItemInline]
