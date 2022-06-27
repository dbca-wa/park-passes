from rest_framework import routers

from parkpasses.components.discount_codes.api import (
    DiscountCodeBatchCommentViewSet,
    DiscountCodeBatchViewSet,
    DiscountCodeViewSet,
)

router = routers.SimpleRouter()

router.register(r"discount-codes", DiscountCodeViewSet, basename="discount-codes")
router.register(
    r"discount-code-batches", DiscountCodeBatchViewSet, basename="discount-code-batches"
)
router.register(
    r"discount-code-batch-comments",
    DiscountCodeBatchCommentViewSet,
    basename="discount-code-batch-comment",
)

urlpatterns = router.urls
