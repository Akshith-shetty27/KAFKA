from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User, UserProfile


class EmailUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",)


class EmailUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"


class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Django's UserAdmin, adjusted for a model without `username`."""

    form = EmailUserChangeForm
    add_form = EmailUserCreationForm
    inlines = [ProfileInline]
    ordering = ["email"]
    list_display = ["email", "first_name", "last_name", "is_staff", "is_active", "date_joined"]
    search_fields = ["email", "first_name", "last_name"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),)
