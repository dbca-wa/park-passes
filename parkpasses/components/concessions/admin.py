from django.contrib import admin

from parkpasses.components.concessions.models import Concession


class ConcessionAdmin(admin.ModelAdmin):
    model = Concession
    list_display = ("concession_type", "discount_percentage", "display_order")
    ordering = ["display_order"]


admin.site.register(Concession, ConcessionAdmin)
