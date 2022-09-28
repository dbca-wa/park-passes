"""
This management commands generates reports and invoices for each retailer for the previous month

Usage: ./manage.sh retailers_generate_monthly_reports_invoices
        (this command should be run on the 1st day of every month by a cron job or task runner not manually)

"""
import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from parkpasses.components.orders.models import Order
from parkpasses.components.retailers.models import RetailerGroup

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generates reports and invoices for each retailer for the previous month"

    def add_arguments(self, parser):
        parser.add_argument(
            "--test",
            action="store_true",
            help="Add the test flag will output what emails would be sent without actually sending them.",
        )

    def handle(self, *args, **options):
        today = timezone.now().date()
        last_day_of_previous_month = today - timezone.timedelta(days=1)
        first_day_of_previous_month = last_day_of_previous_month.replace()

        retailer_groups = RetailerGroup.objects.all()

        for retailer_group in retailer_groups:
            # report = Report.objects.create()
            no_payment_orders = Order.objects.filter(
                retailer_group=retailer_group,
                is_no_payment=True,
                datetime_created__gte=first_day_of_previous_month,
                datetime_created__lte=last_day_of_previous_month,
            )
            for order in no_payment_orders:
                # todo finish this
                print("finish this")
