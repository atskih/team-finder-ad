from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import Count

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("email", "name", "surname", "projects_count", "is_staff", "is_active")
    search_fields = ("email", "name", "surname")
    filter_horizontal = ("groups", "user_permissions")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Profile",
            {"fields": ("name", "surname", "avatar", "phone", "github_url", "about")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "surname",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(projects_count_value=Count("participated_projects", distinct=True))

    @admin.display(description="Projects")
    def projects_count(self, obj):
        return getattr(obj, "projects_count_value", 0)
