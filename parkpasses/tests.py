# import datetime

# from django.contrib.auth.models import AnonymousUser
# from django.contrib.auth.models import User

# from django.test import Client, TestCase
# from django.test.client import RequestFactory

# from ledger_api_client.ledger_models import EmailUserRO as EmailUser

# from parkpasses import helpers


# class SimpleTest(TestCase):
#     def setUp(self):
#         self.client = Client()

#         self.external_user = \
#           TestUser(
# {'id': 238343,
# 'is_authenticated':True,
# 'is_anonymous': False,
# 'is_superuser': False,
# 'email': 'test.user@gmail.com',
# 'first_name': 'Oak2',
# 'last_name': 'McIlwain2',
# 'is_staff': False,
# 'is_active': True,
# 'title': None, 'dob':
# datetime.date(1982, 3, 5),
# 'phone_number': '1234 1234',
# 'position_title': None,
# 'mobile_number': '1234 1235',
# 'fax_number': None,
# 'organisation': None,
# 'residential_address_id': 209725,
# 'postal_address_id': None,
# 'postal_same_as_residential': False,
# 'billing_address_id': None,
# 'billing_same_as_residential': False,
# 'identification_id': None,
# 'identification2_id': None,
# 'senior_card_id': None,
# 'senior_card2_id': None,
# 'character_flagged': False,
# 'character_comments': '',
# 'manager_email': None,
# 'manager_name': None,
# 'extra_data': {},
# '_password': None}
# )
#         #self.retailer_user = EmailUser.objects.get(email='oak1.mcilwain@gmail.com')
#         #self.internal_user = EmailUser.objects.get(email='oak.mcilwain@dbca.wa.gov.au')

#         self.factory = RequestFactory()

#     def test_helpers(self):
#         request = self.factory.get('/')
#         request.user = AnonymousUser()
#         self.assertEqual(helpers.is_retailer(request), False)
#         request.user = self.external_user
#         self.assertEqual(helpers.is_retailer(request), False)
