from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.urls import path
from ledger_api_client.urls import urlpatterns as ledger_patterns
from rest_framework import routers

from parkpasses import views
from parkpasses.admin import admin
from parkpasses.components.cart.api import LedgerCheckoutView
from parkpasses.components.cart.views import CartView, CheckoutSuccessView
from parkpasses.components.help.views import ParkPassesFAQView, ParkPassesHelpView
from parkpasses.components.orders.views import ExternalOrdersView
from parkpasses.components.passes.views import ExternalPassView
from parkpasses.components.retailers.views import RespondToRetailUserInviteView
from parkpasses.components.vouchers.views import ExternalVouchersView

# API patterns
router = routers.DefaultRouter()

api_patterns = [
    url(r"^api/", include(router.urls)),
]

# URL Patterns
urlpatterns = [
    # ========================================================================== External Public
    url(r"^$", views.ParkPassesRoutingView.as_view(), name="home"),
    url(r"^help/", ParkPassesHelpView.as_view(), name="help"),
    url(
        r"^purchase-voucher/",
        views.ParkPassesPurchaseVoucherView.as_view(),
        name="purchase-voucher",
    ),
    url(
        r"^purchase-pass/",
        views.ParkPassesPurchasePassView.as_view(),
        name="purchase-pass",
    ),
    url(r"^contact/", views.ParkPassesContactView.as_view(), name="contact"),
    url(r"^faq/", ParkPassesFAQView.as_view(), name="faq"),
    url(
        r"^further_info/",
        views.ParkPassesFurtherInformationView.as_view(),
        name="further_information",
    ),
    # ========================================================================== External Authenticated
    url(r"^login-success/", views.LoginSuccessView.as_view(), name="login-success"),
    url(r"^cart/", CartView.as_view(), name="user-cart"),
    url(r"^ledger-checkout/", LedgerCheckoutView.as_view(), name="ledger-checkout"),
    url(
        r"checkout-success/(?P<uuid>.+)/",
        CheckoutSuccessView.as_view(),
        name="checkout-success",
    ),
    url(r"^your-park-passes/", ExternalPassView.as_view(), name="your-park-passes"),
    url(r"^your-vouchers/", ExternalVouchersView.as_view(), name="your-vouchers"),
    url(r"^your-orders/", ExternalOrdersView.as_view(), name="your-orders"),
    url(r"^account/$", views.ExternalView.as_view(), name="manage-account"),
    url(r"^profiles/", views.ExternalView.as_view(), name="manage-profiles"),
    # ========================================================================== Internal
    url(
        r"^internal/$",
        views.InternalView.as_view(extra_context={"title": "Internal Home"}),
        name="internal",
    ),
    url(
        r"^internal/passes/refund-success/(?P<id>.+)/(?P<uuid>.+)$",
        views.InternalView.as_view(
            extra_context={"title": "Internal Pass Refund Success"}
        ),
        name="internal-refund-success",
    ),
    url(
        r"^internal/passes/(?P<id>.+)$",
        views.InternalView.as_view(extra_context={"title": "Internal View/Edit Pass"}),
        name="internal-pass-detail",
    ),
    url(
        r"^internal/passes/upload-personnel-passes$",
        views.InternalView.as_view(
            extra_context={"title": "Internal Upload Personnel Passes"}
        ),
        name="internal-uploader-personnel-passes",
    ),
    url(
        r"^internal/pricing-windows$",
        views.InternalView.as_view(extra_context={"title": "Internal Pricing Windows"}),
        name="internal-pricing-windows",
    ),
    url(
        r"^internal/vouchers$",
        views.InternalView.as_view(extra_context={"title": "Internal Vouchers"}),
        name="internal-vouchers",
    ),
    url(
        r"^internal/discount-codes/",
        views.InternalView.as_view(extra_context={"title": "Internal Discount Codes"}),
        name="internal-discount-codes",
    ),
    url(
        r"^internal/discount-code-batch-form/(?P<id>.+)$",
        views.InternalView.as_view(
            extra_context={"title": "Internal View/Edit Discount Code Batch"}
        ),
        name="internal-discount-code-batch-detail",
    ),
    url(
        r"^internal/pricing-window/(?P<id>.+)$",
        views.InternalView.as_view(
            extra_context={"title": "Internal View/Edit Pricing Window"}
        ),
        name="internal-pricing-window-detail",
    ),
    url(
        r"^internal/retailer-group-users$",
        views.InternalView.as_view(extra_context={"title": "Internal Retail Users"}),
        name="internal-retailer-group-users",
    ),
    url(
        r"^internal/invite-a-retail-user$",
        views.InternalView.as_view(
            extra_context={"title": "Internal Invite a Retail User"}
        ),
        name="internal-invite-retail-user",
    ),
    url(
        r"^internal/reports$",
        views.InternalView.as_view(
            extra_context={"title": "Internal Reports and Invoices"}
        ),
        name="internal-reports",
    ),
    url(
        r"^internal/oracle-codes$",
        views.InternalView.as_view(extra_context={"title": "Oracle Codes"}),
        name="internal-oracle-codes",
    ),
    # ========================================================================== Retailer
    url(
        r"^retailer/$",
        views.RetailerView.as_view(extra_context={"title": "Retailer Home"}),
        name="retailer-home",
    ),
    url(
        r"^retailer/passes/(?P<id>.+)/created-successfully$",
        views.RetailerPassCreatedView.as_view(
            extra_context={"title": "Retailer Pass Created Successfully"}
        ),
        name="retailer-pass-created-successfully",
    ),
    url(
        r"^retailer/passes/(?P<id>.+)$",
        views.RetailerView.as_view(extra_context={"title": "Retailer View/Edit Pass"}),
        name="retailer-pass-detail",
    ),
    url(
        r"^retailer/sell-a-pass/(?P<pass_type_slug>.+)/$",
        views.RetailerSellAPassView.as_view(
            extra_context={"title": "Retailer Sell a Pass"}
        ),
        name="retailer-sell-a-pass-with-pass-type-slug",
    ),
    url(
        r"^retailer/sell-a-pass$",
        views.RetailerSellAPassView.as_view(
            extra_context={"title": "Retailer Sell a Pass"}
        ),
        name="retailer-sell-a-pass",
    ),
    url(
        r"^retailer/users$",
        views.RetailerAdminView.as_view(extra_context={"title": "Retailer Users"}),
        name="retailer-users",
    ),
    url(
        r"^retailer/reports$",
        views.RetailerView.as_view(
            extra_context={"title": "Retailer Invoices and Monthly Reports"}
        ),
        name="retailer-reports",
    ),
    url(
        r"^retailer/reports/(?P<report_number>.+)/payment-success$",
        views.RetailerView.as_view(
            extra_context={"title": "Retailer Invoices and Monthly Reports"}
        ),
        name="retailer-reports-pay-invoice-success",
    ),
    url(
        r"^retailer/reports/(?P<report_number>.+)/payment-failure$",
        views.RetailerView.as_view(
            extra_context={"title": "Retailer Invoices and Monthly Reports"}
        ),
        name="retailer-reports-pay-invoice-failure",
    ),
    url(
        r"^retailer/invite-a-user$",
        views.RetailerView.as_view(extra_context={"title": "Invite a User"}),
        name="retailer-invite-a-user",
    ),
    url(
        r"^retailer/respond-to-invite/(?P<uuid>.+)/$",
        RespondToRetailUserInviteView.as_view(
            extra_context={"title": "Retailer Respond to Invite"}
        ),
        name="respond-to-invite",
    ),
    # ========================================================================== Component API end-points
    url(r"api/passes/", include("parkpasses.components.passes.urls")),
    url(r"api/parks/", include("parkpasses.components.parks.urls")),
    url(r"api/concessions/", include("parkpasses.components.concessions.urls")),
    url(r"api/discount-codes/", include("parkpasses.components.discount_codes.urls")),
    url(r"api/vouchers/", include("parkpasses.components.vouchers.urls")),
    url(r"api/cart/", include("parkpasses.components.cart.urls")),
    url(r"api/help/", include("parkpasses.components.help.urls")),
    url(r"api/orders/", include("parkpasses.components.orders.urls")),
    url(r"api/users/", include("parkpasses.components.users.urls")),
    url(r"api/retailers/", include("parkpasses.components.retailers.urls")),
    url(r"api/reports/", include("parkpasses.components.reports.urls")),
    url(r"api/main/", include("parkpasses.components.main.urls")),
    # ========================================================================== Management Commands
    url(
        r"^mgt-commands/$", views.ManagementCommandsView.as_view(), name="mgt-commands"
    ),
    # ========================================================================== Admin
    path(r"admin/", admin.site.urls),
] + ledger_patterns


if settings.DEBUG:  # Serve media locally in development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if "debug_toolbar" in settings.INSTALLED_APPS and settings.SHOW_DEBUG_TOOLBAR:
        urlpatterns += [
            # ...
            path("__debug__/", include("debug_toolbar.urls")),
        ]
