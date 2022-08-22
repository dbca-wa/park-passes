from django.contrib import admin

from parkpasses.components.help.models import FAQ, HelpText


class HelpTextAdmin(admin.ModelAdmin):
    model = HelpText
    list_display = ("label", "version")


admin.site.register(HelpText, HelpTextAdmin)


class FAQAdmin(admin.ModelAdmin):
    model = FAQ
    list_display = ("question", "display_order")

    ordering = ["display_order"]


admin.site.register(FAQ, FAQAdmin)
