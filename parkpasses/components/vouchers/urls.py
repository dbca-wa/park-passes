from rest_framework import routers

from parkpasses.components.vouchers.api import (
    ExternalVoucherViewSet,
    InternalVoucherViewSet,
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
    r"voucher-transactions", VoucherTransactionViewSet, basename="voucher-transactions"
)

urlpatterns = router.urls
