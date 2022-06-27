from rest_framework import routers

from parkpasses.components.cart.api import CartItemViewSet, CartViewSet

router = routers.SimpleRouter()

router.register(r"carts", CartViewSet, basename="carts")
router.register(r"cart-items", CartItemViewSet, basename="cart-items")

urlpatterns = router.urls
