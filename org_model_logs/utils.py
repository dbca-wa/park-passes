import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from rest_framework.viewsets import ModelViewSet

from org_model_logs.models import UserAction

logger = logging.getLogger(__name__)


class UserActionViewSet(ModelViewSet):
    def log_user_action(self, object_id, action):
        model = self.model
        content_type = ContentType.objects.get_for_model(model)
        user_action = UserAction(
            object_id=object_id,
            content_type=content_type,
            who=self.request.user.id,
            what=action.format(model._meta.model.__name__, object_id),
        )
        user_action.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        instance = response.data
        self.log_user_action(instance["id"], settings.ACTION_CREATE)
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        instance = response.data
        self.log_user_action(instance["id"], settings.ACTION_VIEW)
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        instance = response.data
        self.log_user_action(instance["id"], settings.ACTION_UPDATE)
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        instance = response.data
        self.log_user_action(instance["id"], settings.ACTION_PARTIAL_UPDATE)
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        instance = response.data
        self.log_user_action(instance["id"], settings.ACTION_DESTROY)
        return response
