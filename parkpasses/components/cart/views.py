from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView
from django.views.generic.base import TemplateView

from parkpasses.components.cart.models import Cart, CartItem
from parkpasses.forms import LoginForm
from parkpasses.helpers import is_internal


class CartView(LoginRequiredMixin, ListView):
    template_name = "parkpasses/cart.html"
    model = CartItem

    def get_queryset(self):
        cart_id = self.request.session.get("cart_id", None)
        if cart_id and Cart.objects.filter(id=cart_id).exists():
            cart = Cart.objects.get(id=cart_id)
            cart.set_user_for_cart_and_items(self.request.user.id)
            return CartItem.objects.filter(cart=cart)
        else:
            return CartItem.objects.none()

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
