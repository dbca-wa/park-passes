from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.main.api import (
    DocumentCreateView,
    DocumentViewSet,
    EntryTypeList,
    ListCreateCommunicationsLogEntry,
    ParkPassesSystemCheck,
    UserActionList,
)

router = routers.SimpleRouter()
router.register(
    r"internal/org-model-documents",
    DocumentViewSet,
    basename="org-model-documents-internal",
)
urlpatterns = [
    url(r"internal/park-passes-system-check/$", ParkPassesSystemCheck.as_view()),
    # ========================================================================== Org Model Logs
    url(
        r"org-model-logs/user-actions",
        UserActionList.as_view(),
        name="user-actions",
    ),
    url(
        r"org-model-logs/entry-types",
        EntryTypeList.as_view(),
        name="entry-types",
    ),
    url(
        r"internal/org-model-logs/communications-log-entries",
        ListCreateCommunicationsLogEntry.as_view(),
        name="list-create-communications-log-entries",
    ),
    # ========================================================================== Org Model Documents
    url(
        r"internal/org-model-documents/upload-documents",
        DocumentCreateView.as_view(),
        name="upload-documents",
    ),
]

urlpatterns += router.urls
