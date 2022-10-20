import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from parkpasses.components.passes.models import Pass
from parkpasses.components.passes.serializers import ExternalPassSerializer
from parkpasses.components.retailers.models import RetailerGroupUser
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
    def get_basket_parameters(
        self,
        lines,
        booking_reference,
        booking_reference_link=None,
        vouchers=[],
        is_no_payment=False,
    ):
        return {
            "products": lines,
            "vouchers": [],
            "system": settings.PARKPASSES_PAYMENT_SYSTEM_PREFIX,
            "custom_basket": True,
            "no_payment": is_no_payment,
            "booking_reference": booking_reference,
            # Optional: Used to keep a link between bookings that are related such as autorenewal
            "booking_reference_link": booking_reference_link,
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
    def get_checkout_parameters(
        self,
        request,
        return_url,
        return_preload_url,
        user,
        invoice_text,
        internal=False,
    ):
        return {
            "system": settings.PARKPASSES_PAYMENT_SYSTEM_ID,
            "fallback_url": request.build_absolute_uri("/"),
            "return_url": return_url,
            "return_preload_url": return_preload_url,
            "force_redirect": True,
            "proxy": True if internal else False,
            "invoice_text": invoice_text,
            "session_type": "ledger_api",
            "basket_owner": user,
        }

    @classmethod
    def get_oracle_code(self, request, content_type, object_id):
        # Check if the request user belongs to retailer group and if so assign their oracle code
        if is_retailer(request):
            user = request.user
            retailer_group_user = RetailerGroupUser.objects.filter(
                emailuser=user
            ).first()
            if retailer_group_user:
                retailer_group = retailer_group_user.retailer_group
                if retailer_group.oracle_code:
                    return retailer_group.oracle_code
        # If not, assign the oracle code for the pass type
        pass_content_type = ContentType.objects.get(
            app_label="parkpasses", model="pass"
        )
        if pass_content_type == content_type:
            if Pass.objects.filter(id=object_id).exists():
                park_pass = Pass.objects.get(id=object_id)
                pass_type = park_pass.option.pricing_window.pass_type
                if pass_type.oracle_code:
                    return pass_type.oracle_code

        # If not then just fall back to the default code from settings.
        return settings.PARKPASSES_DEFAULT_ORACLE_CODE

    @classmethod
    def get_voucher_purchase_description(self, voucher_number):
        return f"{settings.PARKPASSES_VOUCHER_PURCHASE_DESCRIPTION} {voucher_number}"

    @classmethod
    def get_pass_purchase_description(self, pass_number):
        return f"{settings.PARKPASSES_PASS_PURCHASE_DESCRIPTION} {pass_number}"

    @classmethod
    def get_concession_description(self, concession_type):
        return f"{settings.PARKPASSES_CONCESSION_APPLIED_DESCRIPTION} {concession_type}"

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
            return cart_item_count + 1

        request.session["cart_item_count"] = 1
        return 1

    @classmethod
    def decrement_cart_item_count(self, request):
        cart_item_count = request.session.get("cart_item_count", None)
        if cart_item_count:
            request.session["cart_item_count"] = cart_item_count - 1
            return cart_item_count - 1

        request.session["cart_item_count"] = 0
        return 0

    @classmethod
    def reset_cart_item_count(self, request):
        request.session["cart_item_count"] = 0

    @classmethod
    def remove_cart_id_from_session(self, request):
        del request.session["cart_id"]
