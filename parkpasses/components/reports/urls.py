from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.reports.api import (
    InternalReportViewSet,
    PayInvoiceSuccessCallbackView,
    RetailerReportViewSet,
)

router = routers.SimpleRouter()

router.register(r"retailer/reports", RetailerReportViewSet, basename="reports-retailer")
router.register(r"internal/reports", InternalReportViewSet, basename="reports-internal")

urlpatterns = [
    url(
        r"ledger-api-retailer-invoice-success-callback/(?P<id>.+)/(?P<uuid>.+)$",
        PayInvoiceSuccessCallbackView.as_view(),
        name="ledger-api-retailer-invoice-success-callback",
    ),
]

urlpatterns += router.urls
