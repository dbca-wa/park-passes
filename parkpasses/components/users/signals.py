from django.contrib.auth.signals import user_logged_in

from parkpasses.components.cart.models import Cart
from parkpasses.components.passes.models import Pass


def init_cart(sender, user, request, **kwargs):
    """Since items can be added to a cart anonymously
    we need to attach the correct user to those items once they log in"""
    cart = Cart.get_or_create_cart(request)
    cart.set_user_for_cart_and_items(request.user.id)


def assign_orphan_passes(sender, user, request, **kwargs):
    """When passes are sold via retailers, the user doesn't necessarily have an account in ledger
    so we need a way to attach the user to those passes when they log in"""
    email_user = request.user
    queryset = Pass.objects.filter(user__isnull=True, email=email_user.email)
    if queryset.exists():
        for park_pass in queryset:
            park_pass.user = email_user.id
            park_pass.save()


user_logged_in.connect(init_cart)
user_logged_in.connect(assign_orphan_passes)
