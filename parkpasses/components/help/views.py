from django.views.generic.base import TemplateView


class ParkPassesHelpView(TemplateView):
    template_name = "parkpasses/help.html"
