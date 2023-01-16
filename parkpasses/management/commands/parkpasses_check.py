"""
This management commands makes sure the park passes system is set up in a way
that it can function without any critical issues occuring.

Usage: ./manage.sh parkpasses_check

If there are any critical issues, they will be printed to the console.
"""
from django.conf import settings
from django.core.management.base import BaseCommand

from parkpasses.components.passes.models import PassType, PassTypePricingWindow
from parkpasses.components.retailers.models import RetailerGroup


class Command(BaseCommand):
    help = "Checks the health status of the parkpasses system."

    def check_DBCA_retailer_group(self):
        dbca_retailer_count = RetailerGroup.objects.filter(
            ledger_organisation=settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID
        ).count()
        if 1 == dbca_retailer_count:
            self.stdout.write(
                self.style.SUCCESS(
                    "SUCCESS: One DBCA Retailer Group Exists where ledger_organisation = '{}'"
                ).format(settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID)
            )
            return 0
        if 1 < dbca_retailer_count:
            self.stdout.write(
                self.style.ERROR(
                    f"CRITICAL: There is more than one retailer group whose ledger_organisation = "
                    f"'{settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID}'"
                )
            )
        if 0 == dbca_retailer_count:
            self.stdout.write(
                self.style.ERROR(
                    "CRITICAL: There is no retailer group whose ledger_organisation = "
                    f"'{settings.PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID}'"
                )
            )
        return 1

    def check_default_pricing_windows(self):
        pass_types = PassType.objects.all()
        issues = 0
        for pass_type in pass_types:
            default_pricing_window_count = PassTypePricingWindow.objects.filter(
                pass_type__id=pass_type.id, name="Default"
            ).count()
            if 1 == default_pricing_window_count:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"SUCCESS: There is one default pricing window for pass type {pass_type.name}"
                    )
                )
            elif 0 == default_pricing_window_count:
                self.stdout.write(
                    self.style.ERROR(
                        f"CRITICAL: There is no default pricing window for pass type  {pass_type.name}"
                    )
                )
                issues += 1
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"CRITICAL: There is more than one default pricing window for pass type {pass_type.name}"
                    )
                )
                issues += 1
        if issues:
            return issues
        return 0

    def handle(self, *args, **options):
        critical_issues = 0

        critical_issues += self.check_DBCA_retailer_group()
        critical_issues += self.check_default_pricing_windows()

        if 0 == critical_issues:
            self.stdout.write(
                self.style.SUCCESS(
                    "\nPark passes system check completed with no issues.\n\nHAPPY DAYS.\n"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"\nPark passes system check has failed with {critical_issues}\
                         critical error{'s' if critical_issues>1 else ''}.\n"
                )
            )
            self.stdout.write(
                self.style.ERROR("THE SYSTEM REQUIRES URGENT ATTENTION.\n")
            )
