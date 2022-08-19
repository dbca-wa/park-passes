from django.contrib import admin

from parkpasses.components.orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = (
        "order_number",
        "user",
        "datetime_created",
    )
    readonly_fields = [
        "order_number",
        "datetime_created",
    ]
    ordering = ("-datetime_created",)
    inlines = [OrderItemInline]


admin.site.register(Order, OrderAdmin)
