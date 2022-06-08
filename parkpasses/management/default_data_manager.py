import logging
import os

from django.core.files import File
from ledger_api_client.managed_models import SystemGroup

from parkpasses import settings
from parkpasses.components.main.models import ApplicationType, GlobalSettings

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

        # Store
        for item in GlobalSettings.keys:
            try:
                obj, created = GlobalSettings.objects.get_or_create(key=item[0])
                if created:
                    if item[0] in GlobalSettings.keys_for_file:
                        with open(
                            GlobalSettings.default_values[item[0]], "rb"
                        ) as doc_file:
                            obj._file.save(
                                os.path.basename(
                                    GlobalSettings.default_values[item[0]]
                                ),
                                File(doc_file),
                                save=True,
                            )
                        obj.save()
                    else:
                        obj.value = item[1]
                        obj.save()
                    logger.info(f"Created {item[0]}: {item[1]}")
            except Exception as e:
                logger.error(f"{e}, Key: {item[0]}")

        # ProposalAssessorGroup
        group, created = SystemGroup.objects.get_or_create(
            name=settings.GROUP_NAME_ASSESSOR
        )

        # ProposalApproverGroup
        group, created = SystemGroup.objects.get_or_create(
            name=settings.GROUP_NAME_APPROVER
        )
