from django.contrib import admin

from parkpasses.components.concessions.models import Concession


class ConcessionAdmin(admin.ModelAdmin):
    model = Concession
    list_display = ("concession_type", "discount_percentage")


admin.site.register(Concession, ConcessionAdmin)
