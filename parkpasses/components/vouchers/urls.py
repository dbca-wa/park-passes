from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.vouchers.api import (
    ExternalVoucherViewSet,
    InternalVoucherViewSet,
    ValidateVoucherView,
    VoucherTransactionViewSet,
)

router = routers.SimpleRouter()

router.register(
    r"external/vouchers", ExternalVoucherViewSet, basename="external-vouchers"
)
router.register(
    r"internal/vouchers", InternalVoucherViewSet, basename="internal-vouchers"
)
router.register(
    r"internal/voucher-transactions",
    VoucherTransactionViewSet,
    basename="internal-voucher-transactions",
)

urlpatterns = [
    url(r"validate-voucher", ValidateVoucherView.as_view()),
]

urlpatterns = router.urls + urlpatterns
