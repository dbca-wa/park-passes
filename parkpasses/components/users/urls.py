from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.users.api import UserDataView, UserViewSet

router = routers.SimpleRouter()

router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    url(r"user-data", UserDataView.as_view()),
]

urlpatterns += router.urls
