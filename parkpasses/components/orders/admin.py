from django.contrib import admin

from parkpasses.components.orders.models import Order, OrderItem


class OrderItemAdmin(admin.ModelAdmin):
    model = OrderItem


admin.site.register(OrderItem, OrderItemAdmin)


class OrderItemInline(admin.TabularInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    model = Order
    fields = [
        "order_number",
        "user",
        "uuid",
        "invoice_reference",
        "datetime_created",
    ]
    list_display = (
        "order_number",
        "user",
        "uuid",
    )
    readonly_fields = [
        "order_number",
        "datetime_created",
    ]
    ordering = ("-datetime_created",)
    inlines = [OrderItemInline]


admin.site.register(Order, OrderAdmin)
