from django.conf.urls import url
from rest_framework import routers

from org_model_logs.api import UserActionList

router = routers.SimpleRouter()

urlpatterns = [
    url(r"user-actions", UserActionList.as_view()),
]
