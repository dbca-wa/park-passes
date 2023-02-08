#!/bin/bash
POETRY_ENV=$(poetry env info -p)
if [ $POETRY_ENV ]; then
    RUN_PYTHON="poetry run python"
else
    RUN_PYTHON="python"
fi
$RUN_PYTHON manage.py migrate auth &&
$RUN_PYTHON manage.py migrate ledger_api_client &&

# patch admin 0001_initial migration file
echo "POETRY_ENV"
echo $POETRY_ENV
if [ $POETRY_ENV ]; then
    patch .venv/lib/python3.10/site-packages/django/contrib/admin/migrations/0001_initial.py < 0001_initial.py.patch1 &&
    status=$?
    if [ $status -ne 0  ]; then
          echo "Migration patch filed: $status"
            exit $status
        fi
else
    echo "no venv"
    patch /usr/local/lib/python3.10/dist-packages/django/contrib/admin/migrations/0001_initial.py < 0001_initial.py.patch1 &&
    status=$?
    if [ $status -ne 0  ]; then
          echo "Migration patch filed: $status"
            exit $status
        fi
fi

$RUN_PYTHON manage.py migrate admin &&

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

$RUN_PYTHON manage.py migrate django_cron &&
$RUN_PYTHON manage.py migrate sites 0001_initial &&
$RUN_PYTHON manage.py migrate sites 0002_alter_domain_unique &&
$RUN_PYTHON manage.py migrate sessions &&
$RUN_PYTHON manage.py migrate
if [ $POETRY_ENV ]; then
    ECHO 'ALTER TABLE django_admin_log RENAME COLUMN "user" TO "user_id";' | $RUN_PYTHON manage.py dbshell
else
    ECHO 'ALTER TABLE django_admin_log RENAME COLUMN "user" TO "user_id";' | python manage.py dbshell
fi
