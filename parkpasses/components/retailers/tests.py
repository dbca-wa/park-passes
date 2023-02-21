from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from parkpasses.components.retailers.models import RetailerGroup


class RetailerGroupTestCase(TestCase):
    def setUp(self):
        self.api_request_factory = APIRequestFactory()
        self.retailer_group1 = RetailerGroup.objects.create(
            ledger_organisation=1,
            commission_oracle_code="RETAILER_GROUP_1_ORACLE_CODE",
            commission_percentage=Decimal("10.00"),
            active=True,
        )

    def test_str(self):
        retailer_group_str = self.retailer_group1.__str__()
        self.assertEqual(retailer_group_str, "Org1")
        self.assertNotEqual(retailer_group_str, "Random Name")

    def test_list_retailer_groups(self):
        self.api_request_factory.get("/api/retailers/external/retailer-groups/")
