import logging
from datetime import datetime

from django.core.management.base import BaseCommand
from ledger.payments.reports import generate_items_csv_allocated

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Runs the initial deployment
    """

    help = "Run the initial deployment"

    def handle(self, *args, **options):

        system = "0557"
        start = datetime(2019, 12, 11)
        end = datetime(2019, 12, 11)
        banked_start = datetime(2019, 12, 11)
        banked_end = datetime(2019, 12, 11)
        generate_items_csv_allocated(system, start, end, banked_start, banked_end)
