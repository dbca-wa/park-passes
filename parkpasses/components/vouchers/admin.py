from django.contrib import admin

from parkpasses.components.vouchers.models import Voucher, VoucherTransaction


class VoucherTransactionInline(admin.TabularInline):
    model = VoucherTransaction


class VoucherAdmin(admin.ModelAdmin):
    model = Voucher
    list_display = (
        "voucher_number",
        "recipient_name",
        "recipient_email",
        "amount",
        "remaining_balance",
        "code",
        "expiry",
        "processing_status",
        "datetime_purchased",
        "datetime_updated",
    )
    readonly_fields = [
        "voucher_number",
        "code",
        "expiry",
        "datetime_purchased",
        "datetime_updated",
    ]
    ordering = ("-datetime_purchased",)
    inlines = [VoucherTransactionInline]


admin.site.register(Voucher, VoucherAdmin)
