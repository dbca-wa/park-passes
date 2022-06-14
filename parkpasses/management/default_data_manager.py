import logging

from ledger_api_client.managed_models import SystemGroup

from parkpasses import settings
from parkpasses.components.main.models import ApplicationType

logger = logging.getLogger(__name__)


class DefaultDataManager:
    def __init__(self):
        # Application Types
        for item in settings.APPLICATION_TYPES:
            try:
                myType, created = ApplicationType.objects.get_or_create(name=item[0])
                if created:
                    # myType.description = item[1]
                    # myType.save()
                    logger.info(f"Created ApplicationType: {item[1]}")
            except Exception as e:
                logger.error(f"{e}, ApplicationType: {item[1]}")

        # ProposalAssessorGroup
        group, created = SystemGroup.objects.get_or_create(
            name=settings.GROUP_NAME_ASSESSOR
        )

        # ProposalApproverGroup
        group, created = SystemGroup.objects.get_or_create(
            name=settings.GROUP_NAME_APPROVER
        )
