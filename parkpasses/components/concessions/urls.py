from rest_framework import routers

from parkpasses.components.concessions.api import ConcessionViewSet

router = routers.SimpleRouter()

router.register(r"concessions", ConcessionViewSet, basename="concessions")

urlpatterns = router.urls
