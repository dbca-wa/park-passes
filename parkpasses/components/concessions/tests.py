from django.test import TestCase

from parkpasses.components.concessions.models import Concession


class ConcessionTestCase(TestCase):
    def setUp(self):
        Concession.objects.create(
            concession_type="Pensioner Concession Card", discount_percentage=15
        )
        Concession.objects.create(
            concession_type="Low Income Health Care Card", discount_percentage=9
        )

    def test_str(self):
        pensioner_concession_card = Concession.objects.get(
            concession_type="Pensioner Concession Card"
        )
        low_income_health_care_card = Concession.objects.get(
            concession_type="Low Income Health Care Card"
        )
        concession_str = pensioner_concession_card.__str__()
        self.assertEqual(concession_str, "Pensioner Concession Card")
        self.assertEqual(
            str(low_income_health_care_card), "Low Income Health Care Card"
        )
