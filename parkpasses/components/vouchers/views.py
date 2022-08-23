from django.views.generic.base import TemplateView


class ExternalVouchersView(TemplateView):
    template_name = "parkpasses/your-vouchers.html"


class InternalVouchersView(TemplateView):
    template_name = "parkpasses/index.html"
