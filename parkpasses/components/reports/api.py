import logging

from rest_framework import viewsets

from parkpasses.components.reports.models import Report
from parkpasses.components.reports.serializers import (
    InternalReportSerializer,
    RetailerReportSerializer,
)
from parkpasses.helpers import get_retailer_group_ids_for_user
from parkpasses.permissions import IsInternal, IsRetailer

logger = logging.getLogger(__name__)


class RetailerReportViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for retailers to perform actions on reports.
    """

    model = Report
    permission_classes = [IsRetailer]
    serializer_class = RetailerReportSerializer

    def get_queryset(self):
        user_retailer_groups = get_retailer_group_ids_for_user(self.request)
        if 0 < len(user_retailer_groups):
            return Report.objects.filter(retailer_group__in=user_retailer_groups)
        return Report.objects.none()


class InternalReportViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for internal users to perform actions on reports.
    """

    model = Report
    queryset = Report.objects.all()
    permission_classes = [IsInternal]
    serializer_class = InternalReportSerializer
