from django.contrib import admin
from django.contrib.sessions.models import Session

from parkpasses.components.users.models import UserSession


class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()

    list_display = ["session_key", "_session_data", "expire_date"]


admin.site.register(Session, SessionAdmin)


class UserSessionAdmin(admin.ModelAdmin):
    model = UserSession
    raw_id_fields = ["session"]


admin.site.register(UserSession, UserSessionAdmin)
