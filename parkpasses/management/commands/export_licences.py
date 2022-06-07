from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from parkpasses.components.approvals.models import Approval
import datetime

import itertools

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Export licences - ./manage_co.py export_licences"

    def handle(self, *args, **options):

        approvals = []
        repeat = []
        with open("/tmp/export_licences.csv", "w") as f:
            # f.write('Status', 'Lodgement Number', 'Start Date', 'Expiry Date', 'Applicant', 'Organisation', 'Organsiation Email', 'Application Type', 'Migrated')
            f.write(
                "Status; Lodgement Number; Application Number; Start Date; Expiry Date; Applicant; ABN; Trading Name; Organsiation Email; Contacts; Application Type; Migrated\n"
            )
            for a in Approval.objects.all():
                status = a.get_status_display()
                lodgement_number = (
                    a.lodgement_number if hasattr(a, "lodgement_number") else "None"
                )
                application_number = a.current_proposal.lodgement_number
                start_date = a.start_date.strftime("%d-%b-%Y")
                expiry_date = a.expiry_date.strftime("%d-%b-%Y")
                applicant = a.applicant
                abn = a.org_applicant.abn
                # import ipdb; ipdb.set_trace()
                org_applicant = (
                    a.org_applicant.organisation.trading_name
                    if a.org_applicant.organisation.trading_name
                    else "None"
                )
                email = (
                    a.current_proposal.org_applicant.email
                    if a.current_proposal.org_applicant.email
                    else "None"
                )
                contacts = ", ".join(
                    a.org_applicant.contacts.all().values_list("email", flat=True)
                )
                application_type = a.current_proposal.application_type.name
                migrated = "True" if a.current_proposal.migrated else "False"

                out_str = "; ".join(
                    [
                        status,
                        lodgement_number,
                        application_number,
                        start_date,
                        expiry_date,
                        applicant,
                        abn,
                        org_applicant,
                        email,
                        contacts,
                        application_type,
                        migrated,
                    ]
                )
                # f.write(a.status, a.lodgement_number, a.start_date, a.expiry_date, a.applicant, a.org_applicant, a.current_proposal.org_applicant.email, a.current_proposal.application_type, a.current_proposal.migrated)
                f.write(out_str + "\n")

                if lodgement_number not in approvals:
                    approvals.append(lodgement_number)
                else:
                    repeat.append(lodgement_number)
        print("Repeated Approvals: {}".format(repeat))
