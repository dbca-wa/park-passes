from django.contrib import admin

from parkpasses.components.discount_codes.models import (
    DiscountCode,
    DiscountCodeBatch,
    DiscountCodeUsage,
)


class DiscountCodeTabularInlineAdmin(admin.TabularInline):
    model = DiscountCode


class DiscountCodeBatchAdmin(admin.ModelAdmin):
    model = DiscountCodeBatch

    list_display = (
        "discount_code_batch_number",
        "codes_to_generate",
        "times_each_code_can_be_used",
        "discount_amount",
        "discount_percentage",
    )
    readonly_fields = (
        "codes_to_generate",
        "times_each_code_can_be_used",
        "discount_code_batch_number",
        "datetime_created",
        "datetime_updated",
    )
    inlines = [DiscountCodeTabularInlineAdmin]

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing
            return self.readonly_fields
        return ()


admin.site.register(DiscountCodeBatch, DiscountCodeBatchAdmin)


class DiscountCodeUsageAdmin(admin.TabularInline):
    model = DiscountCodeUsage


class DiscountCodeAdmin(admin.ModelAdmin):
    model = DiscountCode

    list_display = (
        "code",
        "remaining_uses",
    )
    readonly_fields = ("remaining_uses",)

    inlines = [DiscountCodeUsageAdmin]


admin.site.register(DiscountCode, DiscountCodeAdmin)
