from django.views.generic.base import TemplateView


class ExternalOrdersView(TemplateView):
    template_name = "parkpasses/your-orders.html"
