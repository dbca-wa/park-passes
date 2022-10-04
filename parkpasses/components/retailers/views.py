from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.base import TemplateView

from parkpasses.components.retailers.models import RetailerGroupInvite


class RespondToRetailUserInviteView(
    LoginRequiredMixin, UserPassesTestMixin, TemplateView
):
    template_name = "parkpasses/repond-to-retailer-invite.html"

    def test_func(self):
        if self.request.user.is_authenticated:
            uuid = self.kwargs["uuid"]
            email = self.request.user.email
            if RetailerGroupInvite.objects.filter(uuid=uuid, email=email).exists():
                return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dev"] = settings.DEV_STATIC
        context["dev_url"] = settings.DEV_STATIC_URL
        if hasattr(settings, "DEV_APP_BUILD_URL") and settings.DEV_APP_BUILD_URL:
            context["app_build_url"] = settings.DEV_APP_BUILD_URL
        return context
