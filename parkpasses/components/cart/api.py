import logging
import pprint

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from ledger_api_client.utils import create_basket_session, create_checkout_session
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from parkpasses.components.cart.models import Cart, CartItem
from parkpasses.components.cart.serializers import CartItemSerializer, CartSerializer
from parkpasses.components.cart.utils import CartUtils
from parkpasses.helpers import is_customer, is_internal

logger = logging.getLogger(__name__)


class CartViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on carts.
    """

    model = Cart
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if is_internal(self.request):
            return Cart.objects.all()

        cart_id = self.request.session.get("cart_id", None)
        if cart_id and Cart.objects.filter(id=cart_id).exists():
            return Cart.objects.get(id=cart_id)
        else:
            return Cart.objects.none()


class CartItemViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on cart items.
    """

    model = CartItem
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if is_internal(self.request):
            return CartItem.objects.all()
        cart_id = self.request.session.get("cart_id", None)
        if cart_id and Cart.objects.filter(id=cart_id).exists():
            return CartItem.objects.filter(cart_id=cart_id)
        else:
            return CartItem.objects.none()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        logger.debug("cart_item = " + str(instance))
        instance.delete_attached_object()  # will delete the voucher or pass attached to the cart item
        CartUtils.decrement_cart_item_count(request)
        return super().destroy(request, *args, **kwargs)

    def has_object_permission(self, request, view, obj):
        if is_internal(request):
            return True
        if is_customer(request):
            if obj.cart.user == request.user.id:
                return True
        return False


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        cart = Cart.get_or_create_cart(request)
        objects = []
        for cart_item in cart.items.all():
            item = CartUtils.get_serialized_object_by_id_and_content_type(
                cart_item.object_id, cart_item.content_type.id
            )
            item["cart_item_id"] = cart_item.id
            item["cart_id"] = cart.id
            objects.append(item)
        return Response(objects)


class LedgerCheckoutView(APIView):
    def get_ledger_order_lines(self, cart):
        ledger_order_lines = []
        line_status = settings.PARKPASSES_LEDGER_DEFAULT_LINE_STATUS

        order, order_items = cart.create_order()
        for order_item in order_items:
            if settings.DEBUG:
                order_item.amount = int(order_item.amount)
                order_item.description += " (Price rounded for dev env)"
            ledger_order_line = {
                "ledger_description": order_item.description,
                "quantity": 1,
                "price_incl_tax": str(order_item.amount),
                "oracle_code": CartUtils.get_oracle_code(),
                "line_status": line_status,
            }
            ledger_order_lines.append(ledger_order_line)
            logger.debug(pprint.pformat(ledger_order_line))
        return ledger_order_lines

    # Todo: Change this to post once it's working.
    def get(self, request, format=None):
        cart = Cart.get_or_create_cart(request)
        if cart.items.all().exists():
            ledger_order_lines = self.get_ledger_order_lines(cart)
            is_no_payment = self.request.POST.get("no_payment", "false")
            basket_parameters = CartUtils.get_basket_parameters(
                ledger_order_lines, is_no_payment
            )
            logger.debug("\nbasket_parameters = " + str(basket_parameters))

            create_basket_session(request, request.user.id, basket_parameters)
            invoice_text = (
                f'Park Passes Order: {{"user":{request.user.id}, "uuid": {cart.uuid} }}'
            )
            logger.debug("\ninvoice_text = " + invoice_text)
            checkout_parameters = CartUtils.get_checkout_parameters(
                request, cart, invoice_text
            )
            logger.debug("\ncheckout_parameters = " + str(checkout_parameters))

            create_checkout_session(request, checkout_parameters)

            return redirect(reverse("ledgergw-payment-details"))

        # Return the user to the empty cart page
        return redirect(reverse("cart"))


class SuccessView(APIView):
    # permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle]

    def get(self, request, uuid, format=None):
        logger.debug("\n\nParkPasses SuccessView get method called.\n\n")
        invoice_reference = request.GET.get("invoice", "false")
        logger.debug(f"uuid:{uuid} invoice_reference: {invoice_reference} \n")
        if uuid and invoice_reference:
            # TODO: decide what to do if that cart has expired and been deleted
            cart = Cart.objects.get(uuid=uuid)
            # Create the order and order lines, save them to the database and then delete the cart.
            logger.debug("\n\ncart = " + str(cart))
            order, order_items = cart.create_order(
                save_order_to_db_and_delete_cart=True,
                uuid=uuid,
                invoice_reference=invoice_reference,
            )

            logger.debug(f"uuid: \n{uuid} invoice_reference: {invoice_reference} \n")

            CartUtils.reset_cart_item_count(request)
            CartUtils.remove_cart_id_from_session(request)
            # this end-point is called by an unmonitored get request in ledger so there is no point having a
            # a response body however we will return a status in case this is used on the ledger end in future
            return Response(status=status.HTTP_204_NO_CONTENT)

        request.session["cart_item_count"] = 0
        logger.debug("FFS =====================>")
        # If there is no uuid to identify the cart then sent a bad request status back in case ledger can
        # do something with this in future
        return Response(status=status.HTTP_400_BAD_REQUEST)
