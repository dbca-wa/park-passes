from django.conf.urls import url
from rest_framework import routers

from parkpasses.components.help.api import FAQViewSet, HelpDetailView, HelpTextViewSet

router = routers.SimpleRouter()

router.register(r"help-text", HelpTextViewSet, basename="help-text")
router.register(r"faqs", FAQViewSet, basename="faqs")

urlpatterns = [
    url(r"help-detail/(?P<label>.+)/", HelpDetailView.as_view(), name="help-detail"),
]

urlpatterns = router.urls + urlpatterns
