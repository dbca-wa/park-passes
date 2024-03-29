from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.views.generic.base import TemplateView

from parkpasses.components.retailers.models import RetailerGroupInvite


class RespondToRetailUserInviteView(
    LoginRequiredMixin, UserPassesTestMixin, TemplateView
):
    template_name = "parkpasses/repond-to-retailer-invite.html"

    def test_func(self):
        if self.request.user.is_authenticated:
            uuid = self.kwargs["uuid"]
            user = self.request.user
            if RetailerGroupInvite.objects.filter(
                uuid=uuid,
                email=user.email,
                status__in=[
                    RetailerGroupInvite.APPROVED,
                ],
            ).exists():
                raise Http404("Invite already approved.")

            if RetailerGroupInvite.objects.filter(
                uuid=uuid,
                email=user.email,
                status__in=[
                    RetailerGroupInvite.SENT,
                    RetailerGroupInvite.USER_LOGGED_IN,
                    RetailerGroupInvite.USER_ACCEPTED,
                ],
            ).exists():
                retailer_group_invite = RetailerGroupInvite.objects.get(
                    uuid=uuid,
                    email=user.email,
                    status__in=[
                        RetailerGroupInvite.SENT,
                        RetailerGroupInvite.USER_LOGGED_IN,
                        RetailerGroupInvite.USER_ACCEPTED,
                    ],
                )
                if retailer_group_invite.status == RetailerGroupInvite.SENT:
                    retailer_group_invite.user = user.id
                    retailer_group_invite.status = RetailerGroupInvite.USER_LOGGED_IN
                    retailer_group_invite.save()
                return True

        return False
