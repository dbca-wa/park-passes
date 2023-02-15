"""
This management commands makes sure the park passes system is set up in a way
that it can function without any critical issues occuring.

Usage: ./manage.sh parkpasses_check

If there are any critical issues, they will be printed to the console.
"""
from django.core.management.base import BaseCommand

from parkpasses.helpers import park_passes_system_check


class Command(BaseCommand):
    help = "Checks the health status of the parkpasses system."

    def handle(self, *args, **options):
        messages = []
        critical_issues = []

        park_passes_system_check(messages, critical_issues)

        for message in messages:
            self.stdout.write(self.style.SUCCESS(f"{message}\n"))

        critical_issue_count = len(critical_issues)

        if 0 == critical_issue_count:
            self.stdout.write(
                self.style.SUCCESS(
                    "\nPark passes system check completed with no issues.\n\nHAPPY DAYS.\n"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"\nPark passes system check has failed with {critical_issue_count}\
                         critical error{'s' if critical_issue_count>1 else ''}.\n"
                )
            )
            for critical_issue in critical_issues:
                self.stdout.write(self.style.ERROR(f"{critical_issue}\n"))
            self.stdout.write(
                self.style.ERROR("THE SYSTEM REQUIRES URGENT ATTENTION.\n")
            )
