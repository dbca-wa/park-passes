import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from parkpasses.components.passes.exceptions import NoOracleCodeFoundForCartItem
from parkpasses.components.passes.models import DistrictPassTypeDurationOracleCode, Pass
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
            f"Settings line_status to default from settings: {settings.PARKPASSES_LEDGER_DEFAULT_LINE_STATUS}."
        )
        line_status = settings.PARKPASSES_LEDGER_DEFAULT_LINE_STATUS

        previous_item_oracle_code = None

        order, order_items = cart.create_order()
        for order_item in order_items:
            if settings.DEBUG:
                order_item.amount = int(order_item.amount)
                order_item.description += " (Price rounded for dev env)"

            oracle_code = CartUtils.get_oracle_code(
                request, order_item.content_type, order_item.object_id
            )
            if oracle_code:
                previous_item_oracle_code = oracle_code
            else:
                oracle_code = previous_item_oracle_code

            ledger_order_line = {
                "ledger_description": order_item.description,
                "quantity": 1,
                "price_excl_tax": str(order_item.amount),
                "price_incl_tax": str(order_item.amount),
                "oracle_code": oracle_code,
                "line_status": line_status,
            }
            logger.info(
                f"Ledger order line: {ledger_order_line} created.",
            )
            ledger_order_lines.append(ledger_order_line)
            logger.info(
                f"Appended ledger order line: {ledger_order_line} to ledger order lines list.",
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
            "tax_override": True,
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
        """
        There are two main ways that the system determines the oracle code to be used for a
        park pass purchase. The first is if the sale is via a retailer or not. If it is via a retailer
        then the system will use the oracle code based on the district that the retailer is in,
        the pass type and the duration of the pass.

        Note: Internal retailers have a district in the DistrictPassTypeDurationOracleCode model
        for PICA the district is null.

        If they are not a retailer then the sale must be online via the website, in this case,
        the system will use a PICA oracle code. If the pass type is a local park pass then the
        system will use the pica oracle code for the park group that the pass is for.
        """
        logger.info(
            f"Calling get_oracle_code with content_type: {content_type} and object_id: {object_id}"
        )

        # If the content type and object id are None then this item must be a concession, discount code or
        # voucher transaction. In this case we return None as the oracle code and the system will use the
        # oracle code from the previous item in the basket (i.e. the park pass).
        if content_type is None or object_id is None:
            return None

        # Check if the pass is being sold via a retailer
        if is_retailer(request):
            logger.info(
                "User is a retailer.",
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
                )
                retailer_group = retailer_group_user.retailer_group
                district = retailer_group.district
                # Retailers can only sell passes, not vouchers so we know the content type is a pass
                park_pass = Pass.objects.get(id=object_id)

                # oracle codes are only stored from the option in the default pricing window
                default_option = park_pass.option.get_default_option()
                oracle_codes = DistrictPassTypeDurationOracleCode.objects.filter(
                    district=district, option=default_option
                )
                if oracle_codes.exists():
                    district_pass_type_duration_oracle_code = oracle_codes.first()
                    if district_pass_type_duration_oracle_code.oracle_code:
                        logger.info(
                            f"Returning oracle code: {district_pass_type_duration_oracle_code}.",
                        )
                        return district_pass_type_duration_oracle_code.oracle_code

                logger.error(
                    f"No oracle code found: {district_pass_type_duration_oracle_code}.",
                )

        # If not, the pass or voucher is being sold online
        pass_content_type = ContentType.objects.get_for_model(Pass)
        if pass_content_type == content_type:
            logger.info(
                f"Content type is : {pass_content_type}.",
            )
            if Pass.objects.filter(id=object_id).exists():
                logger.info(
                    f"Park pass with object_id: {object_id} exists.",
                )
                park_pass = Pass.objects.get(id=object_id)
                pass_type = park_pass.option.pricing_window.pass_type
                if settings.ANNUAL_LOCAL_PASS == pass_type.name:
                    # PICA Oracle codes for local park passes are based on the park group
                    return park_pass.park_group.oracle_code

                # For other pass types, PICA oracle codes are based on the pass type
                # and duration
                # Note: PICA oracle codes have a null district

                # oracle codes are only stored from the option in the default pricing window
                default_option = park_pass.option.get_default_option()
                oracle_codes = DistrictPassTypeDurationOracleCode.objects.filter(
                    district__isnull=True, option=default_option
                )
                if oracle_codes.exists():
                    district_pass_type_duration_oracle_code = oracle_codes.first()
                    if district_pass_type_duration_oracle_code.oracle_code:
                        logger.info(
                            f"Returning oracle code: {district_pass_type_duration_oracle_code}.",
                        )
                        return district_pass_type_duration_oracle_code.oracle_code

                # If no oracle code is found, then try getting a code from the pass type
                if pass_type.oracle_code:
                    return pass_type.oracle_code

        voucher_content_type = ContentType.objects.get_for_model(Voucher)
        if voucher_content_type == content_type:
            logger.info(
                f"Content type is : {voucher_content_type}.",
            )
            logger.info(
                f"Returning voucher oracle code: {settings.PARKPASSES_DEFAULT_VOUCHER_ORACLE_CODE}.",
            )
            return settings.PARKPASSES_DEFAULT_VOUCHER_ORACLE_CODE
        error_message = (
            f"No oracle code found for this user: {request.user}, "
            f"content_type: {content_type} and object id: {object_id}"
        )
        logger.critical(error_message)
        raise NoOracleCodeFoundForCartItem(error_message)

    @classmethod
    def get_voucher_purchase_description(self, voucher_number):
        return f"{settings.PARKPASSES_VOUCHER_PURCHASE_DESCRIPTION} {voucher_number}"

    @classmethod
    def get_pass_purchase_description(self, pass_number):
        return f"{settings.PARKPASSES_PASS_PURCHASE_DESCRIPTION} {pass_number}"

    @classmethod
    def get_rac_discount_description(self):
        return f"{settings.PARKPASSES_RAC_DISCOUNT_APPLIED_DESCRIPTION}"

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
        logger.info("Resetting cart_item_count session variable to 0.")
        request.session["cart_item_count"] = 0

    @classmethod
    def remove_cart_id_from_session(self, request):
        logger.info("Removing cart_id variable from session.")
        if "cart_id" in request.session:
            logger.info("cart_id variable exists in session. Deleting it.")
            del request.session["cart_id"]
