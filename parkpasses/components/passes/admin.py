from django.contrib import admin

from parkpasses.components.passes.models import PassType


class PassTypeAdmin(admin.ModelAdmin):
    model = PassType
    list_display = (
        "name",
        "display_name",
        "display_order",
        "display_externally",
    )
    ordering = [
        "display_order",
    ]
    readonly_fields = [
        "name",
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing
            return self.readonly_fields
        return ()


admin.site.register(PassType, PassTypeAdmin)
