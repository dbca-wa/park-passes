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
    PassRefundSuccessView,
    PassTemplateViewSet,
    PassTypePricingWindowOptionViewSet,
    PassTypesDistinct,
    RacDiscountCodeCheckView,
    RacDiscountCodeView,
    RetailerApiAccessViewSet,
    RetailerPassTypesDistinct,
    RetailerPassTypeViewSet,
    RetailerPassViewSet,
    UploadPersonnelPasses,
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
router.register(
    r"retailer/api-key-access",
    RetailerApiAccessViewSet,
    basename="passes-external-api-key-access",
)

urlpatterns = [
    url(r"retailer-pass-types/$", RetailerPassTypesDistinct.as_view()),
    url(r"pass-types-distinct", PassTypesDistinct.as_view()),
    url(r"pass-processing-statuses-distinct", PassProcessingStatusesDistinct.as_view()),
    url(r"default-pass-options-by-pass-type-id", DefaultOptionsForPassType.as_view()),
    url(r"pass-options-by-pass-type-id", CurrentOptionsForPassType.as_view()),
    url(r"rac/generate-code-from-email/(?P<email>.+)$", RacDiscountCodeView.as_view()),
    url(r"rac/generate-code-from-email/$", RacDiscountCodeView.as_view()),
    url(
        r"rac/check-hash-matches-email/(?P<discount_hash>.+)/(?P<email>.+)/$",
        RacDiscountCodeCheckView.as_view(),
    ),
    url(r"cancel-pass", CancelPass.as_view()),
    url(r"upload-personnel-passes", UploadPersonnelPasses.as_view()),
    url(
        r"ledger-api-refund-success-callback/(?P<id>.+)/(?P<uuid>.+)$",
        PassRefundSuccessView.as_view(),
        name="ledger-api-refund-success-callback",
    ),
]

urlpatterns += router.urls
