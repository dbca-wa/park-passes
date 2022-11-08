from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView


class ExternalOrdersView(LoginRequiredMixin, TemplateView):
    template_name = "parkpasses/your-orders.html"
