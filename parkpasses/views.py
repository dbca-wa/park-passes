import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.management import call_command
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.base import TemplateView

from parkpasses.forms import LoginForm
from parkpasses.helpers import is_internal, is_retailer, is_retailer_admin

logger = logging.getLogger(__name__)


class InternalView(UserPassesTestMixin, TemplateView):
    template_name = "parkpasses/internal/index.html"

    def test_func(self):
        return is_internal(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dev"] = settings.DEV_STATIC
        context["dev_url"] = settings.DEV_STATIC_URL
        if hasattr(settings, "DEV_APP_BUILD_URL") and settings.DEV_APP_BUILD_URL:
            context["app_build_url"] = settings.DEV_APP_BUILD_URL
        return context


class RetailerView(UserPassesTestMixin, TemplateView):
    template_name = "parkpasses/retailer/index.html"

    def test_func(self):
        return is_retailer(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dev"] = settings.DEV_STATIC
        context["dev_url"] = settings.DEV_STATIC_URL
        if hasattr(settings, "DEV_APP_BUILD_URL") and settings.DEV_APP_BUILD_URL:
            context["app_build_url"] = settings.DEV_APP_BUILD_URL
        return context


class RetailerSellAPassView(UserPassesTestMixin, TemplateView):
    template_name = "parkpasses/retailer/index.html"

    def test_func(self):
        return is_retailer(self.request)

    def get(self, *args, **kwargs):
        cart_item_count = self.request.session.get("cart_item_count", None)
        logger.debug("cart_item_count = " + str(cart_item_count))

        if cart_item_count and cart_item_count > 0:
            logger.debug("Redirecting")
            return redirect(reverse("user-cart"))

        return super().get(*args, **kwargs)


class RetailerAdminView(UserPassesTestMixin, TemplateView):
    template_name = "parkpasses/retailer/index.html"

    def test_func(self):
        return is_retailer_admin(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dev"] = settings.DEV_STATIC
        context["dev_url"] = settings.DEV_STATIC_URL
        if hasattr(settings, "DEV_APP_BUILD_URL") and settings.DEV_APP_BUILD_URL:
            context["app_build_url"] = settings.DEV_APP_BUILD_URL
        return context


class ExternalView(LoginRequiredMixin, TemplateView):
    template_name = "parkpasses/dash/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dev"] = settings.DEV_STATIC
        context["dev_url"] = settings.DEV_STATIC_URL
        if hasattr(settings, "DEV_APP_BUILD_URL") and settings.DEV_APP_BUILD_URL:
            context["app_build_url"] = settings.DEV_APP_BUILD_URL
        return context


class ParkPassesRoutingView(TemplateView):
    template_name = "parkpasses/index.html"

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            if is_internal(self.request):
                return redirect("internal")
            if is_retailer(self.request):
                return redirect("retailer-home")
        kwargs["form"] = LoginForm
        return super().get(*args, **kwargs)


class ParkPassesPurchaseVoucherView(TemplateView):
    template_name = "parkpasses/index.html"


class ParkPassesPurchasePassView(TemplateView):
    template_name = "parkpasses/index.html"


class ParkPassesContactView(TemplateView):
    template_name = "parkpasses/contact.html"


class ParkPassesFurtherInformationView(TemplateView):
    template_name = "parkpasses/further_info.html"


class ManagementCommandsView(LoginRequiredMixin, TemplateView):
    template_name = "parkpasses/mgt-commands.html"

    def post(self, request):
        data = {}
        command_script = request.POST.get("script", None)
        if command_script:
            print(f"running {command_script}")
            call_command(command_script)
            data.update({command_script: "true"})

        return render(request, self.template_name, data)
