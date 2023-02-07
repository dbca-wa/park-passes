import hashlib
import logging
import os

import confy
import dj_database_url
from confy import env

logger = logging.getLogger(__name__)


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
confy.read_environment_file(BASE_DIR + "/.env")
os.environ.setdefault("BASE_DIR", BASE_DIR)

from ledger_api_client.settings_base import *  # noqa: F403

if DEBUG:
    ADMINS = [
        ("Oak McIlwain", "oak.mcilwain@dbca.wa.gov.au"),
    ]
else:
    ADMINS = [
        ("ASI", "asi@dpaw.wa.gov.au"),
    ]

ROOT_URLCONF = "parkpasses.urls"
SITE_ID = 1
DEPT_DOMAINS = env("DEPT_DOMAINS", ["dpaw.wa.gov.au", "dbca.wa.gov.au"])
SYSTEM_MAINTENANCE_WARNING = env("SYSTEM_MAINTENANCE_WARNING", 24)  # hours
DISABLE_EMAIL = env("DISABLE_EMAIL", False)
SHOW_TESTS_URL = env("SHOW_TESTS_URL", False)
SHOW_DEBUG_TOOLBAR = env("SHOW_DEBUG_TOOLBAR", False)

BUILD_TAG = env(
    "BUILD_TAG", hashlib.sha256(os.urandom(32)).hexdigest()
)  # URL of the Dev app.js served by webpack & express

TIME_ZONE = "Australia/Perth"

STATIC_URL = "/static/"


INSTALLED_APPS += [
    "webtemplate_dbca",
    "rest_framework",
    "rest_framework_datatables",
    "django_filters",
    "colorfield",
    "rest_framework_gis",
    "ledger_api_client",
    "ckeditor",
    "org_model_documents",
    "org_model_logs",
    "parkpasses",
    "parkpasses.components.retailers",
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
    "parkpasses.components.emails",
    "parkpasses.components.reports",
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
    "DEFAULT_FILTER_BACKENDS": (
        # "rest_framework_datatables.filters.DatatablesFilterBackend",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework_datatables.pagination.DatatablesPageNumberPagination",
    "PAGE_SIZE": 20,
    "SEARCH_PARAM": "search[value]",
}


MIDDLEWARE_CLASSES += [
    "whitenoise.middleware.WhiteNoiseMiddleware",
]
MIDDLEWARE = MIDDLEWARE_CLASSES
MIDDLEWARE_CLASSES = None

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"


if DEBUG and SHOW_DEBUG_TOOLBAR:

    def show_toolbar(request):
        if request:
            return True

    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
    # KOLO_PATH = "./manage.sh runserver 8010"
    INSTALLED_APPS += ("debug_toolbar",)
    INTERNAL_IPS = ("127.0.0.1", "localhost")

    # this dict removes check to dtermine if toolbar should display --> works for rks docker container
    DEBUG_TOOLBAR_CONFIG = {
        # "SHOW_TOOLBAR_CALLBACK": show_toolbar,
        "INTERCEPT_REDIRECTS": False,
    }

SILENCED_SYSTEM_CHECKS = ["fields.W903", "fields.W904", "debug_toolbar.W004"]

TEMPLATES[0]["DIRS"].append(os.path.join(BASE_DIR, "parkpasses", "templates"))
TEMPLATES[0]["DIRS"].append(
    os.path.join(BASE_DIR, "parkpasses", "components", "emails", "templates")
)
USE_DUMMY_CACHE = env("USE_DUMMY_CACHE", False)
if USE_DUMMY_CACHE:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        },
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": os.path.join(BASE_DIR, "parkpasses", "cache"),
        },
    }

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS.extend(
    [
        os.path.join(os.path.join(BASE_DIR, "parkpasses", "static")),
    ]
)

DATA_UPLOAD_MAX_NUMBER_FIELDS = None

TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    "parkpasses.context_processors.parkpasses_url"
)

# Department details
SYSTEM_NAME = env("SYSTEM_NAME", "Park Passes")
SYSTEM_NAME_SHORT = env("SYSTEM_NAME_SHORT", "PP")

