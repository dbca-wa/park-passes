from rest_framework import serializers

from parkpasses.components.reports.models import Report


class RetailerReportSerializer(serializers.ModelSerializer):
    processing_status = serializers.SerializerMethodField()
    datetime_created = serializers.SerializerMethodField()
    retailer_group = serializers.CharField(source="retailer_group.name")

    class Meta:
        model = Report
        fields = "__all__"

    def get_processing_status(self, obj):
        return obj.get_processing_status_display()

    def get_datetime_created(self, obj):
        return obj.datetime_created.strftime("%d/%m/%Y")


class InternalReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"
