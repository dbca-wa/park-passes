"""
This management commands sends emails to customers who have have a pass that expired today.

Usage: ./manage.sh oracles_codes_create_initial_records
        (this command should be run by a cron job or task runner not manually)

        WARNING: This script is designed to be run once and only once. It will delete all existing records in the
        DistrictPassTypeDurationOracleCode table and then create new records for all districts and pass types.

        Make sure you know what you are doing before running this script.

        TODO: Remove me after production deployment is successful.

"""
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from parkpasses.components.passes.models import (
    District,
    DistrictPassTypeDurationOracleCode,
    PassTypePricingWindowOption,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Creates all the initial records for Oracle Codes that are required by the system"

    def add_arguments(self, parser):
        parser.add_argument(
            "--test",
            action="store_true",
            help="Adding the test flag will output what emails would be sent without actually sending them.",
        )
        parser.add_argument(
            "--unique",
            action="store_true",
            help="Adding the unique flag will assign every record generated a unqiue oracle code so the park \
                passes system check passes. ONLY use this flag for testing purposes.",
        )

    def handle(self, *args, **options):
        DistrictPassTypeDurationOracleCode.objects.all().delete()
        districts = District.objects.all()
        default_options = (
            PassTypePricingWindowOption.objects.exclude(
                pricing_window__pass_type__name__in=[
                    settings.PERSONNEL_PASS,
                    settings.PINJAR_OFF_ROAD_VEHICLE_AREA_ANNUAL_PASS,
                ]
            )
            .filter(
                pricing_window__name=settings.PRICING_WINDOW_DEFAULT_NAME,
                pricing_window__date_expiry__isnull=True,
            )
            .order_by("pricing_window__pass_type__display_order")
        )

        oracle_code = f"{settings.UNENTERED_ORACLE_CODE_LABEL}"

        # Generate PICA Oracle Codes first (no district as they are online sales)
        for option in default_options:
            duration = option.name.replace(" ", "_")
            logger.info(
                f"Setting oracle code for district: PICA, pass type: {option.pricing_window.pass_type.name} "
                f"and duration: {duration} to: {oracle_code}"
            )
            if options["unique"]:
                oracle_code = (
                    f"PICA_{option.pricing_window.pass_type.name}_{duration}".upper()
                )
            if not options["test"]:
                (
                    oracles_code,
                    created,
                ) = DistrictPassTypeDurationOracleCode.objects.get_or_create(
                    district=None, option=option, oracle_code=oracle_code
                )
            for district in districts:
                logger.info(
                    f"Setting oracle code for district: {district}, "
                    f"pass type: {option.pricing_window.pass_type.name} and duration: {duration} to: {oracle_code}"
                )
                if options["unique"]:
                    district_name = district.name.replace(" ", "_").upper()
                    oracle_code = f"{district_name}_{option.pricing_window.pass_type.name}_{duration}".upper()

                if not options["test"]:
                    (
                        oracles_code,
                        created,
                    ) = DistrictPassTypeDurationOracleCode.objects.get_or_create(
                        district=district, option=option, oracle_code=oracle_code
                    )
            logger.info("\n")
