from django.contrib import admin

from parkpasses.components.vouchers.models import Voucher, VoucherTransaction


class VoucherTransactionAdmin(admin.TabularInline):
    model = VoucherTransaction


class VoucherAdmin(admin.ModelAdmin):
    model = Voucher
    list_display = (
        "recipient_email",
        "amount",
        "code",
        "datetime_purchased",
        "expiry",
        "processing_status",
    )
    readonly_fields = ["voucher_number", "code", "expiry"]
    ordering = ("-datetime_purchased",)
    inlines = [VoucherTransactionAdmin]


admin.site.register(Voucher, VoucherAdmin)
