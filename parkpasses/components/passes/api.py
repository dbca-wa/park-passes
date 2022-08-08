import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import FileResponse, Http404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters import rest_framework as filters
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_datatables.django_filters.filters import GlobalFilter
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from org_model_logs.utils import UserActionViewSet
from parkpasses.components.cart.models import Cart, CartItem
from parkpasses.components.passes.models import (
    Pass,
    PassTemplate,
    PassType,
    PassTypePricingWindow,
    PassTypePricingWindowOption,
)
from parkpasses.components.passes.serializers import (
    ExternalCreatePassSerializer,
    ExternalPassSerializer,
    InternalOptionSerializer,
    InternalPassCancellationSerializer,
    InternalPassRetrieveSerializer,
    InternalPassSerializer,
    InternalPassTypeSerializer,
    InternalPricingWindowSerializer,
    OptionSerializer,
    PassTemplateSerializer,
    PassTypeSerializer,
)
from parkpasses.components.retailers.models import RetailerGroup, RetailerGroupUser
from parkpasses.helpers import belongs_to, is_customer, is_internal
from parkpasses.permissions import IsInternal, IsRetailer

# from rest_framework_datatables.filters import DatatablesFilterBackend


logger = logging.getLogger(__name__)


class GlobalCharFilter(GlobalFilter, filters.CharFilter):
    pass


class PassTypesDistinct(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        pass_types = [
            {"code": pass_type.id, "description": pass_type.display_name}
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
            return PassType.objects.filter(display_retailer=True).order_by(
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

    @method_decorator(cache_page(60 * 60 * 2))
    def retrieve(self, request, pk=None):
        return super().retrieve(request, pk=pk)

    @method_decorator(cache_page(60 * 60 * 2))
    def list(self, request, pk=None):
        return super().list(request, pk=pk)


class InternalPricingWindowViewSet(viewsets.ModelViewSet):
    search_fields = [
        # "pass_type_display_name",
        "name",
    ]
    model = PassTypePricingWindow
    pagination_class = DatatablesPageNumberPagination
    queryset = PassTypePricingWindow.objects.all()
    permission_classes = [IsInternal]
    serializer_class = InternalPricingWindowSerializer
    filter_backends = (
        SearchFilter,
        DatatablesFilterBackend,
    )


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

    @method_decorator(cache_page(60 * 60 * 2))
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


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


class ExternalPassViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    model = Pass
    pagination_class = DatatablesPageNumberPagination
    page_size = 10

    def get_queryset(self):
        return Pass.objects.filter(user=self.request.user.id)

    def get_serializer_class(self):
        if "create" == self.action:
            return ExternalCreatePassSerializer
        else:
            return ExternalPassSerializer

    def perform_create(self, serializer):
        if is_customer(self.request):
            park_pass = serializer.save(user=self.request.user.id)
        else:
            park_pass = serializer.save()

        dbca_retailer_group = RetailerGroup.get_dbca_retailer_group()
        park_pass.sold_via = dbca_retailer_group
        park_pass.save()

        if self.request.session.get("cart_id", None):
            cart_id = self.request.session["cart_id"]
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = Cart()
            cart.save()
            self.request.session["cart_id"] = cart.id
        content_type = ContentType.objects.get_for_model(park_pass)
        cart_item = CartItem(
            cart=cart, object_id=park_pass.id, content_type=content_type
        )
        cart_item.save()
        if not cart.datetime_first_added_to:
            cart.datetime_first_added_to = timezone.now()
        cart.datetime_last_added_to = timezone.now()
        cart.save()
        logger.debug(str(self.request.session))

    def has_object_permission(self, request, view, obj):
        if is_customer(request):
            if obj.user == request.user.id:
                return True
        return False

    @action(methods=["GET"], detail=True, url_path="retrieve-park-pass-pdf")
    def retrieve_park_pass_pdf(self, request, *args, **kwargs):
        park_pass = self.get_object()
        logger.debug("user = " + str(self.request.user.id))
        if park_pass.user == self.request.user.id:
            if park_pass.park_pass_pdf:
                return FileResponse(park_pass.park_pass_pdf)
        raise Http404


class PassFilterBackend(DatatablesFilterBackend):
    """
    Custom Filters for Internal Pass Viewset
    """

    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        pass_type = request.GET.get("pass_type")
        processing_status = request.GET.get("processing_status")
        start_date_from = request.GET.get("start_date_from")
        start_date_to = request.GET.get("start_date_to")

        if pass_type:
            queryset = queryset.filter(option__pricing_window__pass_type__id=pass_type)

        if processing_status:
            queryset = queryset.filter(processing_status=processing_status)

        if start_date_from:
            queryset = queryset.filter(datetime_start__gte=start_date_from)

        if start_date_to:
            queryset = queryset.filter(datetime_start__lte=start_date_to)

        fields = self.get_fields(request)
        ordering = self.get_ordering(request, view, fields)
        queryset = queryset.order_by(*ordering)
        if len(ordering):
            queryset = queryset.order_by(*ordering)

        queryset = super().filter_queryset(request, queryset, view)
        setattr(view, "_datatables_total_count", total_count)

        return queryset


class RetailerPassViewSet(UserActionViewSet):
    search_fields = [
        "pass_number",
        "first_name",
        "last_name",
        "vehicle_registration_1",
        "vehicle_registration_2",
    ]
    model = Pass
    pagination_class = DatatablesPageNumberPagination
    permission_classes = [IsRetailer]
    serializer_class = InternalPassSerializer
    filter_backends = (PassFilterBackend,)

    def get_queryset(self):
        if RetailerGroupUser.objects.filter(
            emailuser__id=self.request.user.id
        ).exists():
            retailer_groups = RetailerGroupUser.objects.filter(
                emailuser__id=self.request.user.id
            ).values_list("retailer_group__id")
            return Pass.objects.filter(sold_via__in=list(retailer_groups))

        return Pass.objects.none()


class InternalPassViewSet(UserActionViewSet):
    search_fields = [
        "pass_number",
        "first_name",
        "last_name",
        "vehicle_registration_1",
        "vehicle_registration_2",
    ]
    model = Pass
    pagination_class = DatatablesPageNumberPagination
    queryset = Pass.objects.all()
    permission_classes = [IsInternal]
    filter_backends = (PassFilterBackend,)

    def get_serializer_class(self):
        if "retrieve" == self.action:
            return InternalPassRetrieveSerializer
        return InternalPassSerializer

    @action(methods=["GET"], detail=True, url_path="retrieve-park-pass-pdf")
    def retrieve_park_pass_pdf(self, request, *args, **kwargs):
        park_pass = self.get_object()
        if park_pass.park_pass_pdf:
            return FileResponse(park_pass.park_pass_pdf)
        raise Http404


class CancelPass(APIView):
    permission_classes = [IsInternal]

    def post(self, request, format=None):
        serializer = InternalPassCancellationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
