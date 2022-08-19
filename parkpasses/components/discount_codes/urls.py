from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.discount_codes.api import (
    DiscountCodeBatchCommentViewSet,
    DiscountCodeViewSet,
    DiscountCodeXlsxViewSet,
    InternalDiscountCodeBatchViewSet,
    ValidateDiscountCodeView,
)

router = routers.SimpleRouter()

router.register(
    r"external/discount-codes", DiscountCodeViewSet, basename="external-discount-codes"
)
router.register(
    r"internal/discount-codes", DiscountCodeViewSet, basename="internal-discount-codes"
)
router.register(
    r"internal/discount-codes-xlsx/(?P<discount_code_batch_id>.+)",
    DiscountCodeXlsxViewSet,
    basename="internal-discount-codes-xlsx",
)
router.register(
    r"internal/discount-code-batches",
    InternalDiscountCodeBatchViewSet,
    basename="discount-code-batches",
)
router.register(
    r"discount-code-batch-comments",
    DiscountCodeBatchCommentViewSet,
    basename="discount-code-batch-comment",
)

urlpatterns = [
    url(r"validate-discount-code", ValidateDiscountCodeView.as_view()),
]

urlpatterns = router.urls + urlpatterns
