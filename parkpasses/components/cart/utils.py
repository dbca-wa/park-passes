from django.contrib.contenttypes.models import ContentType

from parkpasses.components.passes.models import Pass
from parkpasses.components.passes.serializers import ExternalPassSerializer
from parkpasses.components.vouchers.models import Voucher
from parkpasses.components.vouchers.serializers import ExternalVoucherSerializer


class CartUtils:
    @classmethod
    def get_serialized_object_by_id_and_content_type(self, object_id, content_type_id):
        content_type = ContentType.objects.get(id=content_type_id)
        if "parkpasses | voucher" == str(content_type):
            voucher = Voucher.objects.get(id=object_id)
            return ExternalVoucherSerializer(voucher).data
        if "parkpasses | pass" == str(content_type):
            park_pass = Pass.objects.get(id=object_id)
            return ExternalPassSerializer(park_pass).data
