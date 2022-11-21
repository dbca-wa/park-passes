from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from parkpasses.components.vouchers.models import Voucher


class VouchersTestCase(TestCase):
    def setUp(self):
        self.datetime_in_future = timezone.now() + timezone.timedelta(days=365)
        self.voucher1 = Voucher.objects.create(
            purchaser=1,
            recipient_name="John Smith",
            recipient_email="john.smith@totallymadeupmailserver.com",
            datetime_to_email=self.datetime_in_future,
            personal_message="A very personal message.",
            amount=Decimal("73.50"),
        )
        # self.voucher_transaction1 = VoucherTransaction.objects.create()

    def test_voucher_number(self):
        voucher_id = self.voucher1.id
        self.assertEqual(self.voucher1.voucher_number, f"V{voucher_id:06d}")
        self.assertNotEqual(self.voucher1.voucher_number, f"V{voucher_id:05d}")
        self.assertNotEqual(self.voucher1.voucher_number, f"V{voucher_id:07d}")
        self.assertNotEqual(self.voucher1.voucher_number, "VRandomString")

    def test_str(self):
        voucher_str = self.voucher1.__str__()
        self.assertEqual(
            voucher_str, f"{self.voucher1.voucher_number} (${self.voucher1.amount})"
        )
        self.assertNotEqual(voucher_str, "Random String")
