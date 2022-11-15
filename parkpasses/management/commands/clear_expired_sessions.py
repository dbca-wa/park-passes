"""
This management commands deleted and park passes objects from sessions
that have expired and then deletes those sessions.

Usage: ./manage.sh clear_expired_sessions

"""
from importlib import import_module

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from parkpasses.components.cart.models import Cart


class Command(BaseCommand):
    help = "Clears expired sessions for the park passes system."

    def handle(self, *args, **options):
        now = timezone.now()
        two_weeks_ago = now - timezone.timedelta(days=14)

        self.stdout.write(
            "Selecting any expired park passes carts (that were last added to more than 14 days ago)"
        )
        if Cart.objects.filter(datetime_last_added_to__lte=two_weeks_ago).exists():
            expired_carts = Cart.objects.filter(
                datetime_last_added_to__lte=two_weeks_ago
            )
            for expired_cart in expired_carts:
                expired_cart_items = expired_cart.items.all()
                for expired_cart_item in expired_cart_items:
                    expired_cart_item.delete()
                expired_cart.delete()
        else:
            self.stdout.write("No expired park passes carts found.")

        self.stdout.write("Clearing expired django sessions.")
        engine = import_module(settings.SESSION_ENGINE)
        engine.SessionStore.clear_expired()

        self.stdout.write(self.style.SUCCESS("Expired django sessions cleared."))
