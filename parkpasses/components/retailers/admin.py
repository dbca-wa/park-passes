from django.contrib import admin

from parkpasses.components.retailers.models import (
    District,
    RetailerGroup,
    RetailerGroupInvite,
    RetailerGroupUser,
)


class DistrictAdmin(admin.ModelAdmin):
    model = District


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
        "district",
        "organisation_name",
        "commission_oracle_code",
        "active",
    )
    search_fields = ("name",)
    fields = [
        "ledger_organisation",
        "organisation_name",
        "organisation_abn",
        "district",
        "commission_oracle_code",
        "commission_percentage",
        "active",
    ]
    readonly_fields = ["organisation_name", "organisation_abn"]
    inlines = [RetailerGroupUserInline]

    def organisation_name(self, obj):
        if obj.organisation:
            return obj.organisation["organisation_name"]
        return "No Organisation Assigned"

    organisation_name.short_description = "Ledger Organisation Name"

    def organisation_abn(self, obj):
        if obj.organisation:
            return obj.organisation["organisation_abn"]
        return "No Organisation Assigned"

    organisation_abn.short_description = "Ledger Organisation ABN"


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


admin.site.register(District, DistrictAdmin)
admin.site.register(RetailerGroup, RetailerGroupAdmin)
admin.site.register(RetailerGroupUser, RetailerGroupUserAdmin)
admin.site.register(RetailerGroupInvite, RetailerGroupInviteAdmin)
