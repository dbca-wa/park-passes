from rest_framework import routers

from parkpasses.components.parks.api import PostcodeViewSet

router = routers.SimpleRouter()
router.register(r"postcodes", PostcodeViewSet, basename="postcodes")

urlpatterns = router.urls
