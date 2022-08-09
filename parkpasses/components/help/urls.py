from rest_framework import routers

from parkpasses.components.help.api import FAQViewSet, HelpTextViewSet

router = routers.SimpleRouter()

router.register(r"help-text", HelpTextViewSet, basename="help-text")
router.register(r"faqs", FAQViewSet, basename="faqs")

urlpatterns = router.urls
