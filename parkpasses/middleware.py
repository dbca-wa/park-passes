from django.urls import reverse
from django.shortcuts import redirect
from django.utils.http import urlquote_plus

import re
import datetime

from django.http import HttpResponseRedirect
from django.utils import timezone
from parkpasses.components.bookings.models import ApplicationFee
from reversion.middleware import RevisionMiddleware
from reversion.views import _request_creates_revision


CHECKOUT_PATH = re.compile("^/ledger/checkout/checkout")


class FirstTimeNagScreenMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated()
            and request.method == "GET"
            and "api" not in request.path
            and "admin" not in request.path
        ):
            if (not request.user.first_name) or (
                not request.user.last_name
            ):  # or (not request.user.dob):
                path_ft = reverse("first_time")
                path_logout = reverse("accounts:logout")
                if request.path not in (path_ft, path_logout):
                    return redirect(
                        reverse("first_time")
                        + "?next="
                        + urlquote_plus(request.get_full_path())
                    )


class BookingTimerMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "lals_app_invoice" in request.session:
            try:
                application_fee = ApplicationFee.objects.get(
                    pk=request.session["lals_app_invoice"]
                )
            except:
                del request.session["lals_app_invoice"]
                return
            if application_fee.payment_type != ApplicationFee.PAYMENT_TYPE_TEMPORARY:
                del request.session["lals_app_invoice"]
        return


class RevisionOverrideMiddleware(RevisionMiddleware):

    """
    Wraps the entire request in a revision.

    override venv/lib/python2.7/site-packages/reversion/middleware.py
    """

    # exclude ledger payments/checkout from revision - hack to overcome basket (lagging status) issue/conflict with reversion
    def request_creates_revision(self, request):
        return (
            _request_creates_revision(request)
            and "checkout" not in request.get_full_path()
        )
