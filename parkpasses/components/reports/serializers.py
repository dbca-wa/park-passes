import os

from rest_framework import serializers

from parkpasses.components.reports.models import Report


class RetailerReportSerializer(serializers.ModelSerializer):
    report_filename = serializers.SerializerMethodField()
    processing_status_display = serializers.SerializerMethodField()
    datetime_created = serializers.SerializerMethodField()
    retailer_group = serializers.SerializerMethodField()
    overdue = serializers.BooleanField(read_only=True)
    invoice_link = serializers.CharField(read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "invoice_reference",
            "invoice_link",
            "processing_status",
            "processing_status_display",
            "report",
            "report_filename",
            "report_number",
            "retailer_group",
            "uuid",
            "datetime_created",
            "overdue",
        ]
        datatables_always_serialize = [
            "invoice_reference",
            "overdue",
        ]

    def get_retailer_group(self, obj):
        return obj.retailer_group.organisation["organisation_name"]

    def get_processing_status_display(self, obj):
        return obj.get_processing_status_display()

    def get_report_filename(self, obj):
        return os.path.basename(obj.report.name)

    def get_datetime_created(self, obj):
        return obj.datetime_created.strftime("%d/%m/%Y")


class InternalReportSerializer(serializers.ModelSerializer):
    report_filename = serializers.SerializerMethodField()
    processing_status_display = serializers.SerializerMethodField()
    datetime_created = serializers.SerializerMethodField()
    retailer_group = serializers.SerializerMethodField()
    overdue = serializers.BooleanField(read_only=True)
    invoice_link = serializers.CharField(read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "invoice_reference",
            "invoice_link",
            "processing_status",
            "processing_status_display",
            "report",
            "report_filename",
            "report_number",
            "retailer_group",
            "uuid",
            "datetime_created",
            "overdue",
        ]
        datatables_always_serialize = [
            "invoice_reference",
            "overdue",
        ]

    def get_processing_status_display(self, obj):
        return obj.get_processing_status_display()

    def get_report_filename(self, obj):
        return os.path.basename(obj.report.name)

    def get_datetime_created(self, obj):
        return obj.datetime_created.strftime("%d/%m/%Y")

    def get_retailer_group(self, obj):
        return obj.retailer_group.organisation["organisation_name"]
