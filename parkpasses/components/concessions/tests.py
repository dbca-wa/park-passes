from django.test import TestCase


class TestTestCase(TestCase):
    def setUp(self):
        pass

    def test_tests(self):
        self.assertEqual("test", "test")
