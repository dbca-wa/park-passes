from django.utils.formats import date_format
from rest_framework import serializers

from parkpasses.components.retailers.models import (
    RetailerGroup,
    RetailerGroupInvite,
    RetailerGroupUser,
)


class RetailerGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetailerGroup
        fields = "__all__"


class RetailerGroupUserSerializer(serializers.ModelSerializer):
    retailer_group_name = serializers.CharField(
        source="retailer_group.name", read_only=True
    )
    emailuser_email = serializers.SerializerMethodField(read_only=True)
    datetime_created = serializers.SerializerMethodField(read_only=True)
    datetime_updated = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RetailerGroupUser
        fields = [
            "id",
            "retailer_group",
            "retailer_group_name",
            "emailuser_email",
            "emailuser",
            "active",
            "is_admin",
            "datetime_created",
            "datetime_updated",
        ]

    def get_datetime_created(self, obj):
        return date_format(
            obj.datetime_created, format="SHORT_DATETIME_FORMAT", use_l10n=True
        )

    def get_datetime_updated(self, obj):
        return date_format(
            obj.datetime_updated, format="SHORT_DATETIME_FORMAT", use_l10n=True
        )

    def get_emailuser_email(self, obj):
        return obj.emailuser.email


class RetailerGroupInviteSerializer(serializers.ModelSerializer):
    retailer_group_name = serializers.CharField(source="retailer_group.name")
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = RetailerGroupInvite
        fields = [
            "id",
            "user",
            "email",
            "retailer_group",
            "retailer_group_name",
            "status",
            "status_display",
            "datetime_created",
        ]

    def get_status_display(self, obj):
        return obj.get_status_display()
