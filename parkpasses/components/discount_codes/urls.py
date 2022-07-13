from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.discount_codes.api import (
    DiscountCodeBatchCommentViewSet,
    DiscountCodeBatchViewSet,
    DiscountCodeViewSet,
    ValidateDiscountCodeView,
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

urlpatterns = [
    url(r"validate-discount-code", ValidateDiscountCodeView.as_view()),
]

urlpatterns = router.urls + urlpatterns