SITE_PREFIX = env("SITE_PREFIX", "")
SITE_DOMAIN = env("SITE_DOMAIN", "dbca.wa.gov.au")
PARKPASSES_EXTERNAL_URL = env("PARKPASSES_EXTERNAL_URL")

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
BRANCH_NAME = env("BRANCH_NAME", "Park Passes Branch")
DEP_ADDRESS = env("DEP_ADDRESS", "17 Dick Perry Avenue, Kensington WA 6151")
if DEBUG is True:
    SITE_URL = env("SITE_URL", "http://" + SITE_DOMAIN)
else:
    SITE_URL = env("SITE_URL", "https://" + SITE_PREFIX + "." + SITE_DOMAIN)
PUBLIC_URL = env("PUBLIC_URL", SITE_URL)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "no-reply@" + SITE_DOMAIN).lower()
MEDIA_APP_DIR = env("MEDIA_APP_DIR", "cols")


""" ==================== SYSTEM GROUP NAMES ======================== """

ADMIN_GROUP = env("ADMIN_GROUP", "Park Passes Admin")
OFFICER_GROUP = env("OFFICER_GROUP", "Park Passes Officer")
PAYMENTS_OFFICER_GROUP = env("PAYMENTS_OFFICER_GROUP", "Park Passes Payments Officer")
READ_ONLY_GROUP = env("READ_ONLY_GROUP", "Park Passes Read-Only Group")
DISCOUNT_CODE_PERCENTAGE_GROUP = env(
    "DISCOUNT_CODE_PERCENTAGE_GROUP", "Park Passes Discount Code Percentage Creator"
)


CRON_RUN_AT_TIMES = env("CRON_RUN_AT_TIMES", "04:05")
CRON_EMAIL = env("CRON_EMAIL", "cron@" + SITE_DOMAIN).lower()
NO_REPLY_EMAIL = env("NO_REPLY_EMAIL", "no-reply@" + SITE_DOMAIN).lower()
# for ORACLE Job Notification - override settings_base.py
EMAIL_FROM = DEFAULT_FROM_EMAIL
OTHER_PAYMENT_ALLOWED = env("OTHER_PAYMENT_ALLOWED", False)  # Cash/Cheque


os.environ[
    "LEDGER_PRODUCT_CUSTOM_FIELDS"
] = "('ledger_description','quantity','price_incl_tax','price_excl_tax','oracle_code')"

if NOTIFICATION_EMAIL is not None:
    CRON_NOTIFICATION_EMAIL = env("CRON_NOTIFICATION_EMAIL", NOTIFICATION_EMAIL).lower()


CRON_CLASSES = [
    "parkpasses.cron.OracleIntegrationCronJob",
]

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

CRON_EMAIL_FILE_NAME = "cron_email.log"

