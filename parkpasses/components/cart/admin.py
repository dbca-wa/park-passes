from django.contrib import admin

from parkpasses.components.cart.models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    readonly_fields = [
        "datetime_created",
    ]
    raw_id_fields = [
        "voucher_transaction",
        "discount_code_usage",
    ]


class CartAdmin(admin.ModelAdmin):
    model = Cart
    list_display = (
        "user",
        "uuid",
        "grand_total",
        "datetime_created",
        "datetime_first_added_to",
        "datetime_last_added_to",
    )
    readonly_fields = [
        "datetime_created",
        "datetime_first_added_to",
        "datetime_last_added_to",
        "grand_total",
    ]
    ordering = ("-datetime_created",)
    inlines = [CartItemInline]


admin.site.register(Cart, CartAdmin)
