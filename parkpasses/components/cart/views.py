from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView

from parkpasses.components.cart.models import Cart, CartItem
from parkpasses.forms import LoginForm
from parkpasses.helpers import is_internal


class CheckoutView(LoginRequiredMixin, ListView):
    template_name = "parkpasses/checkout.html"
    model = CartItem

    def get_queryset(self):
        if self.request.session.get("cart_id", None):
            cart = Cart.objects.get(id=self.request.session["cart_id"])
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
