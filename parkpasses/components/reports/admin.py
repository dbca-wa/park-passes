from django.contrib import admin

from parkpasses.components.reports.models import Report


class ReportAdmin(admin.ModelAdmin):
    model = Report
    readonly_fields = ["report_number"]
    list_display = [field.name for field in Report._meta.get_fields()]
    ordering = ["-datetime_created"]


admin.site.register(Report, ReportAdmin)
