from rest_framework import routers

from parkpasses.components.vouchers.api import VoucherTransactionViewSet, VoucherViewSet

router = routers.SimpleRouter()

router.register(r"vouchers", VoucherViewSet, basename="vouchers")
router.register(
    r"voucher-transactions", VoucherTransactionViewSet, basename="voucher-transactions"
)

urlpatterns = router.urls
