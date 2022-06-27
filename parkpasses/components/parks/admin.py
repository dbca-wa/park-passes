from django.contrib import admin

from parkpasses.components.parks.models import LGA, Member, Park, ParkGroup, Postcode


class ParkGroupAdmin(admin.ModelAdmin):
    model = ParkGroup
    fields = [
        "name",
        "display_order",
        "display_externally",
    ]
    search_fields = [
        "name",
    ]
    list_display = (
        "name",
        "display_order",
        "display_externally",
    )
    ordering = ("display_order",)


admin.site.register(ParkGroup, ParkGroupAdmin)


class ParkAdmin(admin.ModelAdmin):
    model = Park
    fields = [
        "name",
        "image",
        "display_externally",
    ]
    search_fields = [
        "name",
    ]
    list_display = (
        "name",
        "display_externally",
    )
    ordering = ("name",)


admin.site.register(Park, ParkAdmin)


class MemberAdmin(admin.ModelAdmin):
    model = Member
    fields = [
        "park_group",
        "park",
        "display_order",
    ]
    autocomplete_fields = (
        "park_group",
        "park",
    )
    list_display = (
        "park_group",
        "park",
        "display_order",
    )
    ordering = (
        "park_group",
        "display_order",
    )


admin.site.register(Member, MemberAdmin)


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
        "park_group",
        "postcodes",
    ]
    search_fields = [
        "name",
    ]
    list_display = (
        "park_group",
        "name",
    )
    ordering = (
        "park_group__name",
        "name",
    )

    def postcodes(self, obj):
        return obj.postcodes


admin.site.register(LGA, LGAAdmin)
