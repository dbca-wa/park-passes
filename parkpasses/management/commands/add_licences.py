import logging

from django.core.management.base import BaseCommand

from parkpasses.utils.migration_utils import OrganisationReader

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Runs the initial deployment
    """

    help = "Run the initial deployment"

    def handle(self, *args, **options):
        reader = OrganisationReader(
            "parkpasses/utils/csv/CommercialLicencesMigration_07Jan2020_final.csv"
        )
        reader.create_licences()
