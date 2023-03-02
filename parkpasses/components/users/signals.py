import logging

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.contrib.contenttypes.models import ContentType

from parkpasses.components.cart.models import Cart
from parkpasses.components.cart.utils import CartUtils
from parkpasses.components.passes.models import Pass
from parkpasses.components.retailers.models import RetailerGroupUser
from parkpasses.components.users.models import UserSession
from parkpasses.components.vouchers.models import Voucher
from parkpasses.helpers import is_retailer

logger = logging.getLogger(__name__)


def init_cart(sender, user, request, **kwargs):
    """Since items can be added to a cart anonymously
    we need to attach the correct user to those items once they log in"""
    logger.info("user_logged_in signal running init_cart function")
    cart = Cart.get_or_create_cart(request)
    cart.set_user_for_cart_and_items(user.id)


def add_retailer_to_session(sender, user, request, **kwargs):
    logger.info("user_logged_in signal running add_retailer_to_session function")
    cart = Cart.get_or_create_cart(request)
    if is_retailer(request):
        retailer_group_user = (
            RetailerGroupUser.objects.filter(emailuser=user.id)
            .order_by("-datetime_created")
            .first()
        )
        request.session["retailer"] = {
            "id": retailer_group_user.retailer_group.id,
            "name": retailer_group_user.retailer_group.organisation[
                "organisation_name"
            ],
        }
        # If the retailer has any park passes in their cart that have sold_via=
        # Department of Biodiversity, Conservation and Attractions then delete them
        # as once they are logged in as a retailer they should only be able checkout
        # with park passes that have sold_via = <their retailer group>.
        pass_content_type = ContentType.objects.get_for_model(Pass)
        voucher_content_type = ContentType.objects.get_for_model(Voucher)
        for item in cart.items.all():
            if item.content_type == voucher_content_type:
                item.delete()
            if item.content_type == pass_content_type:
                park_pass = Pass.objects.get(id=item.object_id)
                if (
                    settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID
                    == park_pass.sold_via.ledger_organisation
                ):
                    item.delete()
        cart.save()
        CartUtils.set_cart_item_count(request, cart.items.all().count())

    else:
        if "retailer" in request.session.keys():
            del request.session["retailer"]


def assign_orphan_passes(sender, user, request, **kwargs):
    """When passes are sold via retailers, the user doesn't necessarily have an account in ledger
    so we need a way to attach the user to those passes when they log in"""
    logger.info("user_logged_in signal running assign_orphan_passes function")
    queryset = Pass.objects.filter(user__isnull=True, email=user.email)
    if queryset.exists():
        for park_pass in queryset:
            park_pass.user = user.id
            park_pass.save()


def track_user_session(sender, user, request, **kwargs):
    UserSession.objects.get_or_create(
        user=user.id, session_id=request.session.session_key
    )


user_logged_in.connect(init_cart)
user_logged_in.connect(assign_orphan_passes)
user_logged_in.connect(add_retailer_to_session)
user_logged_in.connect(track_user_session)
