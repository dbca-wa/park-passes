from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.main.api import (
    DocumentCreateView,
    DocumentViewSet,
    EntryTypeList,
    ListCreateCommunicationsLogEntry,
    UserActionList,
)

router = routers.SimpleRouter()
router.register(
    r"internal/org-model-documents",
    DocumentViewSet,
    basename="org-model-documents-internal",
)
urlpatterns = [
    url(
        r"api/main/org-model-logs/user-actions",
        UserActionList.as_view(),
        name="user-actions",
    ),
    url(
        r"api/main/internal/org-model-documents/upload-documents",
        DocumentCreateView.as_view(),
        name="upload-documents",
    ),
    # ========================================================================== Org Model Logs
    url(
        r"api/main/org-model-logs/entry-types",
        EntryTypeList.as_view(),
        name="entry-types",
    ),
    url(
        r"api/main/internal/org-model-logs/communications-log-entries",
        ListCreateCommunicationsLogEntry.as_view(),
        name="list-create-communications-log-entries",
    ),
]

urlpatterns += router.urls
