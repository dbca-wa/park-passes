import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.management import call_command
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

from parkpasses.forms import LoginForm
from parkpasses.helpers import is_internal

logger = logging.getLogger("payment_checkout")


class InternalView(UserPassesTestMixin, TemplateView):
    template_name = "parkpasses/dash/index.html"

    def test_func(self):
        return is_internal(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dev"] = settings.DEV_STATIC
        context["dev_url"] = settings.DEV_STATIC_URL
        if hasattr(settings, "DEV_APP_BUILD_URL") and settings.DEV_APP_BUILD_URL:
            context["app_build_url"] = settings.DEV_APP_BUILD_URL
        return context


class RetailerView(LoginRequiredMixin, TemplateView):
    template_name = "parkpasses/dash/index.html"

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
            # return redirect("/")
        kwargs["form"] = LoginForm
        return super().get(*args, **kwargs)


class ParkPassesContactView(TemplateView):
    template_name = "parkpasses/contact.html"


class ParkPassesFAQView(TemplateView):
    template_name = "parkpasses/faq.html"


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
