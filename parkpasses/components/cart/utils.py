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
    def get_ledger_order_lines(self, request, cart):
        ledger_order_lines = []
        logger.info(
            f"Settings line_status to default from settings: {settings.PARKPASSES_LEDGER_DEFAULT_LINE_STATUS}.",
            extra={"className": self.__class__.__name__},
        )
        line_status = settings.PARKPASSES_LEDGER_DEFAULT_LINE_STATUS

        order, order_items = cart.create_order()
        for order_item in order_items:
            if settings.DEBUG:
                order_item.amount = int(order_item.amount)
                order_item.description += " (Price rounded for dev env)"

            ledger_order_line = {
                "ledger_description": order_item.description,
                "quantity": 1,
                "price_incl_tax": str(order_item.amount),
                "oracle_code": CartUtils.get_oracle_code(
                    request, order_item.content_type, order_item.object_id
                ),
                "line_status": line_status,
            }
            logger.info(
                f"Ledger order line: {ledger_order_line} created.",
                extra={"className": self.__class__.__name__},
            )
            ledger_order_lines.append(ledger_order_line)
            logger.info(
                f"Appended ledger order line: {ledger_order_line} to ledger order lines list.",
                extra={"className": self.__class__.__name__},
            )
        return ledger_order_lines

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
        logger.info(
            f"Calling get_oracle_code with content_type: {content_type} and object_id: {object_id}",
            extra={"className": self.__class__.__name__},
        )
        # Check if the request user belongs to retailer group and if so assign their oracle code
        if is_retailer(request):
            logger.info(
                f"User: {request.user.id} ({request.user}) is a retailer.",
                extra={"className": self.__class__.__name__},
            )
            user = request.user
            retailer_group_user = (
                RetailerGroupUser.objects.filter(emailuser=user)
                .order_by("-datetime_created")
                .first()
            )
            if retailer_group_user:
                logger.info(
                    f"Retailer Group User: {retailer_group_user} exists.",
                    extra={"className": self.__class__.__name__},
                )
                retailer_group = retailer_group_user.retailer_group
                if retailer_group.oracle_code:
                    logger.info(
                        f"Returning Retailer Group oracle code: {retailer_group.oracle_code}.",
                        extra={"className": self.__class__.__name__},
                    )
                    return retailer_group.oracle_code
                logger.info(
                    f"No oracle code found for Retailer Group: {retailer_group}.",
                    extra={"className": self.__class__.__name__},
                )

        # If not, assign the oracle code for the pass type
        pass_content_type = ContentType.objects.get(
            app_label="parkpasses", model="pass"
        )
        if pass_content_type == content_type:
            logger.info(
                f"Content type is : {pass_content_type}.",
                extra={"className": self.__class__.__name__},
            )
            if Pass.objects.filter(id=object_id).exists():
                logger.info(
                    f"Park pass with object_id: {object_id} exists.",
                    extra={"className": self.__class__.__name__},
                )
                park_pass = Pass.objects.get(id=object_id)
                pass_type = park_pass.option.pricing_window.pass_type
                if pass_type.oracle_code:
                    logger.info(
                        f"Returning Pass Type: {pass_type} oracle code: {pass_type.oracle_code}.",
                        extra={"className": self.__class__.__name__},
                    )
                    return pass_type.oracle_code

        logger.info(
            f"No retailer group or pass type oracle code found, returning default oracle code from settings:\
                 {settings.PARKPASSES_DEFAULT_ORACLE_CODE} .",
            extra={"className": self.__class__.__name__},
        )
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
            cart_item_count = cart_item_count + 1
        else:
            cart_item_count = 1
        request.session["cart_item_count"] = cart_item_count
        return cart_item_count

    @classmethod
    def decrement_cart_item_count(self, request):
        cart_item_count = request.session.get("cart_item_count", None)
        if cart_item_count and 0 < cart_item_count:
            cart_item_count = cart_item_count - 1
        else:
            cart_item_count = 0
        request.session["cart_item_count"] = cart_item_count
        return cart_item_count

    @classmethod
    def reset_cart_item_count(self, request):
        logger.info(
            "Resetting cart_item_count session variable to 0.",
            extra={"className": self.__class__.__name__},
        )
        request.session["cart_item_count"] = 0

    @classmethod
    def remove_cart_id_from_session(self, request):
        logger.info(
            "Removing cart_id variable from session.",
            extra={"className": self.__class__.__name__},
        )
        del request.session["cart_id"]
