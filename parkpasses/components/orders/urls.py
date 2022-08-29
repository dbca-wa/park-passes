from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.orders.api import (
    ExternalOrderByUUID,
    ExternalOrderViewSet,
    OrderItemViewSet,
    OrderViewSet,
)

router = routers.SimpleRouter()

router.register(r"external/orders", ExternalOrderViewSet, basename="orders-external")
router.register(r"internal/orders", OrderViewSet, basename="orders")
router.register(r"order-items", OrderItemViewSet, basename="order-items")

urlpatterns = [
    url(
        r"external/order-by-uuid/(?P<uuid>.+)/",
        ExternalOrderByUUID.as_view(),
        name="order-by-uuid",
    ),
]

urlpatterns += router.urls
