import logging

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from parkpasses.components.cart.models import Cart, CartItem
from parkpasses.components.cart.serializers import CartItemSerializer, CartSerializer
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
        user_id = self.request.user.id
        return Cart.objects.filter(user=user_id)


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
        user_id = self.request.user.id
        return CartItem.objects.filter(cart__user=user_id)
