from django.contrib import admin

from .models import Category, CodingDetail, Pattern, Question, QuestionOption, Solution, Topic, TopicSection


class TopicSectionInline(admin.TabularInline):
    model = TopicSection
    extra = 0
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "glyph", "order"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [TopicSectionInline]


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "section", "order"]
    list_filter = ["category"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Pattern)
class PatternAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order"]
    prepopulated_fields = {"slug": ("name",)}


class CodingDetailInline(admin.StackedInline):
    model = CodingDetail
    can_delete = False


class SolutionInline(admin.StackedInline):
    model = Solution
    extra = 0


class OptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["title", "topic", "question_type", "difficulty", "is_published", "order"]
    list_filter = ["question_type", "difficulty", "is_published", "topic__category", "topic"]
    search_fields = ["title", "slug", "statement"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["patterns"]
    list_select_related = ["topic"]
    inlines = [CodingDetailInline, SolutionInline, OptionInline]
