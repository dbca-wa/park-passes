import logging

from django.core.management.base import BaseCommand

from parkpasses import settings
from parkpasses.components.main.models import ApplicationType
from parkpasses.components.proposals.models import Proposal

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Remove lease/licence application types."

    def handle(self, *args, **options):
        application_type_lease_licence = ApplicationType.objects.get(
            name=settings.APPLICATION_TYPE_LEASE_LICENCE
        )

        for a_name in [
            "lease",
            "licence",
        ]:
            try:
                app_type = ApplicationType.objects.get(name=a_name)
                proposals = Proposal.objects.filter(application_type=app_type)
                proposals.update(application_type=application_type_lease_licence)
                app_type.delete()
            except Exception as e:
                print(e)
