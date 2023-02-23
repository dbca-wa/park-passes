import logging

from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from ledger_api_client.utils import create_basket_session, create_checkout_session
from ledger_api_client.utils import get_or_create as get_or_create_emailuser
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
from parkpasses.exceptions import LedgerAPIException
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
        logger.info(f"Retrieving cart for user: {request.user.id} ({request.user})")

        cart = Cart.get_or_create_cart(request)
        logger.info(f"{cart} retrieved")

        cart_items = []
        for cart_item in cart.items.all():
            item = CartUtils.get_serialized_object_by_id_and_content_type(
                cart_item.object_id, cart_item.content_type.id
            )
            item["cart_item_id"] = cart_item.id
            item["cart_id"] = cart.id
            cart_items.append(item)

        logger.info(f"Cart items in {cart}: {cart_items}")

        return Response(cart_items)


class LedgerCheckoutView(APIView):
    def post(self, request, format=None):
        cart = Cart.get_or_create_cart(request)
        if not cart.items.all().exists():
            logger.info(
                f"Cart: {cart} is empty. Redirecting to cart page.",
            )
            return redirect(reverse("user-cart"))

        is_bpoint_sale = False
        is_bpoint_sale_param = self.request.POST.get("is_bpoint_sale", False)
        if "true" == is_bpoint_sale_param:
            is_bpoint_sale = True

        if is_retailer(request):
            logger.info(
                "User is a retailer.",
            )
            retailer_group_id = self.request.POST.get("retailer_group_id", None)
            logger.info(
                f"Retailer group id: {retailer_group_id}.",
            )
            if not (
                retailer_group_id
                and RetailerGroup.objects.filter(id=retailer_group_id).exists()
            ):
                logger.info(
                    f"Retailer group with id: {retailer_group_id} does not exist. Redirecting user to cart page.",
                )
                return redirect(reverse("user-cart"))

            logger.info(
                f"Retailer group with id: {retailer_group_id} exists.",
            )
            retailer_group = RetailerGroup.objects.get(id=retailer_group_id)
            cart.retailer_group = retailer_group
            logger.info(
                f"Retailer group with id: {retailer_group_id} assigned to cart: {cart}.",
            )
            logger.info(
                f"Saving cart: {cart}.",
            )
            cart.save()
            logger.info(
                f"Cart: {cart} saved.",
            )
            # A retailer cart should only ever have one pass in it
            cart_item = cart.items.first()
            if not Pass.objects.filter(id=cart_item.object_id).exists():
                return redirect(reverse("user-cart"))

            # Mark the pass as no longer in cart this will prevent it
            # being deleted when the cart item is deleted
            park_pass = Pass.objects.get(id=cart_item.object_id)

            if not is_bpoint_sale:
                logger.info(
                    "Sale is not .",
                )
                park_pass.in_cart = False
                logger.info(
                    f"Park pass: {park_pass} set as in_cart = False.",
                )
                logger.info(
                    f"Saving Park pass: {park_pass}.",
                )
                park_pass.save()
                logger.info(
                    f"Park pass: {park_pass} saved.",
                )

                # Remove the cart item and cart and reset the cart details
                logger.info(
                    f"Deleting cart item: {cart_item}.",
                )
                cart_item.delete()
                logger.info(
                    f"Cart item: {cart_item} deleted.",
                )
                logger.info(
                    f"Deleting cart: {cart}.",
                )
                cart.delete()
                logger.info(
                    f"Cart: {cart} deleted.",
                )
                CartUtils.reset_cart_item_count(request)
                CartUtils.remove_cart_id_from_session(request)

                logger.info(
                    f"Redirecting retailer to form for park pass {park_pass} with success message.",
                )
                return redirect(
                    reverse(
                        "retailer-pass-created-successfully",
                        kwargs={"id": park_pass.id},
                    )
                )

        ledger_order_lines = CartUtils.get_ledger_order_lines(request, cart)

        logger.info("Getting basket parameters.")
        basket_parameters = CartUtils.get_basket_parameters(
            ledger_order_lines, cart.uuid, is_no_payment=False
        )

        logger.info(
            f"Creating basket session with basket parameters: {basket_parameters}"
        )

        basket_user_id = request.user.id
        return_url = request.build_absolute_uri(
            reverse("checkout-success", kwargs={"uuid": cart.uuid})
        )

        if is_bpoint_sale:
            logger.info(
                f"is_bpoint_sale: {is_bpoint_sale}. Setting return url to internal pass created successfully page.",
            )
            return_url = request.build_absolute_uri(
                reverse(
                    "retailer-pass-created-successfully",
                    kwargs={"id": park_pass.id},
                )
            )
            basket_user_response = get_or_create_emailuser(park_pass.email)
            if not 200 == basket_user_response["status"]:
                code = basket_user_response["status"]
                message = basket_user_response["message"]
                logger.error(
                    f"Error encountered trying to run get_or_create emailuser via api. Code: {code}, Message: {message}"
                )
                raise LedgerAPIException(code=code, detail=message)
            basket_user_id = basket_user_response["data"]["emailuser_id"]

        create_basket_session(request, basket_user_id, basket_parameters)

        return_preload_url = request.build_absolute_uri(
            reverse("ledger-api-success-callback", kwargs={"uuid": cart.uuid})
        )
        invoice_text = f"Park Passes Order: {cart.uuid}"
        checkout_parameters = CartUtils.get_checkout_parameters(
            request, return_url, return_preload_url, basket_user_id, invoice_text
        )
        logger.info(
            f"Creating checkout session with checkout parameters: {checkout_parameters}"
        )
        create_checkout_session(request, checkout_parameters)

        logger.info("Redirecting user to ledgergw payment details page.")
        return redirect(reverse("ledgergw-payment-details"))


class SuccessView(APIView):
    throttle_classes = [AnonRateThrottle]

    def get(self, request, uuid, format=None):
        logger.info("Park passes Cart API SuccessView get method called.")

        invoice_reference = request.GET.get("invoice", "false")

        if uuid and invoice_reference:
            logger.info(
                f"Invoice reference: {invoice_reference} and uuid: {uuid}.",
            )
            if not Cart.objects.filter(uuid=uuid).exists():
                return redirect(reverse("user-cart"))

            cart = Cart.objects.get(uuid=uuid)

            order, order_items = cart.create_order(
                save_order_to_db_and_delete_cart=True,
                invoice_reference=invoice_reference,
            )

            CartUtils.reset_cart_item_count(request)
            CartUtils.remove_cart_id_from_session(request)

            logger.info(
                "Returning status.HTTP_200_OK. Order created successfully.",
            )
            # this end-point is called by an unmonitored get request in ledger so there is no point having a
            # a response body however we will return a status in case this is used on the ledger end in future
            return Response(status=status.HTTP_200_OK)

        CartUtils.reset_cart_item_count(request)
        # If there is no uuid to identify the cart then send a bad request status back in case ledger can
        # do something with this in future
        logger.info(
            "Returning status.HTTP_400_BAD_REQUEST bad request as there was not a uuid and invoice_reference."
        )
        return Response(status=status.HTTP_400_BAD_REQUEST)
