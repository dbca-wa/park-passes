# Park Passes
Online sales for park passes for Western Australian national parks.

# Requirements and installation

- Python (3.8.x)
- PostgreSQL (>=11)
- Node JS (>=16)

Python library requirements should be installed using Python Poetry:

To install Poetry, issue these commands:

`sudo apt install python3-venv`
`sudo pip install poetry`

# Development Environment

## Django app
In the root of the cloned repository, `poetry install` will create a .venv folder similar to virtualenv.

A convenience script `manage.sh` is available so that you can run any django command without
having to type 'poetry run python manage.py' before the command:

e.g.    ./manage.sh runserver 8010
        ./manage.sh collectstatic
        etc.

## Ledger
A Ledger server must be run prior to the Park Passes Django application.

The `LEDGER_API_URL` env var assumes that the server will be run with no port specified, i.e. using the default port 8000.

The db listed by the `LEDGER_DATABASE_URL` env var holds user, organisation and other corporate data.
Creating a new user or changing a user password must be done in the Ledger app/db.

## Vue JS
- also see README.md in frontend root

The following assumes you have navigated to the `parkpasses/frontend/parkpasses` folder.

This folder has a package.json file which has the list of packages and rules for installing them
plus commands on to build the software and start the dev server.

If a package-lock.json exists, npm install will use those exact package versions when installing. It's
very important to retain this file especially for legacy projects as installing updated packages may
break the build.

In the root folder, install packages with `npm install`.

While in development you should use the dev server because it has live reloading which will speed up
development time drastically.

To run the dev server type `npm run serve`

When you would like to test how the project will perform in production you need to run a build.

Kill the dev server with ctrl-c and then,

Type: `npm run build` to build the software and move the output files to `parkpasses/static/parkpasses_vue`

The build files are made available to the Django app in production when `./manage.sh collectstatic` is run.

# Environment variables

A `.env` file should be created in the project root and used to set
required environment variables at run time. Example content:

    DEBUG=True
    SECRET_KEY='thisismysecret'
    DATABASE_URL='postgis://user:pw@localhost:port/db_name'
    EMAIL_HOST='SMTP_HOST'
    BPOINT_USERNAME='BPOINT_USER'
    BPOINT_PASSWORD='BPOINT_PW
    BPOINT_BILLER_CODE='1234567'
    BPOINT_MERCHANT_NUM='BPOINT_MERCHANT_NUM'
    BPAY_BILLER_CODE='987654'
    PAYMENT_OFFICERS_GROUP='PAYMENT_GROUP'
    DEFAULT_FROM_EMAIL='FROM_EMAIL_ADDRESS'
    NOTIFICATION_EMAIL='NOTIF_RECIPIENT_1, NOTIF_RECIPIENT_2'
    NON_PROD_EMAIL='NON_PROD_RECIPIENT_1, NON_PROD_RECIPIENT_2'
    EMAIL_INSTANCE='DEV'
    PRODUCTION_EMAIL=False
    BPAY_ALLOWED=False
    SITE_PREFIX='prefix'
    SITE_DOMAIN='SITE_DOMAIN'
    LEDGER_GST=10
    DISABLE_EMAIL=True
    DJANGO_HTTPS=True
    CRON_NOTIFICATION_EMAIL='email'
    ENABLE_DJANGO_LOGIN=True
    OSCAR_SHOP_NAME='shop_name'
    LEDGER_DATABASE_URL='postgis://user:pw@localhost:port/db_name'
    LEDGER_API_URL="http://localhost:8000"
    LEDGER_API_KEY="API_KEY"
    # Below is required to run Vue Js front end with hot reload
    DEV_APP_BUILD_URL="http://localhost:8080/static/parkpassesapp.js"
    # Below prints emails to screen instead of sending via mail server
    CONSOLE_EMAIL_BACKEND=True
