from rest_framework import routers

from parkpasses.components.reports.api import (
    InternalReportViewSet,
    RetailerReportViewSet,
)

router = routers.SimpleRouter()

router.register(r"retailer/reports", RetailerReportViewSet, basename="reports-retailer")
router.register(r"internal/reports", InternalReportViewSet, basename="reports-internal")

urlpatterns = router.urls
