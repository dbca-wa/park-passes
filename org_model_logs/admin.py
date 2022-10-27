from django.contrib import admin

from org_model_logs.models import CommunicationsLogEntry, EntryType, UserAction


class EntryTypeAdmin(admin.ModelAdmin):
    model = EntryType


admin.site.register(EntryType, EntryTypeAdmin)


class UserActionAdmin(admin.ModelAdmin):
    model = UserAction
    fields = [
        "object_id",
        "content_type",
        "who",
        "when",
        "what",
        "why",
    ]

    list_display = (
        "object_id",
        "content_type",
        "who",
        "when",
        "what",
        "why",
    )

    readonly_fields = ["when"]
    ordering = ["-when"]


admin.site.register(UserAction, UserActionAdmin)


class CommunicationsLogEntryAdmin(admin.ModelAdmin):
    model = CommunicationsLogEntry
    list_display = (
        "object_id",
        "content_type",
        "to",
        "fromm",
        "entry_type",
    )
    ordering = ["-created"]


admin.site.register(CommunicationsLogEntry, CommunicationsLogEntryAdmin)
