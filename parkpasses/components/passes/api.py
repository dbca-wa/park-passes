import logging

from django.conf import settings
from rest_framework import viewsets
from rest_framework.permissions import BasePermission

from parkpasses.components.passes.models import (
    Pass,
    PassTemplate,
    PassType,
    PassTypePricingWindow,
    PassTypePricingWindowOption,
)
from parkpasses.components.passes.serializers import (
    InternalPassTypeSerializer,
    PassSerializer,
    PassTemplateSerializer,
    PassTypePricingWindowOptionSerializer,
    PassTypeSerializer,
    PricingWindowSerializer,
)
from parkpasses.helpers import belongs_to, is_customer, is_internal

logger = logging.getLogger(__name__)


class IsInternal(BasePermission):
    def has_permission(self, request, view):
        return is_internal(self.request)


class PassTypeViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on pass types.
    """

    model = PassType

    def get_queryset(self):
        if is_internal(self.request):
            return PassType.objects.all().order_by("display_order")
        elif belongs_to(self.request.user, settings.GROUP_NAME_RETAILER):
            return PassType.objects.filter(display_retail=True).order_by(
                "display_order"
            )
        else:
            return PassType.objects.filter(display_externally=True).order_by(
                "display_order"
            )

    def get_serializer_class(self):
        if is_internal(self.request):
            return InternalPassTypeSerializer
        elif belongs_to(self.request.user, settings.GROUP_NAME_RETAILER):
            return PassTypeSerializer
        else:
            return PassTypeSerializer

    def has_permission(self, request, view):
        if is_internal(request):
            return True
        if is_customer(request):
            if view.action in ["list", "retrieve", "create"]:
                return True
            return False
        if belongs_to(self.request.user, settings.GROUP_NAME_RETAILER):
            if view.action in ["list", "retrieve", "create"]:
                return True
            return False
        return False


class PricingWindowViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on pricing windows.
    """

    model = PassTypePricingWindow
    serializer_class = PricingWindowSerializer

    def get_queryset(self):
        return PassTypePricingWindow.objects.all()

    def has_permission(self, request, view):
        if is_internal(request):
            return True
        if belongs_to(self.request.user, settings.GROUP_NAME_RETAILER):
            if view.action in [
                "list",
                "retrieve",
            ]:
                return True
            return False
        if is_customer(request):
            if view.action in [
                "list",
                "retrieve",
            ]:
                return True
        return False


class PassTypePricingWindowOptionViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on pricing windows.
    """

    model = PassTypePricingWindowOption
    serializer_class = PassTypePricingWindowOptionSerializer

    def get_queryset(self):
        return PassTypePricingWindowOption.objects.all()

    def has_permission(self, request, view):
        if is_internal(request):
            return True
        if belongs_to(self.request.user, settings.GROUP_NAME_RETAILER):
            if view.action in [
                "list",
                "retrieve",
            ]:
                return True
            return False
        if is_customer(request):
            if view.action in [
                "list",
                "retrieve",
            ]:
                return True
        return False


class PassTemplateViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on pricing windows.
    """

    model = PassTemplate
    serializer_class = PassSerializer

    def get_queryset(self):
        return PassTemplate.objects.all()

    def has_permission(self, request, view):
        if is_internal(request):
            return True
        if belongs_to(self.request.user, settings.GROUP_NAME_RETAILER):
            if view.action in [
                "list",
                "retrieve",
            ]:
                return True
            return False
        if is_customer(request):
            if view.action in [
                "list",
                "retrieve",
            ]:
                return True
        return False


class PassViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on pricing windows.
    """

    model = Pass
    serializer_class = PassTemplateSerializer

    def get_queryset(self):
        return Pass.objects.all()

    def has_permission(self, request, view):
        if is_internal(request):
            return True
        if belongs_to(self.request.user, settings.GROUP_NAME_RETAILER):
            if view.action in [
                "list",
                "retrieve",
            ]:
                return True
            return False
        if is_customer(request):
            if view.action in [
                "list",
                "retrieve",
            ]:
                return True
        return False
