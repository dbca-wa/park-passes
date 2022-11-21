from decimal import Decimal

from django.test import TestCase

from parkpasses.components.concessions.models import Concession


class ConcessionTestCase(TestCase):
    def setUp(self):
        self.pensioner_concession_card = Concession.objects.create(
            concession_type="Pensioner Concession Card", discount_percentage=15
        )
        self.low_income_health_care_card = Concession.objects.create(
            concession_type="Low Income Health Care Card", discount_percentage=9
        )

    def test_str(self):
        concession_str = self.pensioner_concession_card.__str__()
        self.assertEqual(concession_str, "Pensioner Concession Card")
        self.assertNotEqual(concession_str, "Random Name")
        self.assertEqual(
            str(self.low_income_health_care_card), "Low Income Health Care Card"
        )

    def test_discount_percentage(self):
        self.assertEqual(
            self.pensioner_concession_card.discount_percentage, Decimal("15.00")
        )
        self.assertNotEqual(
            self.pensioner_concession_card.discount_percentage, Decimal("1.00")
        )
        self.assertEqual(
            self.low_income_health_care_card.discount_percentage, Decimal("9.00")
        )
        self.assertNotEqual(
            self.low_income_health_care_card.discount_percentage, Decimal("7.00")
        )
