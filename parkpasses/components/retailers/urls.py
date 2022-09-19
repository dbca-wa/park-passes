from django.conf.urls import url

from parkpasses.components.retailers.api import RetailerGroupsForUser

urlpatterns = [
    url(r"retailer-groups-for-user", RetailerGroupsForUser.as_view()),
]
