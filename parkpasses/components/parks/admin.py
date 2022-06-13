from django.contrib import admin

from parkpasses.components.parks.models import Park, Postcode


class ParkAdmin(admin.ModelAdmin):
    model = Park
    fields = [
        "name",
        "display_order",
        "display_externally",
        "postcodes",
    ]
    list_display = (
        "name",
        "display_order",
        "display_externally",
    )
    ordering = ("display_order",)
    filter_horizontal = ("postcodes",)

    def postcodes(self, obj):
        return obj.postcodes


admin.site.register(Park, ParkAdmin)
admin.site.register(Postcode)