# Add a debug level logger for development
if DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "verbose": {
                "format": "%(levelname)s %(asctime)s %(name)s [Line:%(lineno)s][%(funcName)s] %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
            },
            "parkpasses_rotating_file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(BASE_DIR, "logs", "parkpasses.log"),
                "formatter": "verbose",
                "maxBytes": 5242880,
            },
            "org_model_documents_rotating_file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(BASE_DIR, "logs", "org_model_documents.log"),
                "formatter": "verbose",
                "maxBytes": 5242880,
            },
            "org_model_logs_rotating_file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(BASE_DIR, "logs", "org_model_logs.log"),
                "formatter": "verbose",
                "maxBytes": 5242880,
            },
            "mail_admins": {
                "level": "ERROR",
                "class": "django.utils.log.AdminEmailHandler",
                "include_html": True,
            },
        },
        "loggers": {
            "parkpasses": {
                "handlers": ["console", "parkpasses_rotating_file", "mail_admins"],
                "level": "DEBUG",
                "propagate": False,
            },
            "org_model_documents": {
                "handlers": ["console", "org_model_documents_rotating_file"],
                "level": "DEBUG",
                "propagate": False,
            },
            "org_model_logs": {
                "handlers": ["console", "org_model_logs_rotating_file"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }
else:
    LOGGING["formatters"]["verbose"] = {
        "format": "%(levelname)s %(asctime)s %(name)s [Line:%(lineno)s][%(funcName)s] %(message)s"
    }
    LOGGING["handlers"]["parkpasses_rotating_file"] = {
        "level": "INFO",
        "class": "logging.handlers.RotatingFileHandler",
        "filename": os.path.join(BASE_DIR, "logs", "parkpasses.log"),
        "formatter": "verbose",
        "maxBytes": 5242880,
    }
    LOGGING["handlers"]["org_model_documents_rotating_file"] = {
        "level": "INFO",
        "class": "logging.handlers.RotatingFileHandler",
        "filename": os.path.join(BASE_DIR, "logs", "org_model_documents.log"),
        "formatter": "verbose",
        "maxBytes": 5242880,
    }
    LOGGING["handlers"]["org_model_logs_rotating_file"] = {
        "level": "INFO",
        "class": "logging.handlers.RotatingFileHandler",
        "filename": os.path.join(BASE_DIR, "logs", "org_model_logs.log"),
        "formatter": "verbose",
        "maxBytes": 5242880,
    }
    LOGGING["handlers"]["mail_admins"] = {
        "level": "WARNING",
        "class": "django.utils.log.AdminEmailHandler",
    }
    LOGGING["loggers"]["parkpasses"] = {
        "handlers": ["console", "parkpasses_rotating_file", "mail_admins"],
        "level": "INFO",
    }
    LOGGING["loggers"]["org_model_documents"] = {
        "handlers": ["org_model_documents_rotating_file", "mail_admins"],
        "level": "INFO",
    }
    LOGGING["loggers"]["org_model_logs"] = {
        "handlers": ["org_model_logs_rotating_file", "mail_admins"],
        "level": "INFO",
    }

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

LOV_CACHE_TIMEOUT = 10800

CACHE_TIMEOUT_2_HOURS = 60 * 60 * 2  # 2 HOURS
CACHE_TIMEOUT_24_HOURS = 60 * 60 * 24  # 24 HOURS

CACHE_KEY_EMAIL_USER = "email-user-{}"

CACHE_KEY_BELONGS_TO = "user-{}-is-a-member-of-{}"
CACHE_KEY_IS_INTERNAL = "user-{}-is-internal"
CACHE_KEY_RETAILER = "user-{}-is-a-retailer"
CACHE_KEY_RETAILER_ADMIN = "user-{}-is-a-retailer-admin"
CACHE_KEY_RETAILER_GROUP_IDS = "user-{}-retailer-group-ids"

CACHE_KEY_GROUP_IDS = "{}-{}-user-ids"

CACHE_KEY_LEDGER_ORGANISATION = "ledger-organisation-{}"

CACHE_SYSTEM_CHECK_FOR = 60  # 1 minute

PROTECTED_MEDIA_ROOT = env(
    "PROTECTED_MEDIA_ROOT", os.path.join(BASE_DIR, "protected_media")
)

RETAILER_GROUP_INVOICE_ROOT = env(
    "RETAILER_GROUP_INVOICE_ROOT", PROTECTED_MEDIA_ROOT + "/retailer_group_invoices"
)

RETAILER_GROUP_REPORT_ROOT = env(
    "RETAILER_GROUP_REPORT_ROOT", PROTECTED_MEDIA_ROOT + "/retailer_group_reports"
)

PICA_GOLD_STAR_PASS_ROOT = env(
    "RETAILER_GROUP_REPORT_ROOT", PROTECTED_MEDIA_ROOT + "/pica_gold_star_pass"
)

PICA_EMAIL = env("PICA_EMAIL", None)

UNENTERED_ORACLE_CODE_LABEL = "You must enter a real oracle code here!"

PICA_ORACLE_CODE_LABEL = "PICA (Online Sales)"

ORG_MODEL_DOCUMENTS_MEDIA_ROOT = env(
    "ORG_MODEL_DOCUMENTS_MEDIA_ROOT", "protected_media"
)

APPLICATION_TYPE_PARK_PASSES = "park_passes"
APPLICATION_TYPES = [
    (APPLICATION_TYPE_PARK_PASSES, "Park Passes"),
]

GROUP_NAME_PARK_PASSES_RETAILER = "Park Passes Retailer"

RETAILER_INVOICE_DUE_DAYS = 30

template_title = "Park Passes"
template_group = "parkpasses"

# Use git commit hash for purging cache in browser for deployment changes
GIT_COMMIT_HASH = ""
GIT_COMMIT_DATE = ""
if os.path.isdir(BASE_DIR + "/.git/") is True:
    GIT_COMMIT_DATE = os.popen("cd " + BASE_DIR + " ; git log -1 --format=%cd").read()
    GIT_COMMIT_HASH = os.popen("cd  " + BASE_DIR + " ; git log -1 --format=%H").read()
if len(GIT_COMMIT_HASH) == 0:
    GIT_COMMIT_HASH = os.popen("cat /app/git_hash").read()
    if len(GIT_COMMIT_HASH) == 0:
        print("ERROR: No git hash provided")

LEDGER_TEMPLATE = "bootstrap5"

LEDGER_UI_CARDS_MANAGEMENT = True

ORGANISATION = {
    "name": "Department of Biodiversity, Conservation and Attractions",
    "address_line_1": "17 Dick Perry Ave",
    "address_line_2": "",
    "suburb": "Kensington",
    "state": "WA",
    "postcode": "6151",
    "ABN": "38 052 249 024",
}

HOLIDAY_PASS = "HOLIDAY_PASS"
ANNUAL_LOCAL_PASS = "ANNUAL_LOCAL_PASS"
ALL_PARKS_PASS = "ALL_PARKS_PASS"
GOLD_STAR_PASS = "GOLD_STAR_PASS"
DAY_ENTRY_PASS = "DAY_ENTRY_PASS"
PINJAR_OFF_ROAD_VEHICLE_AREA_ANNUAL_PASS = "PINJAR_OFF_ROAD_VEHICLE_AREA_ANNUAL_PASS"
PERSONNEL_PASS = "PERSONNEL_PASS"

PASS_TYPES = [
    (HOLIDAY_PASS, "Holiday Pass"),
    (ANNUAL_LOCAL_PASS, "Annual Local Pass"),
    (ALL_PARKS_PASS, "All Park Pass"),
    (GOLD_STAR_PASS, "Gold Star Pass"),
    (DAY_ENTRY_PASS, "Day Entry Pass"),
    (
        PINJAR_OFF_ROAD_VEHICLE_AREA_ANNUAL_PASS,
        "Pinjar Off Road Vehicle Area Annual Pass",
    ),
    (PERSONNEL_PASS, "Personnel Pass"),
]

PASS_TEMPLATE_REPLACEMENT_IMAGE_PATH = "word/media/image2.png"
PASS_TEMPLATE_DEFAULT_IMAGE_PATH = (
    f"{STATIC_ROOT}/parkpasses/img/default-pass-template-image.png"
)

PASS_VEHICLE_REGO_REMINDER_DAYS_PRIOR = 7
PASS_REMINDER_DAYS_PRIOR = 7

PRICING_WINDOW_DEFAULT_NAME = "Default"

RAC_DISCOUNT_PERCENTAGE = env("RAC_DISCOUNT_PERCENTAGE", 50)


UNLIMITED_USES = 999999999
UNLIMITED_USES_TEXT = "Unlimited"

USE_DUMMY_QR_CODE_DATA = env("USE_DUMMY_QR_CODE_DATA", True)

""" ==================== USER ACTIONS ======================== """


ACTION_VIEW = "View {} {}"
ACTION_LIST = "List {} {}"
ACTION_CREATE = "Create {} {}"
ACTION_UPDATE = "Update {} {}"
ACTION_PARTIAL_UPDATE = "Partial Update {} {}"
ACTION_DESTROY = "Destroy {} {}"
ACTION_CANCEL = "Cancel {} {}"
ACTION_INVALIDATE = "Invalidate {} {}"


PARKPASSES_VOUCHER_EXPIRY_IN_DAYS = 365 * 2

PARKPASSES_VALID_CART_CONTENT_TYPES = [
    "parkpasses | voucher",
    "parkpasses | pass",
]

""" ==================== DEFAULT DATA CONFIGS ======================== """

PARKPASSES_DEFAULT_SOLD_VIA = "DBCA Website"
PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID = env(
    "PARKPASSES_DEFAULT_SOLD_VIA_ORGANISATION_ID"
)

RAC_RETAILER_GROUP_ORGANISATION_ID = env("RAC_RETAILER_GROUP_ORGANISATION_ID")

DATABASES["test"] = dj_database_url.config(env="TEST_DATABASE_URL")

LOGIN_URL = "/ssologin"

PARKPASSES_PAYMENT_SYSTEM_ID = env("PARKPASSES_PAYMENT_SYSTEM_ID", "S385")

# missing

PARKPASSES_PAYMENT_SYSTEM_PREFIX = env(
    "PARKPASSES_PAYMENT_SYSTEM_PREFIX", PARKPASSES_PAYMENT_SYSTEM_ID.replace("S", "0")
)  # '0385'

if not VALID_SYSTEMS:
    VALID_SYSTEMS = [PARKPASSES_PAYMENT_SYSTEM_ID]

""" ==================== LEDGER DESCRIPTIONS ======================== """

PARKPASSES_LEDGER_DEFAULT_LINE_STATUS = 1

PARKPASSES_VOUCHER_PURCHASE_DESCRIPTION = "Voucher Purchase:"
PARKPASSES_PASS_PURCHASE_DESCRIPTION = "Park Pass Purchase:"

PARKPASSES_RAC_DISCOUNT_APPLIED_DESCRIPTION = "RAC Discount Applied:"
PARKPASSES_CONCESSION_APPLIED_DESCRIPTION = "Concession Discount:"
PARKPASSES_DISCOUNT_CODE_APPLIED_DESCRIPTION = "Discount Code Applied:"
PARKPASSES_VOUCHER_CODE_REDEEMED_DESCRIPTION = "Voucher Code Redeemed:"

PARKPASSES_DEFAULT_ORACLE_CODE = "PARKPASSES_DEFAULT_ORACLE_CODE"
PARKPASSES_DEFAULT_VOUCHER_ORACLE_CODE = "PARKPASSES_DEFAULT_VOUCHER_ORACLE_CODE"

LEDGER_UI_ACCOUNTS_MANAGEMENT = [
    {"first_name": {"options": {"view": True, "edit": True}}},
    {"last_name": {"options": {"view": True, "edit": True}}},
    {"residential_address": {"options": {"view": True, "edit": True}}},
    {"phone_number": {"options": {"view": True, "edit": True}}},
    {"mobile_number": {"options": {"view": True, "edit": True}}},
]


""" ==================== DJANDO Q ======================== """

Q_CLUSTER = {
    "name": "DjangORM",
    "workers": 4,
    "timeout": 90,
    "retry": 120,
    "queue_limit": 50,
    "bulk": 10,
    "orm": "default",
}


""" ==================== CKEDITOR CONFIGS ======================== """

CKEDITOR_CONFIGS = {
    "default": {
        "skin": "moono",
        # 'skin': 'office2013',
        "toolbar_Basic": [["Source", "-", "Bold", "Italic"]],
        "toolbar_YourCustomToolbarConfig": [
            {
                "name": "document",
                "items": [
                    "Source",
                    "-",
                    "Save",
                    "NewPage",
                    "Preview",
                    "Print",
                    "-",
                    "Templates",
                ],
            },
            {
                "name": "clipboard",
                "items": [
                    "Cut",
                    "Copy",
                    "Paste",
                    "PasteText",
                    "PasteFromWord",
                    "-",
                    "Undo",
                    "Redo",
                ],
            },
            # {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
            # {'name': 'forms',
            # 'items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton',
            #           'HiddenField']},
            # '/',
            {
                "name": "basicstyles",
                "items": [
                    "Bold",
                    "Italic",
                    "Underline",
                    "Strike",
                    "Subscript",
                    "Superscript",
                    "-",
                    "RemoveFormat",
                ],
            },
            # {'name': 'paragraph',
            # 'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
            #           'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',
            #           'Language']},
            {"name": "links", "items": ["Link", "Unlink", "Anchor"]},
            # {'name': 'insert',
            # 'items': ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe']},
            # '/',
            {"name": "styles", "items": ["Styles", "Format", "Font", "FontSize"]},
            # {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            # {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
            # {'name': 'about', 'items': ['About']},
            "/",  # put this to force next toolbar on new line
        ],
        "toolbar": "YourCustomToolbarConfig",  # put selected toolbar config here
        # 'toolbarGroups': [{ 'name': 'document', 'groups': [ 'mode', 'document', 'doctools' ] }],
        # 'height': 291,
        # 'width': '100%',
        # 'filebrowserWindowHeight': 725,
        # 'filebrowserWindowWidth': 940,
        # 'toolbarCanCollapse': True,
        # 'mathJaxLib': '//cdn.mathjax.org/mathjax/2.2-latest/MathJax.js?config=TeX-AMS_HTML',
        "tabSpaces": 4,
        "extraPlugins": ",".join(
            [
                "uploadimage",  # the upload image feature
                # your extra plugins here
                "div",
                "autolink",
                "autoembed",
                "embedsemantic",
                "autogrow",
                "widget",
                "lineutils",
                "clipboard",
                "dialog",
                "dialogui",
                "elementspath",
            ]
        ),
    }
}
