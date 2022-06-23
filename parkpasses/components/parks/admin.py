from django.contrib import admin

from parkpasses.components.parks.models import LGA, Park, Postcode


class ParkAdmin(admin.ModelAdmin):
    model = Park
    fields = [
        "name",
        "display_order",
        "display_externally",
    ]
    list_display = (
        "name",
        "display_order",
        "display_externally",
    )
    ordering = ("display_order",)


admin.site.register(Park, ParkAdmin)


class PostcodeAdmin(admin.ModelAdmin):
    model = Postcode
    search_fields = [
        "postcode",
    ]
    list_display = ("postcode",)
    readonly_fields = [
        "postcode",
        "local_park",
    ]

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Postcode, PostcodeAdmin)


class LGAAdmin(admin.ModelAdmin):
    model = LGA
    autocomplete_fields = ("postcodes",)
    fields = [
        "name",
        "park",
        "postcodes",
    ]
    list_display = (
        "name",
        "park",
    )
    ordering = ("park__name",)

    def postcodes(self, obj):
        return obj.postcodes


admin.site.register(LGA, LGAAdmin)
