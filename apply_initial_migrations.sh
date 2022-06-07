#!/bin/bash
poetry run python manage.py migrate auth &&
poetry run python manage.py migrate ledger_api_client &&

# patch admin 0001_initial migration file
POETRY_ENV=$(poetry env info -p)
echo "POETRY_ENV"
echo $POETRY_ENV
if [ $POETRY_ENV ]; then
    patch .venv/lib/python3.8/site-packages/django/contrib/admin/migrations/0001_initial.py < 0001_initial.py.patch1 &&
    status=$?
    if [ $status -ne 0  ]; then
          echo "Migration patch filed: $status"
            exit $status
        fi
else
    echo "no venv"
    patch /usr/local/lib/python3.8/dist-packages/django/contrib/admin/migrations/0001_initial.py < 0001_initial.py.patch1 &&
    status=$?
    if [ $status -ne 0  ]; then
          echo "Migration patch filed: $status"
            exit $status
        fi
fi

poetry run python manage.py migrate admin &&

# repatch admin 0001_initial migration file
if [ $POETRY_ENV ]; then
    echo $POETRY_ENV
    patch .venv/lib/python3.8/site-packages/django/contrib/admin/migrations/0001_initial.py < 0001_initial.py.patch2 &&
    status=$?
    if [ $status -ne 0  ]; then
          echo "Migration patch filed: $status"
            exit $status
        fi
else
    echo "no venv"
    patch /usr/local/lib/python3.8/dist-packages/django/contrib/admin/migrations/0001_initial.py < 0001_initial.py.patch2 &&
    status=$?
    if [ $status -ne 0  ]; then
          echo "Migration patch filed: $status"
            exit $status
        fi
fi

poetry run python manage.py migrate django_cron &&
poetry run python manage.py migrate sites 0001_initial &&
poetry run python manage.py migrate flatpages 0001_initial &&
poetry run python manage.py migrate sites 0002_alter_domain_unique &&
poetry run python manage.py migrate sessions &&
poetry run python manage.py migrate &&
poetry run python manage.py dbshell -- -c 'ALTER TABLE django_admin_log RENAME COLUMN "user" TO "user_id";'
