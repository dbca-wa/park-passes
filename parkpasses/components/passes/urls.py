from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.passes.api import (
    CurrentOptionsForPassType,
    ExternalPassViewSet,
    PassProcessingStatusesDistinct,
    PassTemplateViewSet,
    PassTypePricingWindowOptionViewSet,
    PassTypesDistinct,
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
router.register(r"external/passes", ExternalPassViewSet, basename="passes-external")
router.register(r"passes", PassViewSet, basename="passes")

urlpatterns = [
    url(r"pass-types-distinct", PassTypesDistinct.as_view()),
    url(r"pass-processing-statuses-distinct", PassProcessingStatusesDistinct.as_view()),
    url(r"pass-options-by-pass-type-id", CurrentOptionsForPassType.as_view()),
]

urlpatterns += router.urls
