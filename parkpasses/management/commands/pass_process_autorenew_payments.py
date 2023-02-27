"""
 This management commands attempts to process payment for passes that have autorenewal enabled
 the result of the processing attempts are stored in the database and if there are 3 failed attempts
 then autorenwal is disabled for that pass and the user is notified via email.

Usage: ./manage.sh pass_process_autorenew_payments
        (this command should be run by a cron job or task runner not manually)

"""
import logging
import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.urls import reverse
from django.utils import timezone
from ledger_api_client import utils as utils_ledger_api_client
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from parkpasses.components.cart.utils import CartUtils
from parkpasses.components.orders.models import Order, OrderItem
from parkpasses.components.passes.models import Pass, PassAutoRenewalAttempt, PassType
from parkpasses.components.retailers.models import RetailerGroup

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Attempts to process payment for all passes that expired recently and had autorenewal enabled."

    def add_arguments(self, parser):
        parser.add_argument(
            "--test",
            action="store_true",
            help="Adding the test flag will output what payments would be processed without actually processing them.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Adding the clear flag will reset the data state for testing purposes.",
        )

    def clear_test_data(self, park_pass_content_type):
        # Delete the new pass that was just created
        park_pass_just_created = Pass.objects.order_by("-id").first()
        containing_order_item = OrderItem.objects.filter(
            content_type=park_pass_content_type, object_id=park_pass_just_created.id
        ).first()
        if containing_order_item:
            if containing_order_item.order:
                order = containing_order_item.order
                order.items.all().delete()
                order.delete()
        park_pass_just_created.delete()
        # Get the pass we are testing with
        p = Pass.objects.get(id=350)
        # Delete all the auto renewal attempts
        p.auto_renewal_attempts.all().delete()
        # Turn auto renewal back on
        p.renew_automatically = True
        p.save()

    def handle(self, *args, **options):
        park_pass_content_type = ContentType.objects.get_for_model(Pass)
        if options["clear"]:
            self.clear_test_data(park_pass_content_type)

        no_reply_email_user, created = EmailUser.objects.get_or_create(
            email=settings.NO_REPLY_EMAIL, password=""
        )
        today = timezone.now().date()

        successful_auto_renewal_attempts = Count(
            "auto_renewal_attempts",
            filter=Q(auto_renewal_attempts__auto_renewal_succeeded=True),
        )
        failed_auto_renewal_attempts = Count(
            "auto_renewal_attempts",
            filter=Q(auto_renewal_attempts__auto_renewal_succeeded=False),
        )

        dbca_retailer_group = RetailerGroup.get_dbca_retailer_group()

        auto_renewal_pass_types = PassType.objects.filter(
            can_be_renewed_automatically=True
        )

        passes = (
            Pass.objects.exclude(processing_status=Pass.CANCELLED)
            .annotate(successful_auto_renewal_attempts=successful_auto_renewal_attempts)
            .annotate(failed_auto_renewal_attempts=failed_auto_renewal_attempts)
            .filter(
                in_cart=False,
                renew_automatically=True,
                sold_via=dbca_retailer_group,
                date_expiry__lte=today,
                successful_auto_renewal_attempts=0,
                failed_auto_renewal_attempts__lt=3,
                option__pricing_window__pass_type__in=auto_renewal_pass_types,
            )
        )

        if passes.exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f"Found {len(passes)} park passes that have expired with autorenewal enabled, "
                    "have no successful renewal attempts and have less than 3 unsuccessful renewal attempts."
                )
            )
            for park_pass in passes:
                if options["test"]:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"TEST: pretending to process automatic renewal of Pass: {park_pass}"
                        )
                    )
                    continue

                if Pass.objects.filter(user=park_pass.user):
                    pass  # todo

                # We have to give the customer warning of how much will be charged to their account
                # See the doc string for the following method for more information
                option = park_pass.get_next_renewal_option

                if (
                    1
                    == Pass.objects.filter(
                        user=park_pass.user,
                        in_cart=True,
                        park_pass_renewed_from=park_pass,
                    ).count()
                ):
                    new_park_pass = Pass.objects.get(
                        user=park_pass.user,
                        in_cart=True,
                        park_pass_renewed_from=park_pass,
                    )
                else:
                    new_park_pass = Pass()
                    new_park_pass.park_pass_renewed_from = park_pass
                    new_park_pass.user = park_pass.user
                    new_park_pass.option = option
                    new_park_pass.first_name = park_pass.first_name
                    new_park_pass.last_name = park_pass.last_name
                    new_park_pass.email = park_pass.email
                    new_park_pass.mobile = park_pass.mobile

                    if park_pass.company:
                        new_park_pass.company = park_pass.company
                    if park_pass.address_line_1:
                        new_park_pass.address_line_1 = park_pass.address_line_1
                    if park_pass.address_line_2:
                        new_park_pass.address_line_2 = park_pass.address_line_2

                    new_park_pass.suburb = park_pass.suburb
                    new_park_pass.state = park_pass.state
                    new_park_pass.postcode = park_pass.postcode

                    if park_pass.rac_member_number:
                        new_park_pass.rac_member_number = park_pass.rac_member_number

                    if park_pass.vehicle_registration_1:
                        new_park_pass.vehicle_registration_1 = (
                            park_pass.vehicle_registration_1
                        )

                    if park_pass.vehicle_registration_2:
                        new_park_pass.vehicle_registration_2 = (
                            park_pass.vehicle_registration_2
                        )

                    if park_pass.drivers_licence_number:
                        new_park_pass.drivers_licence_number = (
                            park_pass.drivers_licence_number
                        )

                    if park_pass.park_group:
                        new_park_pass.park_group = park_pass.park_group

                    new_park_pass.date_start = today
                    new_park_pass.renew_automatically = True
                    # Strickly speaking the new pass is not in a cart as it is not stored in a session
                    # however to prevent these passes showing up where they shouldn't we set this flag
                    new_park_pass.in_cart = True
                    new_park_pass.sold_via = park_pass.sold_via

                    new_park_pass.processing_status = Pass.AWAITING_AUTO_RENEWAL
                    new_park_pass.save()

                logger.info("new_park_pass.in_cart = " + str(new_park_pass.in_cart))
                order_uuid = uuid.uuid4()
                # Every order must have an invoice reference but we don't yet have one so for now
                # we use the order uuid (the real reference number will be populated by the return_preload_url code)
                order = Order(
                    user=park_pass.user,
                    uuid=order_uuid,
                    invoice_reference=order_uuid,
                    retailer_group=dbca_retailer_group,
                )
                order_item = OrderItem()
                order_item.content_type = park_pass_content_type
                order_item.object_id = new_park_pass.id
                order_item.description = CartUtils.get_pass_purchase_description(
                    new_park_pass.pass_number
                )
                order_item.amount = new_park_pass.option.price
                order_item.oracle_code = settings.PARKPASSES_DEFAULT_ORACLE_CODE
                if new_park_pass.option.pricing_window.pass_type.oracle_code:
                    order_item.oracle_code = (
                        new_park_pass.option.pricing_window.pass_type.oracle_code
                    )

                # Check if the pass was purchased with an rac discount and if so apply the same discount
                rac_discount_order_item = None
                concession_order_item = None
                if hasattr(park_pass, "rac_discount_usage"):
                    discount_amount = park_pass.rac_discount_usage.discount_amount
                    if discount_amount > Decimal(0.00):
                        rac_discount_order_item = OrderItem()
                        rac_discount_order_item.description = (
                            CartUtils.get_rac_discount_description()
                        )
                        rac_discount_order_item.amount = -abs(discount_amount)
                        rac_discount_order_item.oracle_code = order_item.oracle_code
                # If the pass wasn't purchased with an RAC discount then check if it was purchased with
                # a concession and if so apply that concession
                elif hasattr(park_pass, "concession_usage"):
                    concession_discount_amount = (
                        park_pass.concession_usage.concession.discount_as_amount(
                            park_pass.option.price
                        )
                    )
                    if concession_discount_amount > Decimal(0.00):
                        concession_order_item = OrderItem()
                        concession_order_item.description = (
                            CartUtils.get_rac_discount_description()
                        )
                        concession_order_item.amount = -abs(concession_discount_amount)
                        concession_order_item.oracle_code = order_item.oracle_code

                logger.info("order_item = " + str(order_item))

                try:
                    # Get ledger payment token id
                    primary_card_resp = (
                        utils_ledger_api_client.get_primary_card_token_for_user(
                            park_pass.user
                        )
                    )
                    ledger_payment_token_id = primary_card_resp["primary_card"]
                    if not ledger_payment_token_id:
                        raise Exception(
                            f"No primary card found for user {park_pass.user}"
                        )

                    # Create a fake request session Id
                    request = utils_ledger_api_client.FakeRequestSessionObj()

                    # using email user assign the email user object to the fake request
                    request.user = EmailUser.objects.get(id=park_pass.user)

                    # Payment Basket Lines
                    products = []
                    if order_item:
                        products.append(
                            {
                                "ledger_description": order_item.description,
                                "quantity": 1,
                                "price_excl_tax": str(order_item.amount),
                                "price_incl_tax": str(order_item.amount),
                                "oracle_code": order_item.oracle_code,
                            }
                        )
                    if rac_discount_order_item:
                        products.append(
                            {
                                "ledger_description": rac_discount_order_item.description,
                                "quantity": 1,
                                "price_excl_tax": str(rac_discount_order_item.amount),
                                "price_incl_tax": str(rac_discount_order_item.amount),
                                "oracle_code": rac_discount_order_item.oracle_code,
                            }
                        )
                    elif concession_order_item:
                        products.append(
                            {
                                "ledger_description": concession_order_item.description,
                                "quantity": 1,
                                "price_excl_tax": str(concession_order_item.amount),
                                "price_incl_tax": str(concession_order_item.amount),
                                "oracle_code": concession_order_item.oracle_code,
                            }
                        )

                    no_payment = False
                    booking_reference = str(order_uuid)

                    # Get the uuid for the order containing the original pass purchase
                    renewed_from_order_item = OrderItem.objects.get(
                        content_type=park_pass_content_type, object_id=park_pass.id
                    )
                    booking_reference_link = str(renewed_from_order_item.order.uuid)

                    basket_params = {
                        "products": products,
                        "vouchers": [],
                        "system": settings.PARKPASSES_PAYMENT_SYSTEM_ID,
                        "tax_override": True,
                        "custom_basket": True,
                        "booking_reference": booking_reference,
                        "booking_reference_link": booking_reference_link,
                        "no_payment": no_payment,
                    }

                    logger.info("basket_params: %s", basket_params)

                    basket_user_id = request.user.id  # email user id for the customer
                    utils_ledger_api_client.create_basket_session(
                        request, basket_user_id, basket_params
                    )

                    # fallback_url,  return_url,  return_preload_url all need to be set as we are
                    # utilising the same funcationality as the payment checkout screen
                    # sett all 3 values to the same.
                    # return_preload_url is what send a completion ping back to the your application.

                    return_preload_url = settings.SITE_URL + reverse(
                        "pass-autorenewal-success-callback",
                        kwargs={
                            "id": str(new_park_pass.id),
                            "uuid": str(order.uuid),
                        },
                    )

                    logger.info("return_preload_url = " + str(return_preload_url))

                    invoice_text = f"Park Passes Order: {order.uuid}"

                    checkout_params = {
                        "system": settings.PARKPASSES_PAYMENT_SYSTEM_ID,
                        "fallback_url": return_preload_url,
                        "return_url": return_preload_url,
                        "return_preload_url": return_preload_url,
                        "force_redirect": True,
                        "proxy": False,
                        "invoice_text": invoice_text,
                        "session_type": "ledger_api",
                        "basket_owner": park_pass.user,
                        "response_type": "json",
                    }

                    utils_ledger_api_client.create_checkout_session(
                        request, checkout_params
                    )

                    # We have to save the order before processing the payment because we will store the
                    # invoice reference number in the order when the code at the return_preload_url is called.
                    order.save()

                    # START - Send Automatic Payment Request to Ledger
                    # look at post info on payment screen an reuse
                    resp = utils_ledger_api_client.process_payment_with_token(
                        request, ledger_payment_token_id
                    )
                    logger.info(resp)
                    # END - Sent Automatic Payment Request to Ledger

                    order_item.order = order
                    order_item.save()

                    if rac_discount_order_item:
                        rac_discount_order_item.order = order
                        rac_discount_order_item.save()
                    elif concession_order_item:
                        concession_order_item.order = order
                        concession_order_item.save()

                    park_pass.renew_automatically = False
                    park_pass.save()

                    PassAutoRenewalAttempt.objects.create(
                        park_pass=park_pass,
                        auto_renewal_succeeded=True,
                    )

                    order.payment_confirmed = True
                    order.save()

                    new_park_pass.in_cart = False
                    new_park_pass.save()
                    new_park_pass.send_autorenew_success_notification_email()

                except Exception as e:
                    PassAutoRenewalAttempt.objects.create(
                        park_pass=park_pass,
                        auto_renewal_succeeded=False,
                    )

                    logger.info(f"{type(e).__name__}: {e}")

                    # For park passes that already had two failed attempts, that means this is the 3rd failed attempt
                    # We will disable automatic renewal and send a final fail email so the user can manually renew
                    if 2 == park_pass.failed_auto_renewal_attempts:
                        logger.info(
                            "Disabling automatic renewal for park pass %s",
                            park_pass.pass_number,
                        )
                        park_pass.renew_automatically = False
                        park_pass.save()
                        new_park_pass.delete()
                        park_pass.send_final_autorenewal_failure_notification_email()
                        continue

                    logger.info(
                        "Sending autorenew failure notification email for park pass %s",
                        park_pass.pass_number,
                    )
                    park_pass.send_autorenew_failure_notification_email(
                        park_pass.failed_auto_renewal_attempts + 1
                    )
                    # Send fail email
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Found {len(passes)} park passes that have expired with autorenewal enabled, have no successful\
                         renewal attempts and have less than 3 unsuccessful renewal attempts."
                )
            )
