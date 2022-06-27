from rest_framework import routers

from parkpasses.components.help.api import HelpTextViewSet

router = routers.SimpleRouter()

router.register(r"help-text", HelpTextViewSet, basename="help-text")

urlpatterns = router.urls
