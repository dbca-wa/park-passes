from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

from parkpasses.forms import LoginForm
from parkpasses.helpers import is_internal


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
