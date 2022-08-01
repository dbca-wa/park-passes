import logging

from django.contrib import admin

from parkpasses import settings
from parkpasses.components.passes.models import (
    Pass,
    PassCancellation,
    PassTemplate,
    PassType,
    PassTypePricingWindow,
    PassTypePricingWindowOption,
)

logger = logging.getLogger(__name__)


class PassCancellationInline(admin.TabularInline):
    model = PassCancellation


class PassAdmin(admin.ModelAdmin):
    model = Pass
    fields = [
        "user",
        "in_cart",
        "processing_status",
        "sold_via",
        "first_name",
        "last_name",
        "email",
        "option",
        "park_group",
        "vehicle_registration_1",
        "vehicle_registration_2",
        "prevent_further_vehicle_updates",
        "datetime_start",
        "datetime_expiry",
        "renew_automatically",
    ]
    list_display = (
        "pass_number",
        "sold_via",
        "park_pass_pdf",
        "processing_status",
        "pass_type",
        "pricing_window",
        "price",
        "full_name",
        "vehicle_registration_1",
        "vehicle_registration_2",
        "datetime_start",
    )
    autocomplete_fields = ("sold_via",)
    readonly_fields = [
        "pass_number",
        "first_name",
        "last_name",
        "email",
        "datetime_expiry",
    ]
    ordering = [
        "datetime_created",
    ]
    inlines = [
        PassCancellationInline,
    ]

    def get_fields(self, request, obj=None):
        if obj:
            if (
                not settings.ANNUAL_LOCAL_PASS
                == obj.option.pricing_window.pass_type.name
            ):
                if "park_group" in self.fields:
                    self.fields.remove("park_group")
            else:
                if "park_group" not in self.fields:
                    self.fields.insert(7, "park_group")
        return self.fields

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing
            return self.readonly_fields
        return ()


admin.site.register(Pass, PassAdmin)


class PassTypeAdmin(admin.ModelAdmin):
    model = PassType
    list_display = (
        "name",
        "display_name",
        "display_order",
        "display_retailer",
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


class PassTypePricingWindowOptionInline(admin.TabularInline):
    model = PassTypePricingWindowOption


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
    inlines = [
        PassTypePricingWindowOptionInline,
    ]
    readonly_fields = [
        "datetime_expiry",
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing
            # Don't allow user to edit expiry date of default payment window
            if not obj.datetime_expiry:
                return self.readonly_fields
        return ()


admin.site.register(PassTypePricingWindow, PassTypePricingWindowAdmin)


class PassTemplateAdmin(admin.ModelAdmin):
    model = PassTemplate
    list_display = (
        "template",
        "version",
    )
    ordering = [
        "-version",
    ]


admin.site.register(PassTemplate, PassTemplateAdmin)
