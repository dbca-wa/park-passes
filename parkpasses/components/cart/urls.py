from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.cart.api import (
    CartItemViewSet,
    CartViewSet,
    CheckoutView,
    SuccessView,
)

router = routers.SimpleRouter()

router.register(r"carts", CartViewSet, basename="carts")
router.register(r"cart-items", CartItemViewSet, basename="cart-items")

urlpatterns = [
    url(r"checkout", CheckoutView.as_view()),
    url(r"checkout-success", SuccessView.as_view(), name="checkout-success"),
]

urlpatterns = router.urls + urlpatterns
