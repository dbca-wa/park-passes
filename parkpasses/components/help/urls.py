from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.help.api import HelpTextViewSet
from parkpasses.components.help.views import ParkPassesHelpView

router = routers.SimpleRouter()

router.register(r"help-text", HelpTextViewSet, basename="help-text")

urlpatterns = [url(r"", ParkPassesHelpView.as_view(), name="help")]

urlpatterns += router.urls
