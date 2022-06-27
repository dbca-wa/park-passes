from rest_framework import routers

from parkpasses.components.parks.api import LGAViewSet, ParkViewSet, PostcodeViewSet

router = routers.SimpleRouter()
router.register(r"postcodes", PostcodeViewSet, basename="postcodes")
router.register(r"parks", ParkViewSet, basename="parks")
router.register(r"lgas", LGAViewSet, basename="lgas")

urlpatterns = router.urls
