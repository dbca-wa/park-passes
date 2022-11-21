from decimal import Decimal

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from parkpasses.components.passes.models import (
    Pass,
    PassType,
    PassTypePricingWindow,
    PassTypePricingWindowOption,
)
from parkpasses.components.retailers.models import RetailerGroup


class PassTestCase(TestCase):
    fixtures = ["parkpasses/components/passes/fixtures/pass-types.json"]

    def setUp(self):
        today = timezone.now()
        datetime_in_28_days = timezone.now() + timezone.timedelta(days=28)
        self.holiday_pass_type = PassType.objects.get(name=settings.HOLIDAY_PASS)
        self.holiday_pass_default_pricing_window = PassTypePricingWindow.objects.create(
            name="Default",
            pass_type=self.holiday_pass_type,
            date_start=today,
            date_expiry=datetime_in_28_days,
        )
        self.option1 = PassTypePricingWindowOption.objects.create(
            pricing_window=self.holiday_pass_default_pricing_window,
            name="Option 1",
            duration=5,
            price=Decimal("10.00"),
        )
        self.default_sold_via, created = RetailerGroup.objects.get_or_create(
            name=settings.PARKPASSES_DEFAULT_SOLD_VIA
        )
        self.holiday_pass = Pass.objects.create(
            user=1,
            option=self.option1,
            first_name="Test",
            last_name="User",
            email="test.user@gmail.com",
            mobile="0405454043",
            address_line_1="Address Line 1",
            address_line_2="Address Line 2",
            suburb="Spearwood",
            postcode="6163",
            vehicle_registration_1="12312312",
            vehicle_registration_2="",
            drivers_licence_number="",
            date_start=today,
            renew_automatically=False,
            prevent_further_vehicle_updates=False,
            sold_via=self.default_sold_via,
        )

    def test_pass_number(self):
        pass_id = self.holiday_pass.id
        self.assertEqual(self.holiday_pass.pass_number, f"PP{pass_id:06d}")
        self.assertNotEqual(self.holiday_pass.pass_number, f"PP{pass_id:05d}")
        self.assertNotEqual(self.holiday_pass.pass_number, f"PP{pass_id:07d}")
        self.assertNotEqual(self.holiday_pass.pass_number, "PPRandomString")

    def test_str(self):
        pass_id = self.holiday_pass.id
        holiday_pass_str = self.holiday_pass.__str__()
        self.assertEqual(holiday_pass_str, f"PP{pass_id:06d}")
        self.assertNotEqual(holiday_pass_str, "Random Name")
        self.assertEqual(str(self.holiday_pass), f"PP{pass_id:06d}")
