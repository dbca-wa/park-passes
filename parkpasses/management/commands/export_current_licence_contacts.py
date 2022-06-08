import logging

from django.core.management.base import BaseCommand

from parkpasses.components.approvals.models import Approval

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Export Current Licence contacts - ./manage_co.py export_current_licence_contacts > /tmp/contacts.csv (cp to media/cols/ to access via web)"

    def handle(self, *args, **options):
        print(
            "Logdement Number: Expiry Date: Type: ABN: Org Name: Trading Name: Org Address: Org Contacts: Org Admin Users"
        )
        for a in Approval.objects.filter(status="current"):
            try:
                # org = i.organisation_set.all()[0]
                org = a.org_applicant
                if hasattr(org, "monthly_invoicing_allowed"):
                    print(
                        "{}: {}: {}: {}: {}: {}: {}: {}: {}".format(
                            a.lodgement_number,
                            a.expiry_date,
                            a.current_proposal.application_type.name,
                            org.abn,
                            org.name,
                            org.organisation.trading_name,
                            org.address.summary,
                            "; ".join(
                                org.contacts.all().values_list("email", flat=True)
                            ),
                            list(
                                org.contacts.filter(
                                    is_admin=True, user_role="organisation_admin"
                                ).values_list("email", "first_name", "last_name")
                            ),
                        )
                    )
                    # print
            except Exception as e:
                print(f"*********************** {e}")
