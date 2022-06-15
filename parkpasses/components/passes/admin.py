from django.contrib import admin

from parkpasses.components.passes.models import PassType, PassTypePricingWindow


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


class PassTypePricingWindowAdmin(admin.ModelAdmin):
    model = PassTypePricingWindow
    list_display = (
        "name",
        "pass_type",
        "datetime_start",
        "datetime_expiry",
    )
    ordering = [
        "datetime_start",
    ]


admin.site.register(PassTypePricingWindow, PassTypePricingWindowAdmin)
