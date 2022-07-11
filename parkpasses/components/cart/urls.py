from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.cart.api import CartItemViewSet, CartViewSet, CheckoutView

router = routers.SimpleRouter()

router.register(r"carts", CartViewSet, basename="carts")
router.register(r"cart-items", CartItemViewSet, basename="cart-items")

urlpatterns = [
    url(r"checkout", CheckoutView.as_view()),
]

urlpatterns = router.urls + urlpatterns
