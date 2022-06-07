from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from ledger.accounts.models import Organisation
import datetime

import itertools

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Export Orgnisation contacts - ./manage_co.py export_contacts > /tmp/contacts.csv"

    def handle(self, *args, **options):
        for i in Organisation.objects.all():
            try:
                org = i.organisation_set.all()[0]
                if hasattr(org, "monthly_invoicing_allowed"):
                    print(
                        "{}, {}, {}, {}".format(
                            org.name,
                            i.trading_name,
                            i.abn,
                            "; ".join(
                                org.contacts.all().values_list("email", flat=True)
                            ),
                        )
                    )
                    # print
            except Exception as e:
                # print '*********************** {}'.format(e)
                pass
