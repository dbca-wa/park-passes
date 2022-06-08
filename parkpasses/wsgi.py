"""
WSGI config for ledger project.
It exposes the WSGI callable as a module-level variable named ``application``.
"""
import os

import confy
from django.core.wsgi import get_wsgi_application

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
confy.read_environment_file(BASE_DIR + "/.env")
os.environ.setdefault("BASE_DIR", BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "parkpasses.settings")
application = get_wsgi_application()
