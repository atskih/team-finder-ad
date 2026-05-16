from django.contrib import admin

from .models import Project, Skill


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "status", "created_at", "skills_list")
    list_filter = ("status", "created_at")
    search_fields = (
        "name",
        "description",
        "owner__email",
        "owner__name",
        "owner__surname",
    )
    filter_horizontal = ("participants", "skills")

    @admin.display(description="Skills")
    def skills_list(self, obj):
        return ", ".join(obj.skills.values_list("name", flat=True))


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
