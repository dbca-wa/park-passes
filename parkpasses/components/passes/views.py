from django.views.generic.base import TemplateView


class InternalPricingWindowsView(TemplateView):
    template_name = "parkpasses/index.html"
