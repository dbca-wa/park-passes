from django.contrib import admin

from parkpasses.components.orders.models import Order, OrderItem


class OrderItemAdmin(admin.ModelAdmin):
    model = OrderItem
    list_display = (
        "order",
        "object_id",
        "content_type",
        "amount",
    )


admin.site.register(OrderItem, OrderItemAdmin)


class OrderItemInline(admin.TabularInline):
    model = OrderItem

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class OrderAdmin(admin.ModelAdmin):
    model = Order
    fields = [
        "order_number",
        "user",
        "uuid",
        "invoice_reference",
        "datetime_created",
        "total_display",
        "retailer_group",
        "is_no_payment",
        "payment_confirmed",
    ]

    list_display = (
        "order_number",
        "datetime_created",
        "user",
        "retailer_group",
        "uuid",
        "invoice_reference",
        "payment_confirmed",
        "total_display",
    )
    readonly_fields = [
        "order_number",
        "datetime_created",
        "total_display",
    ]
    ordering = ("-datetime_created",)
    inlines = [OrderItemInline]


admin.site.register(Order, OrderAdmin)
