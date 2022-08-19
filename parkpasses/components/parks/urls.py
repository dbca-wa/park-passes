from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.parks.api import (
    LGAViewSet,
    ParkGroupsForPostcodeView,
    ParkViewSet,
    PostcodeViewSet,
    ValidatePostcodeView,
)

router = routers.SimpleRouter()
router.register(r"postcodes", PostcodeViewSet, basename="postcodes")
router.register(r"parks", ParkViewSet, basename="parks")
router.register(r"lgas", LGAViewSet, basename="lgas")

urlpatterns = [
    url(r"validate-postcode", ValidatePostcodeView.as_view()),
    url(r"park-groups-for-postcode", ParkGroupsForPostcodeView.as_view()),
]

urlpatterns += router.urls
