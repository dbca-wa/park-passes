from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.urls import path
from ledger_api_client.urls import urlpatterns as ledger_patterns
from rest_framework import routers

from parkpasses import views
from parkpasses.admin import admin

# API patterns
router = routers.DefaultRouter()

api_patterns = [
    url(r"^api/", include(router.urls)),
]

# URL Patterns
urlpatterns = [
    path(r"admin/", admin.site.urls),
    url(r"passes/", include("parkpasses.components.passes.urls")),
    url(r"parks/", include("parkpasses.components.parks.urls")),
    url(r"concessions/", include("parkpasses.components.concessions.urls")),
    url(r"discount-codes/", include("parkpasses.components.discount_codes.urls")),
    url(r"vouchers/", include("parkpasses.components.vouchers.urls")),
    url(r"cart/", include("parkpasses.components.cart.urls")),
    url(r"help/", include("parkpasses.components.help.urls")),
    url(r"api/", include(api_patterns)),
    url(r"^$", views.ParkPassesRoutingView.as_view(), name="home"),
    url(r"^contact/", views.ParkPassesContactView.as_view(), name="ds_contact"),
    url(
        r"^further_info/",
        views.ParkPassesFurtherInformationView.as_view(),
        name="ds_further_info",
    ),
    url(r"^internal/", views.InternalView.as_view(), name="internal"),
    url(r"^external/", views.ExternalView.as_view(), name="external"),
    url(r"^account/$", views.ExternalView.as_view(), name="manage-account"),
    url(r"^profiles/", views.ExternalView.as_view(), name="manage-profiles"),
    url(
        r"^mgt-commands/$", views.ManagementCommandsView.as_view(), name="mgt-commands"
    ),
] + ledger_patterns


if settings.DEBUG:  # Serve media locally in development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += [
        # ...
        path("__debug__/", include("debug_toolbar.urls")),
    ]
