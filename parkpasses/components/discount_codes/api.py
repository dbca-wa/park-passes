import logging

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from parkpasses.components.discount_codes.models import DiscountCode
from parkpasses.components.discount_codes.serializers import (
    InternalDiscountCodeSerializer,
)

logger = logging.getLogger(__name__)


class DiscountCodeViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on discount codes.
    """

    model = DiscountCode
    queryset = DiscountCode.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = InternalDiscountCodeSerializer
