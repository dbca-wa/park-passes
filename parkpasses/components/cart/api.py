import logging
import pprint

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.urls import reverse
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from ledger_api_client.utils import create_basket_session, create_checkout_session
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from parkpasses.components.cart.models import Cart, CartItem
from parkpasses.components.cart.serializers import CartItemSerializer, CartSerializer
from parkpasses.components.cart.utils import CartUtils
from parkpasses.components.orders.serializers import OrderListItemSerializer
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
        if self.request.session.get("cart_id", None):
            cart_id = self.request.session["cart_id"]
            return Cart.objects.filter(id=cart_id)
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
        if self.request.session.get("cart_id", None):
            cart_id = self.request.session["cart_id"]
            return CartItem.objects.filter(cart_id=cart_id)
        else:
            return CartItem.objects.none()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # cart_item = instance.content_type.get_object_for_this_type(pk=instance.object_id)
        logger.debug("cart_item = " + str(instance))
        instance.delete_attached_object()  # will delete the voucher or pass attached to the cart item
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
        if request.session.get("cart_id", None):
            cart_id = request.session["cart_id"]
            cart = Cart.objects.get(id=cart_id)
            logger.debug("cart = " + str(cart))
            logger.debug("cart.items = " + str(cart.items))
            purchaser = EmailUser.objects.get(id=cart.user)
            cart_items = CartItem.objects.filter(cart=cart)
            objects = []
            for cart_item in cart_items:
                item = CartUtils.get_serialized_object_by_id_and_content_type(
                    cart_item.object_id, cart_item.content_type.id
                )
                item.purchaser_email = purchaser.email
                item.purchaser_first_name = purchaser.first_name
                item.purchaser_last_name = purchaser.last_name
                item["cart_item_id"] = cart_item.id
                logger.debug("item = " + str(item))
                objects.append(item)
            return Response(objects)
        else:
            # Todo: Raise exception or redirect to homepage here?
            return Response([])


class LedgerCheckoutView(APIView):
    def get_ledger_order_lines(self, cart):
        ledger_order_lines = []
        ledger_order_line_descriptions = []
        line_status = settings.PARKPASSES_LEDGER_DEFAULT_LINE_STATUS

        order, order_items = cart.create_order()
        for order_item in order_items:
            ledger_order_line = {
                "ledger_description": order_item.description,
                "quantity": 1,
                "price_incl_tax": str(order_item.amount),
                "oracle_code": CartUtils.get_oracle_code(),
                "line_status": line_status,
            }
            ledger_order_lines.append(ledger_order_line)
            ledger_order_line_descriptions.append(order_item.description)
            logger.debug(pprint.pformat(ledger_order_line))
        return ledger_order_lines, ledger_order_line_descriptions

    # Todo: Change this to post once it's working.
    def get(self, request, format=None):
        if self.request.session.get("cart_id", None):
            cart_id = request.session["cart_id"]
            cart = Cart.objects.get(id=cart_id)
            (
                ledger_order_lines,
                ledger_order_line_descriptions,
            ) = self.get_ledger_order_lines(cart)
            is_no_payment = self.request.POST.get("no_payment", "false")
            basket_parameters = CartUtils.get_basket_parameters(
                ledger_order_lines, is_no_payment
            )
            logger.debug("basket_parameters = " + str(basket_parameters))
            create_basket_session(request, request.user.id, basket_parameters)
            logger.debug(request.user)
            invoice_text = f"Park Passes Purchase for {request.user} [{','.join(ledger_order_line_descriptions)}]"
            logger.debug("invoice_text = " + invoice_text)
            checkout_parameters = CartUtils.get_checkout_parameters(
                request, cart, invoice_text
            )
            logger.debug("checkout_parameters = " + str(checkout_parameters))
            create_checkout_session(request, checkout_parameters)
            return redirect(reverse("ledgergw-payment-details"))

        # Todo send user to a page that says their cart has expired?
        pass


class SuccessView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        uuid = self.request.query_params.get("uuid")
        cart_id = self.request.query_params.get("cart_id")
        if uuid and cart_id:
            try:
                cart = Cart.objects.get(id=cart_id, uuid=uuid)
            except ObjectDoesNotExist:
                logger.warning(
                    "Client has requested cart success view for cart with id:\
                     {} and uuid: {}. No such cart exists.".format(
                        cart_id, uuid
                    )
                )
                return Response([])
            # Create the order and order lines, save them to the database and then delete the cart.
            order, order_items = cart.create_order(True)
            serializer = OrderListItemSerializer(order)

            return Response(serializer.data)

        return Response({"Nope, didn't work"})
