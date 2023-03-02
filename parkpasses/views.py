import logging

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.management import call_command
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.base import RedirectView, TemplateView

from parkpasses.components.cart.utils import CartUtils
from parkpasses.components.retailers.models import RetailerGroupInvite
from parkpasses.forms import LoginForm
from parkpasses.helpers import is_internal, is_retailer, is_retailer_admin

logger = logging.getLogger(__name__)


class InternalView(UserPassesTestMixin, TemplateView):
    template_name = "parkpasses/internal/index.html"

    def test_func(self):
        return is_internal(self.request)


class LoginSuccessView(LoginRequiredMixin, RedirectView):
    """This view is called when the oauth2 login is successful."""

    permanent = False
    pattern_name = "home"

    def get_redirect_url(self, *args, **kwargs):
        # Check if the user has any retailer invites
        user_email = self.request.user.email
        invites = RetailerGroupInvite.objects.filter(
            email=user_email,
            status__in=[RetailerGroupInvite.SENT, RetailerGroupInvite.USER_LOGGED_IN],
        )
        if invites.exists():
            # If so, redirect them to the most recently sent invite page
            latest_invite = invites.last()
            return reverse("respond-to-invite", kwargs={"uuid": latest_invite.uuid})

        # If the user has any items in their cart, redirect them to the cart page
        cart_item_count = self.request.session["cart_item_count"]
        if cart_item_count > 0:
            logger.info(f"session['cart_item_count'] = {cart_item_count}")
            logger.info("Redirecting to cart page")
            return reverse("user-cart")

        # otherwise, redirect them to the home page.
        return super().get_redirect_url(*args, **kwargs)


class RetailerView(UserPassesTestMixin, TemplateView):
    template_name = "parkpasses/retailer/index.html"

    def test_func(self):
        return is_retailer(self.request)


class RetailerPassCreatedView(UserPassesTestMixin, TemplateView):
    template_name = "parkpasses/retailer/index.html"

    def test_func(self):
        return is_retailer(self.request)

    def get(self, *args, **kwargs):
        logger.info("Flushing the cart from the session")
        # Flush the cart from the session
        CartUtils.reset_cart_item_count(self.request)
        CartUtils.remove_cart_id_from_session(self.request)
        return super().get(*args, **kwargs)


class RetailerSellAPassView(UserPassesTestMixin, TemplateView):
    template_name = "parkpasses/retailer/index.html"

    def test_func(self):
        return is_retailer(self.request)

    def get(self, *args, **kwargs):
        # This stops retailers adding more than one item to the cart at a time
        cart_item_count = self.request.session.get("cart_item_count", None)

        if cart_item_count and cart_item_count > 0:
            return redirect(reverse("user-cart"))

        return super().get(*args, **kwargs)


class RetailerAdminView(UserPassesTestMixin, TemplateView):
    template_name = "parkpasses/retailer/index.html"

    def test_func(self):
        return is_retailer_admin(self.request)


class ExternalView(LoginRequiredMixin, TemplateView):
    template_name = "parkpasses/dash/index.html"


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
