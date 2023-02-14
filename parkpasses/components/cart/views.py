from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.base import RedirectView, TemplateView

from parkpasses.components.retailers.models import RetailerGroupInvite
from parkpasses.forms import LoginForm
from parkpasses.helpers import is_internal


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
        if self.request.session["cart_item_count"] > 0:
            return reverse("user-cart")

        # otherwise, redirect them to the home page.
        return super().get_redirect_url(*args, **kwargs)


class CartView(LoginRequiredMixin, TemplateView):
    template_name = "parkpasses/cart.html"

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            if is_internal(self.request):
                return redirect("internal")

        kwargs["form"] = LoginForm
        return super().get(*args, **kwargs)


class CheckoutSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "parkpasses/checkout-success.html"

    def get(self, *args, **kwargs):
        self.request.session["cart_item_count"] = 0
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            del self.request.session["cart_id"]
        if self.request.user.is_authenticated:
            if is_internal(self.request):
                return redirect("internal")
        kwargs["form"] = LoginForm
        return super().get(*args, **kwargs)
