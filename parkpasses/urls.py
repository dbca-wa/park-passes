from django.conf import settings

# from django.contrib import admin
from parkpasses.admin import admin
from django.conf.urls import url, include
from django.urls import path
from django.contrib.auth.views import LogoutView, LoginView

from django.contrib.auth import logout, login  # DEV ONLY

from django.conf.urls.static import static
from rest_framework import routers
from parkpasses import views

from ledger_api_client.urls import urlpatterns as ledger_patterns
from parkpasses.management.default_data_manager import DefaultDataManager
from parkpasses.utils import are_migrations_running

from parkpasses.components.proposals import api as proposal_api
# API patterns
router = routers.DefaultRouter()
router.register(r"proposal", proposal_api.ProposalViewSet)
router.register(r"proposal_paginated", proposal_api.ProposalPaginatedViewSet)

api_patterns = [
    url(r"^api/", include(router.urls)),
]

# URL Patterns
urlpatterns = [
    path(r"admin/", admin.site.urls),
    url(r"", include(api_patterns)),
    url(r"^$", views.LicensingTemplateRoutingView.as_view(), name="home"),
    url(r"^contact/", views.LicensingTemplateContactView.as_view(), name="ds_contact"),
    url(
        r"^further_info/",
        views.LicensingTemplateFurtherInformationView.as_view(),
        name="ds_further_info",
    ),
    url(r"^internal/", views.InternalView.as_view(), name="internal"),
    url(r"^external/", views.ExternalView.as_view(), name="external"),
    url(r"^firsttime/$", views.first_time, name="first_time"),
    url(r"^account/$", views.ExternalView.as_view(), name="manage-account"),
    url(r"^profiles/", views.ExternalView.as_view(), name="manage-profiles"),
    url(
        r"^help/(?P<application_type>[^/]+)/(?P<help_type>[^/]+)/$",
        views.HelpView.as_view(),
        name="help",
    ),
    url(
        r"^mgt-commands/$", views.ManagementCommandsView.as_view(), name="mgt-commands"
    ),
    url(
        r"^api/application_types$",
        proposal_api.GetApplicationTypeDescriptions.as_view(),
        name="get-application-type-descriptions",
    ),
    url(
        r"^api/application_types_dict$",
        proposal_api.GetApplicationTypeDict.as_view(),
        name="get-application-type-dict",
    ),

    url(
        r"^api/application_statuses_dict$",
        proposal_api.GetApplicationStatusesDict.as_view(),
        name="get-application-statuses-dict",
    ),

] + ledger_patterns


if settings.DEBUG:  # Serve media locally in development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not are_migrations_running():
    DefaultDataManager()

# if settings.SHOW_DEBUG_TOOLBAR:
#    import debug_toolbar
#    urlpatterns = [
#        url('__debug__/', include(debug_toolbar.urls)),
#    ] + urlpatterns
