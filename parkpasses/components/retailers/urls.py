from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.retailers.api import (
    InternalRetailerGroupViewSet,
    RetailerGroupsForUser,
)

router = routers.SimpleRouter()
router.register(
    r"internal/retailer-groups",
    InternalRetailerGroupViewSet,
    basename="retailer-groups-internal",
)

urlpatterns = [
    url(r"retailer-groups-for-user", RetailerGroupsForUser.as_view()),
]

urlpatterns += router.urls
