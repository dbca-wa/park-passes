from django.contrib import admin

from parkpasses.components.vouchers.models import Voucher, VoucherTransaction


class VoucherTransactionInline(admin.TabularInline):
    model = VoucherTransaction
    raw_id_fields = ["park_pass"]


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
    search_fields = ["code"]
    ordering = ("-datetime_purchased",)
    inlines = [VoucherTransactionInline]


admin.site.register(Voucher, VoucherAdmin)


class VoucherTransactionAdmin(admin.ModelAdmin):
    model = VoucherTransaction


admin.site.register(VoucherTransaction, VoucherTransactionAdmin)
