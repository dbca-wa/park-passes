import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from parkpasses.components.passes.models import Pass
from parkpasses.components.passes.serializers import ExternalPassSerializer
from parkpasses.components.vouchers.models import Voucher
from parkpasses.components.vouchers.serializers import ExternalListVoucherSerializer
from parkpasses.helpers import is_retailer

logger = logging.getLogger(__name__)


class CartUtils:
    @classmethod
    def get_serialized_object_by_id_and_content_type(self, object_id, content_type_id):
        content_type = ContentType.objects.get(id=content_type_id)
        if "parkpasses | voucher" == str(content_type):
            voucher = Voucher.objects.get(id=object_id)
            return ExternalListVoucherSerializer(voucher).data
        if "parkpasses | pass" == str(content_type):
            park_pass = Pass.objects.get(id=object_id)
            return ExternalPassSerializer(park_pass).data

    @classmethod
    def get_basket_parameters(self, lines, vouchers=[], is_no_payment=False):
        logger.debug("vouchers = " + vouchers)
        return {
            "products": lines,
            "vouchers": [],
            "system": settings.PARKPASSES_PAYMENT_SYSTEM_PREFIX,
            "custom_basket": True,
            "no_payment": is_no_payment,
        }

    @classmethod
    def is_no_payment_checkout(self, request):
        user = request.user
        if user.is_authenticated and user.is_staff and is_retailer(request):
            no_payment = request.POST.get("no_payment", "false")
            if no_payment == "true":
                return True
        return False

    @classmethod
    def get_checkout_parameters(self, request, cart, invoice_text, internal=False):
        return {
            "system": settings.PARKPASSES_PAYMENT_SYSTEM_ID,
            "fallback_url": request.build_absolute_uri("/"),
            "return_url": request.build_absolute_uri(
                reverse("checkout-success", kwargs={"uuid": cart.uuid})
            ),
            "return_preload_url": request.build_absolute_uri(
                reverse("ledger-api-success-callback", kwargs={"uuid": cart.uuid})
            ),
            "force_redirect": True,
            "proxy": True if internal else False,
            "invoice_text": invoice_text,
            "session_type": "ledger_api",
            "basket_owner": cart.user,
        }

    @classmethod
    def get_oracle_code(self):
        # Check if the request user belongs to retailer group and if so assign their oracle code

        # If not, assign the oracle code for the pass type

        # If not then just fall back to the default code from settings.
        return settings.PARKPASSES_ORACLE_CODE

    @classmethod
    def get_voucher_purchase_description(self, voucher_number):
        return f"{settings.PARKPASSES_VOUCHER_PURCHASE_DESCRIPTION} {voucher_number}"

    @classmethod
    def get_pass_purchase_description(self, pass_number):
        return f"{settings.PARKPASSES_PASS_PURCHASE_DESCRIPTION} {pass_number}"

    @classmethod
    def get_concession_discount_description(self, user_information):
        concession_discount_description = (
            settings.PARKPASSES_CONCESSION_DESCRIPTION + " "
        )
        concession_discount_description += (
            user_information.concession.concession_type + " "
        )
        concession_discount_description += user_information.concession_card_number
        return concession_discount_description

    @classmethod
    def get_discount_code_description(self, code):
        return f"{settings.PARKPASSES_DISCOUNT_CODE_APPLIED_DESCRIPTION} {code}"

    @classmethod
    def get_voucher_code_description(self, code):
        return f"{settings.PARKPASSES_VOUCHER_CODE_REDEEMED_DESCRIPTION} {code}"

    @classmethod
    def increment_cart_item_count(self, request):
        cart_item_count = request.session.get("cart_item_count", None)
        if cart_item_count:
            request.session["cart_item_count"] = cart_item_count + 1
        else:
            request.session["cart_item_count"] = 1

    @classmethod
    def decrement_cart_item_count(self, request):
        cart_item_count = request.session.get("cart_item_count", None)
        if cart_item_count:
            request.session["cart_item_count"] = cart_item_count - 1
        else:
            request.session["cart_item_count"] = 0

    @classmethod
    def reset_cart_item_count(self, request):
        request.session["cart_item_count"] = 0

    @classmethod
    def remove_cart_id_from_session(self, request):
        del request.session["cart_id"]
