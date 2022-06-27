from rest_framework import routers

from parkpasses.components.discount_codes.api import DiscountCodeViewSet

router = routers.SimpleRouter()

router.register(r"discount-codes", DiscountCodeViewSet, basename="discount-codes")

urlpatterns = router.urls
