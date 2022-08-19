from rest_framework import routers

from parkpasses.components.orders.api import OrderItemViewSet, OrderViewSet

router = routers.SimpleRouter()

router.register(r"orders", OrderViewSet, basename="orders")
router.register(r"order-items", OrderItemViewSet, basename="order-items")

urlpatterns = router.urls
