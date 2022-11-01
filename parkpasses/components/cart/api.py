import logging

from django.http import Http404
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
from parkpasses.components.passes.models import Pass
from parkpasses.components.retailers.models import RetailerGroup
from parkpasses.helpers import is_customer, is_internal, is_retailer

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
        try:
            cart_item = self.get_object()
            CartUtils.decrement_cart_item_count(request)
            logger.info(
                f"Destroyed Cart Item {cart_item} {cart_item.cart}",
                extra={"className": self.__class__.__name__},
            )
            return super().destroy(request, *args, **kwargs)
        except Http404:
            pass

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
        logger.info(
            f"Retrieving cart for user: {request.user.id} ({request.user})",
            extra={"className": self.__class__.__name__},
        )

        cart = Cart.get_or_create_cart(request)
        logger.info(f"{cart} retrieved", extra={"className": self.__class__.__name__})

        cart_items = []
        for cart_item in cart.items.all():
            item = CartUtils.get_serialized_object_by_id_and_content_type(
                cart_item.object_id, cart_item.content_type.id
            )
            item["cart_item_id"] = cart_item.id
            item["cart_id"] = cart.id
            cart_items.append(item)

        logger.info(
            f"Cart items in {cart}: {cart_items}",
            extra={"className": self.__class__.__name__},
        )

        return Response(cart_items)


class LedgerCheckoutView(APIView):
    def post(self, request, format=None):
        cart = Cart.get_or_create_cart(request)
        logger.debug("cart = " + str(cart))
        if not cart.items.all().exists():
            return redirect(reverse("cart"))

        if is_retailer(request):
            retailer_group_id = self.request.POST.get("retailer_group_id", None)
            if retailer_group_id:
                if RetailerGroup.objects.filter(id=retailer_group_id).exists():
                    retailer_group = RetailerGroup.objects.get(id=retailer_group_id)
                    cart.retailer_group = retailer_group
                    cart.save()
                    cart_item = cart.items.first()
                    if Pass.objects.filter(id=cart_item.object_id).exists():
                        # Mark the pass as no longer in cart this will prevent it
                        # being deleted when the cart item is deleted
                        park_pass = Pass.objects.get(id=cart_item.object_id)
                        park_pass.in_cart = False
                        park_pass.save()

                        # Remove the cart item and cart and reset the cart details
                        cart_item.delete()
                        cart.delete()
                        CartUtils.reset_cart_item_count(request)
                        CartUtils.remove_cart_id_from_session(request)

                        return redirect(
                            reverse(
                                "retailer-pass-created-successfully",
                                kwargs={"id": park_pass.id},
                            )
                        )

        ledger_order_lines = CartUtils.get_ledger_order_lines(request, cart)

        basket_parameters = CartUtils.get_basket_parameters(
            ledger_order_lines, cart.uuid, is_no_payment=False
        )
        logger.debug("\nbasket_parameters = " + str(basket_parameters))

        create_basket_session(request, request.user.id, basket_parameters)
        invoice_text = f"Park Passes Order: {cart.uuid}"
        logger.debug("\ninvoice_text = " + invoice_text)
        return_url = request.build_absolute_uri(
            reverse("checkout-success", kwargs={"uuid": cart.uuid})
        )
        return_preload_url = request.build_absolute_uri(
            reverse("ledger-api-success-callback", kwargs={"uuid": cart.uuid})
        )
        checkout_parameters = CartUtils.get_checkout_parameters(
            request, return_url, return_preload_url, cart.user, invoice_text
        )
        logger.debug("\ncheckout_parameters = " + str(checkout_parameters))

        create_checkout_session(request, checkout_parameters)

        return redirect(reverse("ledgergw-payment-details"))


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
                invoice_reference=invoice_reference,
            )

            logger.debug(f"uuid: \n{uuid} invoice_reference: {invoice_reference} \n")

            CartUtils.reset_cart_item_count(request)
            CartUtils.remove_cart_id_from_session(request)
            # this end-point is called by an unmonitored get request in ledger so there is no point having a
            # a response body however we will return a status in case this is used on the ledger end in future
            return Response(status=status.HTTP_204_NO_CONTENT)

        CartUtils.reset_cart_item_count(request)
        # If there is no uuid to identify the cart then send a bad request status back in case ledger can
        # do something with this in future
        return Response(status=status.HTTP_400_BAD_REQUEST)
