"""
 This management commands attempts to process payment for passes that have autorenewal enabled
 the result of the processing attempts are stored in the database and if there are 3 failed attempts
 then autorenwal is disabled for that pass and the user is notified via email.

Usage: ./manage.sh pass_process_autorenew_payments
        (this command should be run by a cron job or task runner not manually)

"""
import logging
import uuid

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
from parkpasses.components.passes.models import (
    Pass,
    PassAutoRenewalAttempt,
    PassTypePricingWindowOption,
)
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

    def handle(self, *args, **options):
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
            )
        )

        if passes.exists():
            if options["test"]:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Found {len(passes)} park passes that have expired with autorenewal enabled,\
have no successful renewal attempts and have less than 3 unsuccessful renewal attempts."
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

                pass_type = park_pass.option.pricing_window.pass_type

                option = (
                    PassTypePricingWindowOption.get_current_options_by_pass_type_id(
                        pass_type.id
                    )
                    .filter(duration=park_pass.option.duration)
                    .first()
                )

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

                    new_park_pass.date_start = park_pass.date_expiry
                    new_park_pass.renew_automatically = True
                    # Strickly speaking the new pass is not in a cart as it is not stored in a session
                    # however to prevent these passes showing up where they shouldn't we set this flag
                    new_park_pass.in_cart = True
                    new_park_pass.sold_via = park_pass.sold_via

                    new_park_pass.processing_status = Pass.AWAITING_AUTO_RENEWAL
                    new_park_pass.save()

                order_uuid = uuid.uuid4()
                order = Order(user=park_pass.user, uuid=order_uuid)
                order_item = OrderItem()
                order_item.order = order
                order_item.description = CartUtils.get_pass_purchase_description(
                    new_park_pass.pass_number
                )
                order_item.amount = new_park_pass.option.price

                oracle_code = settings.PARKPASSES_DEFAULT_ORACLE_CODE
                if new_park_pass.option.pricing_window.pass_type.oracle_code:
                    oracle_code = (
                        new_park_pass.option.pricing_window.pass_type.oracle_code
                    )

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
                    lines = []
                    lines.append(
                        {
                            "ledger_description": order_item.description,
                            "quantity": 1,
                            "price_incl_tax": order_item.amount,
                            "oracle_code": oracle_code,
                        }
                    )

                    no_payment = False
                    booking_reference = order_uuid
                    content_type = ContentType.objects.get_for_model(park_pass)
                    order_item = OrderItem.objects.get(
                        content_type=content_type, object_id=park_pass.id
                    )
                    booking_reference_link = order_item.order.uuid
                    basket_params = {
                        "products": lines,
                        "vouchers": [],
                        "system": settings.PARKPASSES_PAYMENT_SYSTEM_ID,
                        "custom_basket": True,
                        "booking_reference": booking_reference,
                        "booking_reference_link": booking_reference_link,
                        "no_payment": no_payment,
                    }

                    basket_user_id = request.user.id  # email user id for the customer
                    utils_ledger_api_client.create_basket_session(
                        request, basket_user_id, basket_params
                    )

                    # fallback_url,  return_url,  return_preload_url all need to be set as we are
                    # utilising the same funcationality as the payment checkout screen
                    # sett all 3 values to the same.
                    # return_preload_url is what send a completion ping back to the your application.

                    return_preload_url = request.build_absolute_uri(
                        reverse(
                            "pass-autorenewal-success-callback",
                            kwargs={"uuid": order.uuid},
                        )
                    )

                    checkout_params = {
                        "system": settings.PARKPASSES_PAYMENT_SYSTEM_ID,
                        "fallback_url": return_preload_url,
                        "return_url": return_preload_url,
                        "return_preload_url": return_preload_url,
                        "force_redirect": True,
                        "proxy": False,
                        "invoice_text": "Parkstay test booking",
                        "session_type": "ledger_api",
                        "basket_owner": park_pass.user,
                        "response_type": "json",
                    }

                    utils_ledger_api_client.create_checkout_session(
                        request, checkout_params
                    )

                    # START - Send Automatic Payment Request to Ledger
                    # look at post info on payment screen an reuse
                    resp = utils_ledger_api_client.process_payment_with_token(
                        request, ledger_payment_token_id
                    )
                    print(resp)
                    # END - Sent Automatic Payment Request to Ledger

                    PassAutoRenewalAttempt.objects.create(
                        park_pass=park_pass,
                        auto_renewal_succeeded=True,
                    )

                    order.save()
                    order_item.save()

                    park_pass.renew_automatic = False
                    park_pass.save()

                except Exception as e:
                    PassAutoRenewalAttempt.objects.create(
                        park_pass=park_pass,
                        auto_renewal_succeeded=False,
                    )

                    print(type(e).__name__, e)

                    # For park passes that already had two failed attempts, that means this is the 3rd failed attempt
                    # We will disable automatic renewal and send a final fail email so the user can manually renew
                    if 2 == park_pass.failed_auto_renewal_attempts:
                        logger.info(
                            "Disabling automatic renewal for park pass %s",
                            park_pass.pass_number,
                        )
                        park_pass.renew_automatic_failed = False
                        park_pass.save()
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
