import os

from rest_framework import serializers

from parkpasses.components.reports.models import Report


class RetailerReportSerializer(serializers.ModelSerializer):
    report_filename = serializers.SerializerMethodField()
    invoice_filename = serializers.SerializerMethodField()
    processing_status_display = serializers.SerializerMethodField()
    datetime_created = serializers.SerializerMethodField()
    retailer_group = serializers.CharField(source="retailer_group.name")

    class Meta:
        model = Report
        fields = "__all__"
        datatables_always_serialize = [
            "invoice_reference",
        ]

    def get_processing_status_display(self, obj):
        return obj.get_processing_status_display()

    def get_report_filename(self, obj):
        return os.path.basename(obj.report.name)

    def get_invoice_filename(self, obj):
        return os.path.basename(obj.invoice.name)

    def get_datetime_created(self, obj):
        return obj.datetime_created.strftime("%d/%m/%Y")


class InternalReportSerializer(serializers.ModelSerializer):
    report_filename = serializers.SerializerMethodField()
    invoice_filename = serializers.SerializerMethodField()
    processing_status_display = serializers.SerializerMethodField()
    datetime_created = serializers.SerializerMethodField()
    retailer_group = serializers.CharField(source="retailer_group.name")

    class Meta:
        model = Report
        fields = "__all__"

    def get_processing_status_display(self, obj):
        return obj.get_processing_status_display()

    def get_report_filename(self, obj):
        return os.path.basename(obj.report.name)

    def get_invoice_filename(self, obj):
        return os.path.basename(obj.invoice.name)

    def get_datetime_created(self, obj):
        return obj.datetime_created.strftime("%d/%m/%Y")
