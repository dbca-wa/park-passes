from django.contrib import admin

from parkpasses.components.discount_codes.models import DiscountCodeBatch


class DiscountCodeBatchAdmin(admin.ModelAdmin):
    model = DiscountCodeBatch
    list_display = (
        "codes_to_generate",
        "times_each_code_can_be_used",
        "discount_amount",
        "discount_percentage",
    )
    readonly_fields = (
        "datetime_created",
        "datetime_updated",
    )


admin.site.register(DiscountCodeBatch, DiscountCodeBatchAdmin)
