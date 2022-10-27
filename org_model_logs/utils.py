import logging
from abc import ABC, abstractmethod

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from rest_framework.viewsets import ModelViewSet

from org_model_logs.models import UserAction

logger = logging.getLogger(__name__)


class BaseUserActionViewSet(ModelViewSet, ABC):
    def log_user_action(self, object_id, action, why=None):
        model = self.model
        content_type = ContentType.objects.get_for_model(model)
        user_action = UserAction.objects.log_action(
            object_id=object_id,
            content_type=content_type,
            who=self.request.user.id,
            what=action.format(model._meta.model.__name__, object_id),
            why=why,
        )
        return user_action

    @abstractmethod
    def get_user_action_serializer_class(self):
        raise NotImplementedError(
            "Subclasses must implement a get_user_action_serializer method."
        )

    def create(self, request, *args, **kwargs):
        why = self.request.data.get("why", None)
        response = super().create(request, *args, **kwargs)
        instance = response.data
        user_action = self.log_user_action(
            instance["id"], settings.ACTION_CREATE, why=why
        )
        serializer = self.get_user_action_serializer_class()
        response.data["user_action"] = serializer(user_action).data
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        instance = response.data
        self.log_user_action(instance["id"], settings.ACTION_VIEW)
        return response

    def update(self, request, *args, **kwargs):
        why = self.request.data.get("why", None)
        response = super().update(request, *args, **kwargs)
        instance = response.data
        user_action = self.log_user_action(
            instance["id"], settings.ACTION_UPDATE, why=why
        )
        serializer = self.get_user_action_serializer_class()
        response.data["user_action"] = serializer(user_action).data
        return response

    def partial_update(self, request, *args, **kwargs):
        why = self.request.data.get("why", None)
        response = super().partial_update(request, *args, **kwargs)
        instance = response.data
        user_action = self.log_user_action(
            instance["id"], settings.ACTION_PARTIAL_UPDATE, why=why
        )
        serializer = self.get_user_action_serializer_class()
        response.data["user_action"] = serializer(user_action).data
        return response

    def destroy(self, request, *args, **kwargs):
        why = self.request.data.get("why", None)
        response = super().destroy(request, *args, **kwargs)
        instance = response.data
        user_action = self.log_user_action(
            instance["id"], settings.ACTION_DESTROY, why=why
        )
        serializer = self.get_user_action_serializer_class()
        response.data["user_action"] = serializer(user_action).data
        return response
