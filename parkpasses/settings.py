import hashlib
import os

import confy
import dj_database_url
from confy import env
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
confy.read_environment_file(BASE_DIR + "/.env")
os.environ.setdefault("BASE_DIR", BASE_DIR)

from ledger_api_client.settings_base import *  # noqa: F403

ROOT_URLCONF = "parkpasses.urls"
SITE_ID = 1
DEPT_DOMAINS = env("DEPT_DOMAINS", ["dpaw.wa.gov.au", "dbca.wa.gov.au"])
SYSTEM_MAINTENANCE_WARNING = env("SYSTEM_MAINTENANCE_WARNING", 24)  # hours
DISABLE_EMAIL = env("DISABLE_EMAIL", False)
SHOW_TESTS_URL = env("SHOW_TESTS_URL", False)
SHOW_DEBUG_TOOLBAR = env("SHOW_DEBUG_TOOLBAR", False)
BUILD_TAG = env(
    "BUILD_TAG", hashlib.md5(os.urandom(32)).hexdigest()
)  # URL of the Dev app.js served by webpack & express


STATIC_URL = "/static/"


INSTALLED_APPS += [
    "webtemplate_dbca",
    "rest_framework",
    "rest_framework_datatables",
    "django_filters",
    "rest_framework_gis",
    "ledger_api_client",
    "ckeditor",
    "org_model_documents",
    "org_model_logs",
    "parkpasses",
    "parkpasses.components.concessions",
    "parkpasses.components.main",
    "parkpasses.components.vouchers",
    "parkpasses.components.parks",
    "parkpasses.components.discount_codes",
    "parkpasses.components.passes",
    "parkpasses.components.cart",
    "parkpasses.components.orders",
    "parkpasses.components.users",
    "parkpasses.components.help",
    "parkpasses.components.retailers",
]

ADD_REVERSION_ADMIN = True

# maximum number of days allowed for a booking
WSGI_APPLICATION = "parkpasses.wsgi.application"


REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
        "rest_framework_datatables.renderers.DatatablesRenderer",
    ),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework_datatables.pagination.DatatablesPageNumberPagination",
    "PAGE_SIZE": 20,
}


MIDDLEWARE_CLASSES += [
    "whitenoise.middleware.WhiteNoiseMiddleware",
]
MIDDLEWARE = MIDDLEWARE_CLASSES
MIDDLEWARE_CLASSES = None

if SHOW_DEBUG_TOOLBAR:

    def show_toolbar(request):
        if request:
            return True

    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
    INSTALLED_APPS += ("debug_toolbar",)
    INTERNAL_IPS = ("127.0.0.1", "localhost")

    # this dict removes check to dtermine if toolbar should display --> works for rks docker container
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": show_toolbar,
        "INTERCEPT_REDIRECTS": False,
    }

TEMPLATES[0]["DIRS"].append(os.path.join(BASE_DIR, "parkpasses", "templates"))
TEMPLATES[0]["DIRS"].append(
    os.path.join(BASE_DIR, "parkpasses", "components", "emails", "templates")
)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": os.path.join(BASE_DIR, "parkpasses", "cache"),
    }
}
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS.extend(
    [
        os.path.join(os.path.join(BASE_DIR, "parkpasses", "static")),
    ]
)
DEV_STATIC = env("DEV_STATIC", False)
DEV_STATIC_URL = env("DEV_STATIC_URL")
if DEV_STATIC and not DEV_STATIC_URL:
    raise ImproperlyConfigured("If running in DEV_STATIC, DEV_STATIC_URL has to be set")
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    "parkpasses.context_processors.parkpasses_template_url"
)

# Department details
SYSTEM_NAME = env("SYSTEM_NAME", "Park Passes")
SYSTEM_NAME_SHORT = env("SYSTEM_NAME_SHORT", "PP")
SITE_PREFIX = env("SITE_PREFIX")
SITE_DOMAIN = env("SITE_DOMAIN")
SUPPORT_EMAIL = env("SUPPORT_EMAIL", "licensing@" + SITE_DOMAIN).lower()
SUPPORT_EMAIL_FILMING = env("SUPPORT_EMAIL_FILMING", "filming@" + SITE_DOMAIN).lower()
DEP_URL = env("DEP_URL", "www." + SITE_DOMAIN)
DEP_PHONE = env("DEP_PHONE", "(08) 9219 9978")
DEP_PHONE_FILMING = env("DEP_PHONE_FILMING", "(08) 9219 8411")
DEP_PHONE_SUPPORT = env("DEP_PHONE_SUPPORT", "(08) 9219 9000")
DEP_FAX = env("DEP_FAX", "(08) 9423 8242")
DEP_POSTAL = env(
    "DEP_POSTAL", "Locked Bag 104, Bentley Delivery Centre, Western Australia 6983"
)
DEP_NAME = env("DEP_NAME", "Department of Biodiversity, Conservation and Attractions")
DEP_NAME_SHORT = env("DEP_NAME_SHORT", "DBCA")
DEP_ADDRESS = env("DEP_ADDRESS", "17 Dick Perry Avenue, Kensington WA 6151")
SITE_URL = env("SITE_URL", "https://" + SITE_PREFIX + "." + SITE_DOMAIN)
PUBLIC_URL = env("PUBLIC_URL", SITE_URL)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "no-reply@" + SITE_DOMAIN).lower()
MEDIA_APP_DIR = env("MEDIA_APP_DIR", "cols")
ADMIN_GROUP = env("ADMIN_GROUP", "LALS Admin")
CRON_RUN_AT_TIMES = env("CRON_RUN_AT_TIMES", "04:05")
CRON_EMAIL = env("CRON_EMAIL", "cron@" + SITE_DOMAIN).lower()
# for ORACLE Job Notification - override settings_base.py
EMAIL_FROM = DEFAULT_FROM_EMAIL
OTHER_PAYMENT_ALLOWED = env("OTHER_PAYMENT_ALLOWED", False)  # Cash/Cheque

