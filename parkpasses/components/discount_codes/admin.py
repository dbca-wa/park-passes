from django.contrib import admin

from parkpasses.components.discount_codes.models import (
    DiscountCode,
    DiscountCodeBatch,
    DiscountCodeBatchValidPassType,
    DiscountCodeBatchValidUser,
    DiscountCodeUsage,
)


class DiscountCodeBatchValidPassTypeTabularInlineAdmin(admin.TabularInline):
    model = DiscountCodeBatchValidPassType


class DiscountCodeBatchValidUserTabularInlineAdmin(admin.TabularInline):
    model = DiscountCodeBatchValidUser


class DiscountCodeTabularInlineAdmin(admin.TabularInline):
    model = DiscountCode
    readonly_fields = ["code"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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
    inlines = [
        DiscountCodeBatchValidPassTypeTabularInlineAdmin,
        DiscountCodeBatchValidUserTabularInlineAdmin,
        DiscountCodeTabularInlineAdmin,
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing
            return self.readonly_fields
        return ()


admin.site.register(DiscountCodeBatch, DiscountCodeBatchAdmin)


class DiscountCodeUsageAdmin(admin.TabularInline):
    model = DiscountCodeUsage
    raw_id_fields = ["park_pass"]


class DiscountCodeAdmin(admin.ModelAdmin):
    model = DiscountCode

    list_display = (
        "code",
        "remaining_uses",
    )

    inlines = [DiscountCodeUsageAdmin]


admin.site.register(DiscountCode, DiscountCodeAdmin)
