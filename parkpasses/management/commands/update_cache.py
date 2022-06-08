import logging

from django.core.management.base import BaseCommand

from parkpasses.components.bookings.models import BookingInvoice

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Updates the property_cache"

    def handle(self, *args, **options):
        logger.info(f"Running command {__name__}")
        # unset the cache
        BookingInvoice.objects.all().update(property_cache={})

        # rebuild the cache
        for bi in BookingInvoice.objects.all():
            bi.update_property_cache()

        cmd_name = __name__.split(".")[-1].replace("_", " ").upper()
        err_str = '<strong style="color: green;">Errors: 0</strong>'
        msg = f"<p>{cmd_name} completed. {err_str}.</p>"
        logger.info(msg)
        print(msg)  # will redirect to cron_tasks.log file, by the parent script
