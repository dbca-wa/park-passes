from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.retailers.api import (
    ExternalRetailerGroupInviteViewSet,
    InternalDistrictViewSet,
    InternalRetailerGroupInviteViewSet,
    InternalRetailerGroupUserViewSet,
    InternalRetailerGroupViewSet,
    RetailerGroupsForUser,
    RetailerRetailerGroupInviteViewSet,
    RetailerRetailerGroupUserViewSet,
)

router = routers.SimpleRouter()
router.register(
    r"internal/retailer-groups",
    InternalRetailerGroupViewSet,
    basename="retailer-groups-internal",
)
router.register(
    r"internal/retailer-group-users",
    InternalRetailerGroupUserViewSet,
    basename="retailer-group-users-internal",
)
router.register(
    r"retailer/retailer-group-users",
    RetailerRetailerGroupUserViewSet,
    basename="retailer-group-users-retailer",
)
router.register(
    r"internal/retailer-group-invites",
    InternalRetailerGroupInviteViewSet,
    basename="retailer-group-invites-internal",
)
router.register(
    r"retailer/retailer-group-invites",
    RetailerRetailerGroupInviteViewSet,
    basename="retailer-group-invites-retailer",
)
router.register(
    r"external/retailer-group-invites",
    ExternalRetailerGroupInviteViewSet,
    basename="retailer-group-invites-external",
)
router.register(
    r"internal/districts",
    InternalDistrictViewSet,
    basename="internal-districts",
)

urlpatterns = [
    url(r"retailer-groups-for-user", RetailerGroupsForUser.as_view()),
    url(r"retailer-invite-reponse", RetailerGroupsForUser.as_view()),
]

urlpatterns += router.urls
