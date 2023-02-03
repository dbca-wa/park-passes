import logging

from django.contrib import admin
from django.utils.html import format_html

from parkpasses import settings
from parkpasses.components.passes.models import (
    Pass,
    PassAutoRenewalAttempt,
    PassCancellation,
    PassTemplate,
    PassType,
    PassTypePricingWindow,
    PassTypePricingWindowOption,
    RACDiscountUsage,
)

logger = logging.getLogger(__name__)


class PassCancellationInline(admin.TabularInline):
    model = PassCancellation
    fields = [
        "cancellation_reason",
        "datetime_cancelled",
    ]
    readonly_fields = ["datetime_cancelled"]


class PassAutoRenewalAttemptInline(admin.TabularInline):
    model = PassAutoRenewalAttempt
    fields = [
        "auto_renewal_succeeded",
        "datetime_attempted",
    ]
    readonly_fields = [
        "auto_renewal_succeeded",
        "datetime_attempted",
    ]
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser


class PassAdmin(admin.ModelAdmin):
    model = Pass
    fields = [
        "park_pass_pdf_secure",
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
        "drivers_licence_number",
        "date_start",
        "date_expiry",
        "renew_automatically",
        "park_pass_renewed_from",
        "datetime_created",
        "datetime_updated",
    ]
    list_display = (
        "pass_number",
        "renew_automatically",  # remove later
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
        "park_pass_pdf_secure",
        "pass_number",
        "first_name",
        "last_name",
        "email",
        "date_expiry",
        "park_pass_renewed_from",
        "datetime_created",
        "datetime_updated",
    ]
    ordering = [
        "-id",
    ]
    inlines = [
        PassCancellationInline,
        PassAutoRenewalAttemptInline,
    ]

    # def get_inline_instances(self, request, obj=None):
    #     to_return = super().get_inline_instances(request, obj)
    #     if not obj or not obj.renew_automatically:
    #         to_return = [
    #             x for x in to_return if not isinstance(x, PassAutoRenewalAttemptInline)
    #         ]
    #     return to_return

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
        "pass_type_field",
        "template_secure",
        "version",
    )
    ordering = ["pass_type", "-version"]

    def pass_type_field(self, instance):
        if instance.pass_type:
            return str(instance.pass_type)
        return "All Pass Types"

    def template_secure(self, instance):
        value_link = f"/api/passes/pass-templates/{instance.id}/retrieve-pass-template/"
        value_desc = str(instance.template)
        return format_html('<a href="{}" target="blank">{}</a>', value_link, value_desc)


admin.site.register(PassTemplate, PassTemplateAdmin)


class RACDiscountUsageAdmin(admin.ModelAdmin):
    model = RACDiscountUsage
    list_display = ["park_pass", "discount_percentage"]
    raw_id_fields = ["park_pass"]
    readonly_fields = ["park_pass", "discount_percentage"]


admin.site.register(RACDiscountUsage, RACDiscountUsageAdmin)
