from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from parkpasses.components.proposals.models import Referral, Proposal

import logging

logger = logging.getLogger(__name__)


class ReferralListener(object):
    """
    Event listener for Referral
    """

    @staticmethod
    @receiver(pre_save, sender=Referral)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = Referral.objects.get(pk=instance.pk)
            setattr(instance, "_original_instance", original_instance)

        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")

    @staticmethod
    @receiver(post_save, sender=Referral)
    def _post_save(sender, instance, **kwargs):
        original_instance = (
            getattr(instance, "_original_instance")
            if hasattr(instance, "_original_instance")
            else None
        )
        if original_instance:
            # Check if the proposal attached to the referral outstanding referrals
            outstanding = instance.proposal.referrals.filter(
                processing_status=Referral.PROCESSING_STATUS_WITH_REFERRAL
            )
            if len(outstanding) == 0:
                instance.proposal.processing_status = (
                    Proposal.PROCESSING_STATUS_WITH_ASSESSOR
                )
                instance.proposal.save()
