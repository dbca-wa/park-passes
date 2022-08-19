from django.contrib import admin

from parkpasses.components.concessions.models import Concession, ConcessionUsage


class ConcessionAdmin(admin.ModelAdmin):
    model = Concession
    list_display = ("concession_type", "discount_percentage", "display_order")
    ordering = ["display_order"]


class ConcessionUsageAdmin(admin.ModelAdmin):
    model = ConcessionUsage


admin.site.register(Concession, ConcessionAdmin)
admin.site.register(ConcessionUsage, ConcessionUsageAdmin)
