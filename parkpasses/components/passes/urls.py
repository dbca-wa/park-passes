from rest_framework import routers

from parkpasses.components.passes.api import (
    PassTemplateViewSet,
    PassTypePricingWindowOptionViewSet,
    PassTypeViewSet,
    PassViewSet,
    PricingWindowViewSet,
)

router = routers.SimpleRouter()
router.register(r"pass-types", PassTypeViewSet, basename="pass-types")
router.register(
    r"pricing-windows", PricingWindowViewSet, basename="pass-type-pricing-windows"
)
router.register(
    r"pass-options", PassTypePricingWindowOptionViewSet, basename="pass-options"
)
router.register(r"pass-templates", PassTemplateViewSet, basename="pass-templates")
router.register(r"passes", PassViewSet, basename="passes")
urlpatterns = router.urls
