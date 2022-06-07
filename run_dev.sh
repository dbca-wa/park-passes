#!/bin/bash

# copy pre-commit hook from git_hooks/
cp git_hooks/pre-commit .git/hooks

poetry run python manage.py runserver $1
