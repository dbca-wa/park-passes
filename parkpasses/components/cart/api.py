import logging

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from parkpasses.components.cart.models import Cart, CartItem
from parkpasses.components.cart.serializers import CartItemSerializer, CartSerializer
from parkpasses.components.cart.utils import CartUtils
from parkpasses.helpers import is_internal

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
            return Cart.objects.filter(id=cart_id)
        else:
            return Cart.objects.none()


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        if self.request.session.get("cart_id", None):
            cart_id = self.request.session["cart_id"]
            cart = Cart.objects.get(id=cart_id)
            logger.debug("cart = " + str(cart))
            logger.debug("cart.items = " + str(cart.items))
            cart_items = CartItem.objects.filter(cart=cart)
            objects = []
            for cart_item in cart_items:
                item = CartUtils.get_serialized_object_by_id_and_content_type(
                    cart_item.object_id, cart_item.content_type.id
                )
                objects.append(item)
            return Response(objects)
        else:
            return Response([])
