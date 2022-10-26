import logging

from django.contrib import admin
from django.utils.html import format_html

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
    fields = [
        "cancellation_reason",
        "datetime_cancelled",
    ]
    readonly_fields = ["datetime_cancelled"]


class PassAdmin(admin.ModelAdmin):
    model = Pass
    fields = [
        "user",
        "in_cart",
        "purchase_email_sent",
        "processing_status",
        "sold_via",
        "first_name",
        "last_name",
        "email",
        "company",
        "address_line_1",
        "address_line_2",
        "suburb",
        "state",
        "mobile",
        "rac_member_number",
        "option",
        "park_group",
        "postcode",
        "vehicle_registration_1",
        "vehicle_registration_2",
        "prevent_further_vehicle_updates",
        "date_start",
        "date_expiry",
        "renew_automatically",
        "datetime_created",
        "datetime_updated",
    ]
    list_display = (
        "pass_number",
        "sold_via",
        "park_pass_pdf_secure",
        "processing_status",
        "pass_type",
        "pricing_window",
        "price",
        "full_name",
        "vehicle_registration_1",
        "vehicle_registration_2",
        "date_start",
    )
    autocomplete_fields = ("sold_via",)
    readonly_fields = [
        "pass_number",
        "first_name",
        "last_name",
        "email",
        "date_expiry",
        "datetime_created",
        "datetime_updated",
    ]
    ordering = [
        "-id",
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

    def park_pass_pdf_secure(self, instance):
        value_link = (
            f"/api/passes/internal/passes/{instance.id}/retrieve-park-pass-pdf/"
        )
        value_desc = str(instance.park_pass_pdf)
        return format_html('<a href="{}" target="blank">{}</a>', value_link, value_desc)


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
        "slug",
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
        "date_start",
        "date_expiry",
    )
    ordering = [
        "date_start",
    ]
    inlines = [
        PassTypePricingWindowOptionInline,
    ]
    readonly_fields = [
        "date_expiry",
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing
            # Don't allow user to edit expiry date of default payment window
            if not obj.date_expiry:
                return self.readonly_fields
        return ()


admin.site.register(PassTypePricingWindow, PassTypePricingWindowAdmin)


class PassTemplateAdmin(admin.ModelAdmin):
    model = PassTemplate
    list_display = (
        "id",
        "template_secure",
        "version",
    )
    ordering = [
        "-version",
    ]

    def template_secure(self, instance):
        value_link = f"/api/passes/pass-templates/{instance.id}/retrieve-pass-template/"
        value_desc = str(instance.template)
        return format_html('<a href="{}" target="blank">{}</a>', value_link, value_desc)


admin.site.register(PassTemplate, PassTemplateAdmin)
