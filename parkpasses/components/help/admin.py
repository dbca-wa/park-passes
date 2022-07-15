from django.contrib import admin

from parkpasses.components.help.models import HelpText


class HelpTextAdmin(admin.ModelAdmin):
    model = HelpText
    list_display = ("label", "version")


admin.site.register(HelpText, HelpTextAdmin)
