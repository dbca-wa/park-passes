from django.contrib import admin

from parkpasses.components.retailers.models import RetailerGroup, RetailerGroupUser


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


admin.site.register(RetailerGroup, RetailerGroupAdmin)
