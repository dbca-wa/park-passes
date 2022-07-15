from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.users.api import UserDataView

router = routers.SimpleRouter()


urlpatterns = [
    url(r"user-data", UserDataView.as_view()),
]

urlpatterns += router.urls
