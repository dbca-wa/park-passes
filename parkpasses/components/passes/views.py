from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView


class ExternalPassView(LoginRequiredMixin, TemplateView):
    template_name = "parkpasses/your-park-passes.html"


class InternalPricingWindowsView(TemplateView):
    template_name = "parkpasses/index.html"
