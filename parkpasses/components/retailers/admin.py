from django.contrib import admin
from rest_framework_api_key.admin import APIKeyModelAdmin

from parkpasses.components.retailers.models import (
    RetailerGroup,
    RetailerGroupAPIKey,
    RetailerGroupInvite,
    RetailerGroupUser,
)


class RetailerGroupUserInline(admin.TabularInline):
    model = RetailerGroupUser
    readonly_fields = [
        "datetime_created",
        "datetime_updated",
    ]
    extra = 0
    autocomplete_fields = ["emailuser"]


class RetailerGroupAdmin(admin.ModelAdmin):
    model = RetailerGroup
    list_display = (
        "id",
        "name",
        "oracle_code",
        "active",
    )
    search_fields = ("name",)
    inlines = [RetailerGroupUserInline]
    ordering = ["name"]


class RetailerGroupAPIKeyAdmin(APIKeyModelAdmin):
    model = RetailerGroupAPIKey


class RetailerGroupUserAdmin(admin.ModelAdmin):
    model = RetailerGroupUser
    list_display = (
        "id",
        "emailuser",
        "active",
        "is_admin",
        "datetime_created",
        "datetime_updated",
    )
    search_fields = ("emailuser",)
    ordering = ["-datetime_created"]


class RetailerGroupInviteAdmin(admin.ModelAdmin):
    model = RetailerGroupInvite
    list_display = (
        "email",
        "retailer_group",
        "uuid",
        "status",
        "initiated_by",
        "datetime_created",
        "datetime_updated",
    )
    readonly_fields = ["uuid"]


admin.site.register(RetailerGroup, RetailerGroupAdmin)
admin.site.register(RetailerGroupUser, RetailerGroupUserAdmin)
admin.site.register(RetailerGroupInvite, RetailerGroupInviteAdmin)
admin.site.register(RetailerGroupAPIKey, RetailerGroupAPIKeyAdmin)
