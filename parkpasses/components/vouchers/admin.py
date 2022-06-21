from django.contrib import admin

from parkpasses.components.vouchers.models import Voucher, VoucherTransaction


class VoucherTransactionInline(admin.TabularInline):
    model = VoucherTransaction


class VoucherAdmin(admin.ModelAdmin):
    model = Voucher
    list_display = (
        "recipient_email",
        "amount",
        "remaining_balance",
        "code",
        "datetime_purchased",
        "expiry",
        "processing_status",
    )
    readonly_fields = ["voucher_number", "code", "expiry"]
    ordering = ("-datetime_purchased",)
    inlines = [VoucherTransactionInline]


admin.site.register(Voucher, VoucherAdmin)
