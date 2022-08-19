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
    r"voucher-transactions", VoucherTransactionViewSet, basename="voucher-transactions"
)

urlpatterns = [
    url(r"validate-voucher", ValidateVoucherView.as_view()),
]

urlpatterns = router.urls + urlpatterns
