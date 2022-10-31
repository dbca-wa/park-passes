from django.test import TestCase
from django.utils import timezone

from parkpasses.components.discount_codes.models import DiscountCode, DiscountCodeBatch


class DiscountCodeBatchTestCase(TestCase):
    def setUp(self):
        discount_code_batch1 = DiscountCodeBatch(
            created_by=1,
            datetime_start=timezone.now(),
            datetime_expiry=timezone.now() + timezone.timedelta(365),
            codes_to_generate=3,
            times_each_code_can_be_used=3,
            discount_percentage=25,
        )
        discount_code_batch1.save()
        discount_code_batch2 = DiscountCodeBatch(
            created_by=2,
            datetime_start=timezone.now() + timezone.timedelta(30),
            datetime_expiry=timezone.now() + timezone.timedelta(60),
            codes_to_generate=7,
            times_each_code_can_be_used=8,
            discount_amount=15,
        )
        discount_code_batch2.save()
        discount_code_batch3 = DiscountCodeBatch(
            created_by=3,
            datetime_start=timezone.now() + timezone.timedelta(40),
            datetime_expiry=timezone.now() + timezone.timedelta(60),
            codes_to_generate=12,
            times_each_code_can_be_used=0,
            discount_percentage=33,
        )
        discount_code_batch3.save()
        # park_pass = Pass()
        self.discount_code_batch1 = discount_code_batch1
        self.discount_code_batch2 = discount_code_batch2
        self.discount_code_batch3 = discount_code_batch3
        self.first_discount_code_batch = DiscountCodeBatch.objects.all().first()

    def test_discount_code_generation(self):
        discount_codes = list(
            DiscountCode.objects.filter(discount_code_batch=self.discount_code_batch1)
        )
        self.assertTrue(len(discount_codes), 3)

    def test_discount_code_str(self):
        discount_codes = list(
            DiscountCode.objects.filter(
                discount_code_batch=self.first_discount_code_batch
            )
        )
        discount_code = discount_codes[0]
        code = discount_code.code
        self.assertEqual(str(discount_code), f"{code} (25% Off)")
        discount_codes = list(
            DiscountCode.objects.filter(discount_code_batch=self.discount_code_batch2)
        )
        discount_code = discount_codes[0]
        code = discount_code.code
        self.assertEqual(str(discount_code), f"{code} ($15.00 Off)")

    def test_discount_code_remaining_uses(self):
        discount_codes = list(
            DiscountCode.objects.filter(
                discount_code_batch=self.first_discount_code_batch
            )
        )
        discount_code = discount_codes[0]
        self.assertEqual(discount_code.remaining_uses, 3)
        discount_codes = list(
            DiscountCode.objects.filter(discount_code_batch=self.discount_code_batch3)
        )
        discount_code = discount_codes[0]
        self.assertEqual(discount_code.remaining_uses, 999999999)

    def test_discount_code_usage(self):
        pass
        # discount_code_usage = DiscountCodeUsage()
