import logging

from django.contrib import admin
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

admin.site.index_template = "admin-index.html"
admin.autodiscover()


logger = logging.getLogger(__name__)


@admin.register(EmailUser)
class EmailUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    ordering = ("email",)
    search_fields = ("id", "email", "first_name", "last_name")
    list_display_links = None

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.opts.verbose_name_plural = "Email Users (Read-Only)"

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
