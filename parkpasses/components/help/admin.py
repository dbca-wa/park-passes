from django.contrib import admin

from parkpasses.components.help.models import HelpText


class HelpTextAdmin(admin.ModelAdmin):
    model = HelpText
    list_display = ("label", "version")
    readonly_fields = [
        "content",
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing
            return self.readonly_fields
        return ()


admin.site.register(HelpText, HelpTextAdmin)
