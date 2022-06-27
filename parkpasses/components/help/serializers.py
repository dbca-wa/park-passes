from rest_framework import serializers

from parkpasses.components.help.models import HelpText


class HelpTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpText
        fields = ["id", "label", "content"]


class InternalHelpTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpText
        fields = "__all__"
