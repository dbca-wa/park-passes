import logging

from django.conf import settings
from django_filters import rest_framework as filters
from rest_framework import generics, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_datatables.django_filters.backends import DatatablesFilterBackend
from rest_framework_datatables.django_filters.filterset import DatatablesFilterSet
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from parkpasses.components.passes.models import (
    Pass,
    PassTemplate,
    PassType,
    PassTypePricingWindow,
    PassTypePricingWindowOption,
)
from parkpasses.components.passes.serializers import (
    ExternalPassSerializer,
    InternalOptionSerializer,
    InternalPassCancellationSerializer,
    InternalPassSerializer,
    InternalPassTypeSerializer,
    OptionSerializer,
    PassTemplateSerializer,
    PassTypeSerializer,
    PricingWindowSerializer,
)
from parkpasses.helpers import (
    belongs_to,
    get_retailer_groups_for_user,
    is_customer,
    is_internal,
    is_retailer,
)
from parkpasses.permissions import IsInternal

logger = logging.getLogger(__name__)


class PassTypesDistinct(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        if request.query_params.get("for_filter", ""):
            pass_types = [
                {"id": pass_type.name, "text": pass_type.display_name}
                for pass_type in PassType.objects.all().distinct()
            ]
        else:
            pass_types = [
                {"code": pass_type.name, "description": pass_type.display_name}
                for pass_type in PassType.objects.all().distinct()
            ]
        return Response(pass_types)


class PassProcessingStatusesDistinct(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        if request.query_params.get("for_filter", ""):
            processing_status_choices = [
                {"id": processing_status_choice[0], "text": processing_status_choice[1]}
                for processing_status_choice in Pass.PROCESSING_STATUS_CHOICES
            ]
        else:
            processing_status_choices = [
                {
                    "code": processing_status_choice[0],
                    "description": processing_status_choice[1],
                }
                for processing_status_choice in Pass.PROCESSING_STATUS_CHOICES
            ]
        return Response(processing_status_choices)


class PassTypeViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on pass types.
    """

    model = PassType

    def get_queryset(self):
        if is_internal(self.request):
            return PassType.objects.all().order_by("display_order")
        elif belongs_to(self.request, settings.GROUP_NAME_PARK_PASSES_RETAILER):
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
        elif belongs_to(self.request, settings.GROUP_NAME_PARK_PASSES_RETAILER):
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
        if belongs_to(self.request, settings.GROUP_NAME_PARK_PASSES_RETAILER):
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
        if belongs_to(self.request, settings.GROUP_NAME_PARK_PASSES_RETAILER):
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


class CurrentOptionsForPassType(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = OptionSerializer

    def get_queryset(self):
        pass_type_id = self.request.query_params.get("pass_type_id")
        logger.debug("pass_type_id = " + pass_type_id)
        options = PassTypePricingWindowOption.get_current_options_by_pass_type_id(
            int(pass_type_id)
        )
        if options:
            return options
        return PassTypePricingWindowOption.objects.none()


class PassTypePricingWindowOptionViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on pricing windows options.
    """

    model = PassTypePricingWindowOption
    serializer_class = OptionSerializer

    def get_queryset(self):
        return PassTypePricingWindowOption.objects.all()

    def get_serializer_class(self):
        if is_internal(self.request):
            return InternalOptionSerializer
        elif belongs_to(self.request, settings.GROUP_NAME_PARK_PASSES_RETAILER):
            return OptionSerializer
        else:
            return OptionSerializer

    def has_permission(self, request, view):
        if is_internal(request):
            return True
        if belongs_to(self.request, settings.GROUP_NAME_PARK_PASSES_RETAILER):
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
    A ViewSet for performing actions on pass templates.
    """

    model = PassTemplate
    serializer_class = PassTemplateSerializer

    def get_queryset(self):
        return PassTemplate.objects.all()

    def has_permission(self, request, view):
        if is_internal(request):
            return True
        return False


class PassFilter(DatatablesFilterSet):
    start_date_from = filters.DateFilter(field_name="datetime_start", lookup_expr="gte")
    start_date_to = filters.DateFilter(field_name="datetime_start", lookup_expr="lte")

    class Meta:
        model = Pass
        fields = [
            # "option__pricing_window__pass_type__name",
            "processing_status",
        ]


class PassViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on passes.
    """

    search_fields = ["last_name"]
    queryset = Pass.objects.all()
    model = Pass
    filter_backends = [SearchFilter, DatatablesFilterBackend]
    pagination_class = DatatablesPageNumberPagination
    # filterset_class = PassFilter
    filterset_fields = ["processing_status"]
    page_size = 10

    def get_queryset(self):
        if is_internal(self.request):
            return Pass.objects.all()
        elif is_retailer(self.request):
            retailer_groups_for_user = get_retailer_groups_for_user(self.request)
            return Pass.objects.filter(sold_via__in=retailer_groups_for_user)
        else:
            return Pass.objects.filter(user=self.request.user.id)

    def get_serializer_class(self):
        if is_internal(self.request):
            return InternalPassSerializer
        elif belongs_to(self.request, settings.GROUP_NAME_PARK_PASSES_RETAILER):
            return ExternalPassSerializer
        else:
            return ExternalPassSerializer

    def has_permission(self, request, view):
        if is_internal(request):
            return True
        if belongs_to(self.request, settings.GROUP_NAME_PARK_PASSES_RETAILER):
            if view.action in [
                "list",
                "retrieve",
                "create",
                "update",
                "partial_update",
            ]:
                return True
            return False
        if is_customer(request):
            if view.action in [
                "list",
                "create",
                "update",
                "partial_update",
            ]:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if is_internal(request):
            return True
        if is_customer(request):
            if view.action in [
                "partial_update",
                "update",
            ]:
                if obj.user == request.user.id:
                    return True
        return False


class CancelPass(APIView):
    permission_classes = [IsInternal]

    def post(self, request, format=None):
        serializer = InternalPassCancellationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
