from django.core.management.base import BaseCommand

from parkpasses.components.retailers.models import RetailerGroup


class Command(BaseCommand):
    help = "Checks the health status of the parkpasses system."

    def check_DBCA_retailer_group(self):
        dbca_retailer_count = RetailerGroup.objects.filter(
            name__icontains="DBCA"
        ).count()
        if 1 == dbca_retailer_count:
            return 0
        if 1 < dbca_retailer_count:
            self.stdout.write(
                self.style.ERROR(
                    "CRITICAL: There is more than one retailer group whose name contains 'DBCA'"
                )
            )
            return 1
        if 0 == dbca_retailer_count:
            self.stdout.write(
                self.style.ERROR(
                    "CRITICAL: There is no retailer group whose name contains 'DBCA'"
                )
            )
            return 1

    def handle(self, *args, **options):
        critical_issues = 0

        critical_issues += self.check_DBCA_retailer_group()

        if 0 == critical_issues:
            self.stdout.write(
                self.style.SUCCESS("Park passes system check completed with no issues.")
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Park passes system check has failed with {critical_issues} critical errors."
                    + "The system requires urgent attention."
                )
            )