OSCAR_BASKET_COOKIE_OPEN = "cols_basket"
PAYMENT_SYSTEM_ID = env("PAYMENT_SYSTEM_ID", "S557")
PAYMENT_SYSTEM_PREFIX = env(
    "PAYMENT_SYSTEM_PREFIX", PAYMENT_SYSTEM_ID.replace("S", "0")
)  # '0557'
os.environ[
    "LEDGER_PRODUCT_CUSTOM_FIELDS"
] = "('ledger_description','quantity','price_incl_tax','price_excl_tax','oracle_code')"
CRON_NOTIFICATION_EMAIL = env("CRON_NOTIFICATION_EMAIL", NOTIFICATION_EMAIL).lower()

if not VALID_SYSTEMS:
    VALID_SYSTEMS = [PAYMENT_SYSTEM_ID]

CRON_CLASSES = [
    "parkpasses.cron.OracleIntegrationCronJob",
]


BASE_URL = env("BASE_URL")

CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
        "height": 300,
        # 'width': 300,
        "width": "100%",
    },
    "awesome_ckeditor": {
        "toolbar": "Basic",
    },
}


CONSOLE_EMAIL_BACKEND = env("CONSOLE_EMAIL_BACKEND", False)
if CONSOLE_EMAIL_BACKEND:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Additional logging for parkpasses
LOGGING["handlers"]["payment_checkout"] = {
    "level": "INFO",
    "class": "logging.handlers.RotatingFileHandler",
    "filename": os.path.join(BASE_DIR, "logs", "cols_payment_checkout.log"),
    "formatter": "verbose",
    "maxBytes": 5242880,
}
LOGGING["loggers"]["payment_checkout"] = {
    "handlers": ["payment_checkout"],
    "level": "INFO",
}
# Add a handler
LOGGING["handlers"]["file_parkpasses"] = {
    "level": "INFO",
    "class": "logging.handlers.RotatingFileHandler",
    "filename": os.path.join(BASE_DIR, "logs", "parkpasses.log"),
    "formatter": "verbose",
    "maxBytes": 5242880,
}

LOGGING["loggers"]["parkpasses"] = {
    "handlers": ["file_parkpasses"],
    "level": "INFO",
}

# Add a debug level logger for development
if DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": True,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "parkpasses": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
DEV_APP_BUILD_URL = env(
    "DEV_APP_BUILD_URL"
)  # URL of the Dev app.js served by webpack & express
LOV_CACHE_TIMEOUT = 10800


APPLICATION_TYPE_PARK_PASSES = "park_passes"
APPLICATION_TYPES = [
    (APPLICATION_TYPE_PARK_PASSES, "Park Passes"),
]
KMI_SERVER_URL = env("KMI_SERVER_URL", "https://kmi.dbca.wa.gov.au")

GROUP_NAME_PARK_PASSES_RETAILER = "Park Passes Retailer"

template_title = "Park Passes"
template_group = "parkswildlife"

HOLIDAY_PASS = "HOLIDAY_PASS"
ANNUAL_LOCAL_PASS = "ANNUAL_LOCAL_PASS"
ALL_PARKS_PASS = "ALL_PARKS_PASS"
GOLD_STAR_PASS = "GOLD_STAR_PASS"
DAY_ENTRY_PASS = "DAY_ENTRY_PASS"

PASS_TYPES = [
    (HOLIDAY_PASS, "Holiday Pass"),
    (ANNUAL_LOCAL_PASS, "Annual Local Pass"),
    (ALL_PARKS_PASS, "All Park Pass"),
    (GOLD_STAR_PASS, "Gold Star Pass"),
    (DAY_ENTRY_PASS, "Day Entry Pass"),
]

COMMUNICATIONS_LOG_ENTRY_CHOICES = [
    ("email", "Email"),
    ("phone", "Phone Call"),
    ("mail", "Mail"),
    ("person", "In Person"),
    ("onhold", "On Hold"),
    ("onhold_remove", "Remove On Hold"),
    ("with_qaofficer", "With QA Officer"),
    ("with_qaofficer_completed", "QA Officer Completed"),
    ("referral_complete", "Referral Completed"),
]

PARKPASSES_VOUCHER_EXPIRY_IN_DAYS = 365 * 2

PARKPASSES_VALID_CART_CONTENT_TYPES = [
    "parkpasses | voucher",
    "parkpasses | pass",
]

DATABASES["test"] = dj_database_url.config(env="TEST_DATABASE_URL")
