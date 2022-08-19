#!/usr/bin/env python3
import os
import sys

import confy

dot_env = os.path.join(os.getcwd(), ".env")

if os.path.exists(dot_env):
    confy.read_environment_file(dot_env)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "parkpasses.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
