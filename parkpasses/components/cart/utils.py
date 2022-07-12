import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from parkpasses.components.passes.models import Pass
from parkpasses.components.passes.serializers import ExternalPassSerializer
from parkpasses.components.vouchers.models import Voucher
from parkpasses.components.vouchers.serializers import ExternalListVoucherSerializer

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
    def get_checkout_parameters(
        self, request, cart, checkouthash, internal=False, invoice_text=None
    ):
        return {
            "system": settings.PARKPASSES_PAYMENT_SYSTEM_ID,
            "fallback_url": request.build_absolute_uri("/"),
            "return_url": request.build_absolute_uri(reverse("cart_success"))
            + "?checkouthash="
            + checkouthash,
            "return_preload_url": settings.PARKSTAY_EXTERNAL_URL
            + "/api/cart/success/"
            + cart.uuid
            + "/"
            + str(cart.id)
            + "/",
            "force_redirect": True,
            "proxy": True if internal else False,
            "invoice_text": invoice_text,
            "session_type": "ledger_api",
            "basket_owner": cart.user.id,
        }

    @classmethod
    def get_basket_parameters(self, lines, vouchers=[]):
        return {
            "products": lines,
            "vouchers": lines,
            "system": settings.PARKPASSES_PAYMENT_SYSTEM_ID,
            "custom_basket": True,
            "products": lines,
            "products": lines,
            "products": lines,
        }
        return

    @classmethod
    def get_oracle_code(self):
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
    def checkout(request):
        # Ipliment checkout function
        # https://github.com/dbca-wa/parkstay_bs/blob/881019cc4df996ebeca3629d45cccbcb91704205/parkstay/utils.py#L1676
        pass
