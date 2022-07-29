from django.views.generic.base import TemplateView


class InternalVouchersView(TemplateView):
    template_name = "parkpasses/index.html"
