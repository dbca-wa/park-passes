from rest_framework import routers

from parkpasses.components.main.api import DocumentViewSet

router = routers.SimpleRouter()
router.register(
    r"internal/org-model-documents",
    DocumentViewSet,
    basename="org-model-documents-internal",
)

urlpatterns = router.urls
