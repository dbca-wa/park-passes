from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.cart.api import (
    CartItemViewSet,
    CartView,
    CartViewSet,
    SuccessView,
)

router = routers.SimpleRouter()

router.register(r"carts", CartViewSet, basename="carts")
router.register(r"cart-items", CartItemViewSet, basename="cart-items")

urlpatterns = [
    url(
        r"ledger-api-success-callback/(?P<uuid>.+)/",
        SuccessView.as_view(),
        name="ledger-api-success-callback",
    ),
    url(r"cart", CartView.as_view(), name="cart"),
]

urlpatterns = router.urls + urlpatterns
