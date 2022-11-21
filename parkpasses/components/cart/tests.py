from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from ledger_api_client.ledger_models import EmailUserRO
from rest_framework.test import force_authenticate

from parkpasses.components.cart.models import Cart

User = get_user_model()


class CartTestCase(TestCase):
    def setUp(self):
        user = EmailUserRO(
            first_name="John",
            last_name="Doe",
            email="test.user@totallymadeupemailserver.com",
        )
        self.user_id = user.id
        self.client = Client()
        request = self.client.get("/").wsgi_request
        force_authenticate(request, user=user)
        self.cart1 = Cart.get_or_create_cart(request)
        self.cart2 = Cart.get_or_create_cart(request)
        self.cart1.set_user_for_cart_and_items(1)

    def test_str(self):
        datetime_created = self.cart1.datetime_created
        cart_str = self.cart1.__str__()
        self.assertEqual(cart_str, f"Cart for user: 1 (Created: {datetime_created})")
        self.assertNotEqual(cart_str, "Random Name")
