from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

from parkpasses.components.cart.models import Cart
from parkpasses.forms import LoginForm
from parkpasses.helpers import is_customer, is_internal


class CartView(LoginRequiredMixin, TemplateView):
    template_name = "parkpasses/cart.html"

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            if is_internal(self.request):
                return redirect("internal")
            if is_customer(self.request):
                cart = Cart.get_or_create_cart(self.request)
                if not cart.user:
                    cart.set_user_for_cart_and_items(self.request.user.id)
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
