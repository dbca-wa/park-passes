import logging

from django.contrib.contenttypes.models import ContentType
from rest_framework import generics, viewsets
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from org_model_logs.models import UserAction
from org_model_logs.serializers import UserActionSerializer

logger = logging.getLogger(__name__)


class UserActionList(generics.ListAPIView):
    search_fields = ["what", "why"]
    model = UserAction
    serializer_class = UserActionSerializer
    pagination_class = DatatablesPageNumberPagination
    filter_backends = (DatatablesFilterBackend,)
    ordering = ("-when",)

    def get_queryset(self):
        app_label = self.request.query_params.get("app_label", None)
        model = self.request.query_params.get("model", None)
        object_id = self.request.query_params.get("object_id", None)
        if app_label and model and object_id:
            if ContentType.objects.filter(app_label=app_label, model=model).exists():
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                logger.debug("content_type = " + str(content_type))
                if UserAction.objects.filter(
                    content_type=content_type, object_id=object_id
                ).exists():
                    return UserAction.objects.filter(
                        content_type=content_type, object_id=object_id
                    )
                UserAction.objects.none()
        if app_label and model:
            if ContentType.objects.filter(app_label=app_label, model=model).exists():
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                return UserAction.objects.filter(content_type=content_type)
        if app_label:
            if ContentType.objects.filter(app_label=app_label, model=model).exists():
                content_types = ContentType.objects.filter(app_label=app_label)
                return UserAction.objects.filter(content_type__in=content_types)
        return UserAction.objects.all()

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class UserActionViewSet(viewsets.ModelViewSet):
    model = UserAction
    serializer_class = UserActionSerializer
