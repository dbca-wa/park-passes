from django.contrib.auth.signals import user_logged_in

from parkpasses.components.cart.models import Cart


def init_cart(sender, user, request, **kwargs):
    cart = Cart.get_or_create_cart(request)
    # Since items can be added to a cart anonymously
    # we need to attach the correct user to those items once they log in
    cart.set_user_for_cart_and_items(request.user.id)


user_logged_in.connect(init_cart)
