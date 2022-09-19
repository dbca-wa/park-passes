import logging
from decimal import Decimal

import requests
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import FileResponse, Http404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from org_model_logs.models import UserAction
from org_model_logs.utils import UserActionSerializer, UserActionViewSet
from parkpasses.components.cart.models import Cart, CartItem
from parkpasses.components.cart.utils import CartUtils
from parkpasses.components.concessions.models import Concession, ConcessionUsage
from parkpasses.components.discount_codes.models import DiscountCode, DiscountCodeUsage
from parkpasses.components.orders.models import OrderItem
from parkpasses.components.passes.exceptions import NoValidPassTypeFoundInPost
from parkpasses.components.passes.models import (
    Pass,
    PassTemplate,
    PassType,
    PassTypePricingWindow,
    PassTypePricingWindowOption,
)
from parkpasses.components.passes.serializers import (
    ExternalCreateAllParksPassSerializer,
    ExternalCreateAnnualLocalPassSerializer,
    ExternalCreateDayEntryPassSerializer,
    ExternalCreateGoldStarPassSerializer,
    ExternalCreateHolidayPassSerializer,
    ExternalCreatePinjarOffRoadPassSerializer,
    ExternalPassSerializer,
    ExternalUpdatePassSerializer,
    InternalCreatePricingWindowSerializer,
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
from parkpasses.components.vouchers.models import Voucher, VoucherTransaction
from parkpasses.helpers import belongs_to, is_customer, is_internal
from parkpasses.permissions import IsInternal, IsRetailer

# from rest_framework_datatables.filters import DatatablesFilterBackend


logger = logging.getLogger(__name__)


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


class PricingWindowFilterBackend(DatatablesFilterBackend):
    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        pass_type = request.GET.get("pass_type")

        start_date_from = request.GET.get("start_date_from")
        start_date_to = request.GET.get("start_date_to")

        expiry_date_from = request.GET.get("expiry_date_from")
        expiry_date_to = request.GET.get("expiry_date_to")

        if pass_type:
            queryset = queryset.filter(pass_type__id=pass_type)

        if start_date_from:
            queryset = queryset.filter(date_start__gte=start_date_from)

        if start_date_to:
            queryset = queryset.filter(date_start__lte=start_date_to)

        if expiry_date_from:
            queryset = queryset.filter(date_expiry__gte=expiry_date_from)

        if expiry_date_to:
            queryset = queryset.filter(date_expiry__lte=expiry_date_to)

        fields = self.get_fields(request)
        ordering = self.get_ordering(request, view, fields)
        queryset = queryset.order_by(*ordering)
        if len(ordering):
            queryset = queryset.order_by(*ordering)

        queryset = super().filter_queryset(request, queryset, view)
        setattr(view, "_datatables_total_count", total_count)

        return queryset


class InternalPricingWindowViewSet(viewsets.ModelViewSet):
    search_fields = [
        # "pass_type_display_name",
        "name",
    ]
    model = PassTypePricingWindow
    pagination_class = DatatablesPageNumberPagination
    queryset = PassTypePricingWindow.objects.all()
    permission_classes = [IsInternal]
    filter_backends = (PricingWindowFilterBackend,)

    def get_serializer_class(self):
        logger.debug("self.action = " + str(self.action))
        logger.debug("self.request.data = " + str(self.request.data))
        if "create" == self.action:
            return InternalCreatePricingWindowSerializer
        return InternalPricingWindowSerializer


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


class DefaultOptionsForPassType(generics.ListAPIView):
    """Updated docstring"""

    permission_classes = [IsInternal]
    serializer_class = OptionSerializer

    def get_queryset(self):
        pass_type_id = self.request.query_params.get("pass_type_id")
        if pass_type_id.isnumeric():
            return PassTypePricingWindowOption.get_default_options_by_pass_type_id(
                pass_type_id
            )
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
    queryset = PassTemplate.objects.all()
    serializer_class = PassTemplateSerializer
    permission_classes = [IsInternal]

    @action(methods=["GET"], detail=True, url_path="retrieve-pass-template")
    def retrieve_park_pass_pdf(self, request, *args, **kwargs):
        pass_template = self.get_object()
        logger.debug("user = " + str(self.request.user.id))
        if pass_template.template:
            return FileResponse(pass_template.template)
        raise Http404


class SmallResultSetPagination(DatatablesPageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000


class ExternalPassViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    pagination_class = SmallResultSetPagination
    model = Pass

    def get_queryset(self):
        return (
            Pass.objects.exclude(user__isnull=True)
            .exclude(processing_status="CA")
            .exclude(in_cart=True)
            .filter(user=self.request.user.id)
            .order_by("-date_start")
        )

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return ExternalUpdatePassSerializer
        if "create" == self.action:
            if "pass_type_name" in self.request.data:
                pass_type_name = self.request.data["pass_type_name"]
                if pass_type_name:
                    if settings.HOLIDAY_PASS == pass_type_name:
                        return ExternalCreateHolidayPassSerializer
                    if settings.ANNUAL_LOCAL_PASS == pass_type_name:
                        return ExternalCreateAnnualLocalPassSerializer
                    if settings.ALL_PARKS_PASS == pass_type_name:
                        return ExternalCreateAllParksPassSerializer
                    if settings.GOLD_STAR_PASS == pass_type_name:
                        return ExternalCreateGoldStarPassSerializer
                    if settings.DAY_ENTRY_PASS == pass_type_name:
                        return ExternalCreateDayEntryPassSerializer
                    if (
                        settings.PINJAR_OFF_ROAD_VEHICLE_AREA_ANNUAL_PASS
                        == pass_type_name
                    ):
                        return ExternalCreatePinjarOffRoadPassSerializer

                    error = "ERROR: No valid pass type name found in POST."
                    logger.error(error)
                    raise NoValidPassTypeFoundInPost(error)

        return ExternalPassSerializer

    def perform_create(self, serializer):
        logger.debug("perform create -------------\n\n")
        logger.debug("serializer data = " + str(serializer.validated_data))

        # Pop these values out so they don't mess with the model serializer
        discount_code = serializer.validated_data.pop("discount_code", None)
        voucher_code = serializer.validated_data.pop("voucher_code", None)
        voucher_pin = serializer.validated_data.pop("voucher_pin", None)
        concession_id = serializer.validated_data.pop("concession_id", None)
        concession_card_number = serializer.validated_data.pop(
            "concession_card_number", None
        )

        sold_via = serializer.validated_data.pop("sold_via", None)

        if is_customer(self.request):
            park_pass = serializer.save(user=self.request.user.id)
        else:
            park_pass = serializer.save()

        logger.debug("park_pass.sold_via = " + str(park_pass.sold_via))

        if sold_via and RetailerGroup.objects.filter(id=sold_via).exists():
            park_pass.sold_via = RetailerGroup.objects.get(id=sold_via)
        else:
            park_pass.sold_via = RetailerGroup.get_dbca_retailer_group()

        park_pass.save()

        cart_id = self.request.session.get("cart_id", None)
        if cart_id and Cart.objects.filter(id=cart_id).exists():
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = Cart()
            cart.save()
            self.request.session["cart_id"] = cart.id

        content_type = ContentType.objects.get_for_model(park_pass)
        cart_item = CartItem(
            cart=cart, object_id=park_pass.id, content_type=content_type
        )

        """ If the user deletes a cart item, any objects that can be attached to a cart item
        (concession usage, discount code usage and voucher transaction)
        are deleted in the cart item's delete method  """
        if concession_id and concession_card_number:
            if Concession.objects.filter(id=concession_id).exists():
                concession = Concession.objects.get(id=concession_id)
                concession_usage = ConcessionUsage.objects.create(
                    concession=concession,
                    park_pass=park_pass,
                    concession_card_number=concession_card_number,
                )
                cart_item.concession_usage = concession_usage

        if discount_code:
            pass_type_id = park_pass.option.pricing_window.pass_type.id
            if DiscountCode.is_valid(discount_code, self.request.user.id, pass_type_id):
                discount_code = DiscountCode.objects.get(code=discount_code)
                discount_code_usage = DiscountCodeUsage.objects.create(
                    discount_code=discount_code, park_pass=park_pass
                )
                cart_item.discount_code_usage = discount_code_usage

        if voucher_code:
            if Voucher.is_valid(voucher_code, voucher_pin):
                voucher = Voucher.objects.get(code=voucher_code, pin=voucher_pin)
                voucher_transaction = VoucherTransaction.objects.create(
                    voucher=voucher,
                    park_pass=park_pass,
                    debit=voucher.balance_available_for_purchase(
                        park_pass.price_after_discount_code_applied
                    ),
                    credit=Decimal(0.00),
                )
                cart_item.voucher_transaction = voucher_transaction

        # Save to apply any concession usages, discount code usages or voucher transactions to the cart item
        cart_item.save()

        if is_customer(self.request):
            CartUtils.increment_cart_item_count(self.request)

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

    @action(methods=["GET"], detail=True, url_path="retrieve-invoice")
    def retrieve_invoice(self, request, *args, **kwargs):
        park_pass = self.get_object()
        logger.debug("user = " + str(self.request.user.id))
        content_type = ContentType.objects.get_for_model(Pass)
        if OrderItem.objects.filter(
            object_id=park_pass.id, content_type=content_type
        ).exists():
            order_item = OrderItem.objects.get(
                object_id=park_pass.id, content_type=content_type
            )
            invoice_url = order_item.order.invoice_link
            if invoice_url:
                response = requests.get(invoice_url)
                return FileResponse(response, content_type="application/pdf")

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
            queryset = queryset.filter(date_start__gte=start_date_from)

        if start_date_to:
            queryset = queryset.filter(date_start__lte=start_date_to)

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

    @action(methods=["GET"], detail=True, url_path="retrieve-park-pass-pdf")
    def retrieve_park_pass_pdf(self, request, *args, **kwargs):
        if RetailerGroupUser.objects.filter(
            emailuser__id=self.request.user.id
        ).exists():
            retailer_groups = RetailerGroupUser.objects.filter(
                emailuser__id=self.request.user.id
            ).values_list("retailer_group__id", flat=True)
            park_pass = self.get_object()
            logger.debug("park_pass.sold_via = " + str(park_pass.sold_via.id))
            logger.debug("list(retailer_groups) = " + str(list(retailer_groups)))
            if park_pass.sold_via.id in list(retailer_groups):
                if park_pass.park_pass_pdf:
                    return FileResponse(park_pass.park_pass_pdf)
        raise Http404


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
    queryset = Pass.objects.exclude(in_cart=True)
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
            user_action = settings.ACTION_CANCEL
            object_id = serializer.data["park_pass"]
            content_type = ContentType.objects.get_for_model(Pass)
            user_action = UserAction.objects.log_action(
                object_id=object_id,
                content_type=content_type,
                who=request.user.id,
                what=user_action.format(Pass._meta.model.__name__, object_id),
                why=serializer.data["cancellation_reason"],
            )
            extended_serializer = {
                "user_action": UserActionSerializer(user_action).data
            }
            extended_serializer.update(serializer.data)
            return Response(extended_serializer, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
