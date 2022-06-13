from django.contrib import admin

from parkpasses.components.vouchers.models import Voucher


class VoucherAdmin(admin.ModelAdmin):
    model = Voucher
    list_display = (
        "recipient_email",
        "datetime_purchased",
        "amount",
        "code",
        "expiry",
    )

    ordering = ("-datetime_purchased",)


admin.site.register(Voucher, VoucherAdmin)
