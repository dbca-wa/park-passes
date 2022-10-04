from django.contrib import admin

from parkpasses.components.retailers.models import (
    RetailerGroup,
    RetailerGroupInvite,
    RetailerGroupUser,
)


class RetailerGroupUserInline(admin.TabularInline):
    model = RetailerGroupUser
    extra = 0
    autocomplete_fields = ["emailuser"]


class RetailerGroupAdmin(admin.ModelAdmin):
    model = RetailerGroup
    list_display = (
        "id",
        "name",
    )
    search_fields = ("name",)
    inlines = [RetailerGroupUserInline]
    ordering = ["name"]


class RetailerGroupInviteAdmin(admin.ModelAdmin):
    model = RetailerGroupInvite
    list_display = (
        "email",
        "retailer_group",
        "uuid",
        "status",
        "datetime_created",
        "datetime_updated",
    )
    readonly_fields = ["uuid"]


admin.site.register(RetailerGroup, RetailerGroupAdmin)
admin.site.register(RetailerGroupInvite, RetailerGroupInviteAdmin)
