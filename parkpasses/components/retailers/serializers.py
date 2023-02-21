from django.utils.formats import date_format
from rest_framework import serializers

from parkpasses.components.retailers.models import (
    District,
    RetailerGroup,
    RetailerGroupInvite,
    RetailerGroupUser,
)


class RetailerGroupSerializer(serializers.ModelSerializer):
    ledger_organisation_name = serializers.SerializerMethodField(read_only=True)
    user_count = serializers.IntegerField(read_only=True)
    is_internal_retailer = serializers.BooleanField(read_only=True)

    class Meta:
        model = RetailerGroup
        fields = [
            "id",
            "ledger_organisation",
            "ledger_organisation_name",
            "district",
            "commission_oracle_code",
            "commission_percentage",
            "is_internal_retailer",
            "active",
            "user_count",
            "datetime_created",
            "datetime_updated",
        ]

    def get_ledger_organisation_name(self, obj):
        return obj.organisation["organisation_name"]


class RetailerGroupUserSerializer(serializers.ModelSerializer):
    retailer_group_name = serializers.SerializerMethodField(read_only=True)
    emailuser_email = serializers.SerializerMethodField(read_only=True)
    datetime_created = serializers.DateTimeField(
        format="%d/%m/%Y %I:%M %p", read_only=True
    )
    datetime_updated = serializers.DateTimeField(
        format="%d/%m/%Y %I:%M %p", read_only=True
    )
    retailer_group_admin_user_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = RetailerGroupUser
        fields = [
            "id",
            "retailer_group",
            "retailer_group_name",
            "retailer_group_admin_user_count",
            "emailuser_email",
            "emailuser",
            "active",
            "is_admin",
            "datetime_created",
            "datetime_updated",
        ]

    def get_retailer_group_name(self, obj):
        return obj.retailer_group.organisation["organisation_name"]

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


class InternalRetailerGroupInviteSerializer(serializers.ModelSerializer):
    retailer_group_name = serializers.SerializerMethodField(read_only=True)
    initiated_by_display = serializers.CharField(
        source="get_initiated_by_display", read_only=True
    )
    status_display = serializers.SerializerMethodField()
    datetime_created = serializers.DateTimeField(
        format="%d/%m/%Y %I:%M %p", read_only=True
    )
    datetime_updated = serializers.DateTimeField(
        format="%d/%m/%Y %I:%M %p", read_only=True
    )
    is_admin = serializers.CharField(write_only=True, required=False, allow_blank=True)
    user_count_for_retailer_group = serializers.IntegerField(read_only=True)

    class Meta:
        model = RetailerGroupInvite
        fields = [
            "id",
            "uuid",
            "user",
            "email",
            "retailer_group",
            "retailer_group_name",
            "user_count_for_retailer_group",
            "initiated_by",
            "initiated_by_display",
            "status",
            "status_display",
            "is_admin",
            "datetime_created",
            "datetime_updated",
        ]
        datatables_always_serialize = ["status", "user_count_for_retailer_group"]

    def get_retailer_group_name(self, obj):
        return obj.retailer_group.organisation["organisation_name"]

    def create(self, validated_data):
        validated_data.pop("is_admin", None)
        return super().create(validated_data)

    def update(self, validated_data):
        validated_data.pop("is_admin", None)
        return super().update(validated_data)

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_datetime_created(self, obj):
        return date_format(
            obj.datetime_created, format="SHORT_DATETIME_FORMAT", use_l10n=True
        )

    def get_datetime_updated(self, obj):
        return date_format(
            obj.datetime_updated, format="SHORT_DATETIME_FORMAT", use_l10n=True
        )


class RetailerRetailerGroupInviteSerializer(serializers.ModelSerializer):
    retailer_group_name = serializers.SerializerMethodField(read_only=True)
    initiated_by_display = serializers.CharField(
        source="get_initiated_by_display", read_only=True
    )
    status_display = serializers.SerializerMethodField()
    datetime_created = serializers.SerializerMethodField(read_only=True)
    datetime_updated = serializers.SerializerMethodField(read_only=True)
    user_count_for_retailer_group = serializers.IntegerField(read_only=True)

    class Meta:
        model = RetailerGroupInvite
        fields = [
            "id",
            "uuid",
            "user",
            "email",
            "retailer_group",
            "retailer_group_name",
            "user_count_for_retailer_group",
            "initiated_by",
            "initiated_by_display",
            "status",
            "status_display",
            "datetime_created",
            "datetime_updated",
        ]
        datatables_always_serialize = ["status", "user_count_for_retailer_group"]

    def get_retailer_group_name(self, obj):
        return obj.retailer_group.organisation["organisation_name"]

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_datetime_created(self, obj):
        return date_format(
            obj.datetime_created, format="SHORT_DATETIME_FORMAT", use_l10n=True
        )

    def get_datetime_updated(self, obj):
        return date_format(
            obj.datetime_updated, format="SHORT_DATETIME_FORMAT", use_l10n=True
        )


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = "__all__"
