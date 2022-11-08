import logging

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, mixins, viewsets

from parkpasses.components.help.models import FAQ, HelpText
from parkpasses.components.help.serializers import (
    FAQSerializer,
    HelpTextSerializer,
    InternalHelpTextSerializer,
)
from parkpasses.helpers import is_internal
from parkpasses.permissions import IsInternalOrReadOnly

logger = logging.getLogger(__name__)


class HelpDetailView(generics.RetrieveAPIView):
    lookup_field = "label"
    queryset = HelpText.objects.all()
    serializer_class = HelpTextSerializer

    @method_decorator(cache_page(settings.CACHE_TIMEOUT_2_HOURS))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class HelpTextViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing actions on help text.
    """

    model = HelpText
    queryset = HelpText.objects.all()
    permission_classes = [IsInternalOrReadOnly]

    def get_serializer_class(self):
        if is_internal(self.request):
            return InternalHelpTextSerializer
        else:
            return HelpTextSerializer

    @method_decorator(cache_page(settings.CACHE_TIMEOUT_2_HOURS))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FAQViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    model = FAQ
    queryset = FAQ.objects.all().order_by("display_order")
    serializer_class = FAQSerializer
    permission_classes = [IsInternalOrReadOnly]

    @method_decorator(cache_page(settings.CACHE_TIMEOUT_2_HOURS))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
