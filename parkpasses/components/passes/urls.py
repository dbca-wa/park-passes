from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.passes.api import (
    CancelPass,
    CurrentOptionsForPassType,
    DefaultOptionsForPassType,
    ExternalPassTypeViewSet,
    ExternalPassViewSet,
    InternalPassTypeViewSet,
    InternalPassViewSet,
    InternalPricingWindowViewSet,
    PassProcessingStatusesDistinct,
    PassTemplateViewSet,
    PassTypePricingWindowOptionViewSet,
    PassTypesDistinct,
    RetailerPassTypeViewSet,
    RetailerPassViewSet,
)

router = routers.SimpleRouter()
router.register(
    r"external/pass-types", ExternalPassTypeViewSet, basename="pass-types-external"
)
router.register(
    r"retailer/pass-types", RetailerPassTypeViewSet, basename="pass-types-retailer"
)
router.register(
    r"internal/pass-types", InternalPassTypeViewSet, basename="pass-types-internal"
)
router.register(
    r"internal/pricing-windows",
    InternalPricingWindowViewSet,
    basename="pricing-windows-internal",
)
router.register(
    r"pass-options", PassTypePricingWindowOptionViewSet, basename="pass-options"
)
router.register(r"pass-templates", PassTemplateViewSet, basename="pass-templates")
router.register(r"external/passes", ExternalPassViewSet, basename="passes-external")
router.register(r"retailer/passes", RetailerPassViewSet, basename="passes-internal")
router.register(r"internal/passes", InternalPassViewSet, basename="passes-internal")

urlpatterns = [
    url(r"pass-types-distinct", PassTypesDistinct.as_view()),
    url(r"pass-processing-statuses-distinct", PassProcessingStatusesDistinct.as_view()),
    url(r"default-pass-options-by-pass-type-id", DefaultOptionsForPassType.as_view()),
    url(r"pass-options-by-pass-type-id", CurrentOptionsForPassType.as_view()),
    url(r"cancel-pass", CancelPass.as_view()),
]

urlpatterns += router.urls
