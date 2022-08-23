from rest_framework import routers

from parkpasses.components.orders.api import (
    ExternalOrderViewSet,
    OrderItemViewSet,
    OrderViewSet,
)

router = routers.SimpleRouter()

router.register(r"external/orders", ExternalOrderViewSet, basename="orders-external")
router.register(r"internal/orders", OrderViewSet, basename="orders")
router.register(r"order-items", OrderItemViewSet, basename="order-items")

urlpatterns = router.urls
