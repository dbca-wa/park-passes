from django.contrib.gis import admin

from parkpasses.components.main import models

admin.site.index_template = "admin-index.html"
admin.autodiscover()


@admin.register(models.EmailUser)
class EmailUserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    ordering = ("email",)
    search_fields = ("id", "email", "first_name", "last_name")

    def has_change_permission(self, request, obj=None):
        if obj is None:  # and obj.status > 1:
            return True
        return None

    def has_delete_permission(self, request, obj=None):
        return None
