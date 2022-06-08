# Prepare the base environment.
FROM ubuntu:20.04 as builder_base_parkpasses
MAINTAINER asi@dbca.wa.gov.au

ENV DEBIAN_FRONTEND=noninteractive
#ENV DEBUG=True
ENV TZ=Australia/Perth
ENV EMAIL_HOST="smtp.corporateict.domain"
ENV DEFAULT_FROM_EMAIL='no-reply@dbca.wa.gov.au'
ENV NOTIFICATION_EMAIL='oak.mcilwain@dbca.wa.gov.au'
ENV NON_PROD_EMAIL='none@none.com'
ENV PRODUCTION_EMAIL=False
ENV EMAIL_INSTANCE='DEV'
ENV SECRET_KEY="ThisisNotRealKey"
ENV SITE_PREFIX='lals-dev'
ENV SITE_DOMAIN='dbca.wa.gov.au'
ENV OSCAR_SHOP_NAME='Parks & Wildlife'
ENV BPAY_ALLOWED=False

RUN apt-get clean
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install --no-install-recommends -y wget git libmagic-dev gcc binutils libproj-dev gdal-bin
RUN apt-get install --no-install-recommends -y python3-setuptools python3-dev python3-pip tzdata libreoffice cron rsyslog python3.8-venv gunicorn
RUN apt-get install --no-install-recommends -y libpq-dev patch
RUN apt-get install --no-install-recommends -y postgresql-client mtr
RUN apt-get install --no-install-recommends -y sqlite3 vim postgresql-client ssh htop libspatialindex-dev
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip install --upgrade pip

WORKDIR /app
ENV POETRY_VERSION=1.1.13
RUN pip install "poetry==$POETRY_VERSION"
RUN python -m venv /venv
COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

# Install Python libs from requirements.txt.
COPY git_history_recent ./
RUN touch /app/rand_hash

# Install the project (ensure that frontend projects have been built prior to this step).
COPY timezone /etc/timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Patch also required on local environments after a venv rebuild
# (in local) patch /home/<username>/park-passes/.venv/lib/python3.8/site-packages/django/contrib/admin/migrations/0001_initial.py admin.patch.additional
COPY admin.patch.additional /app/
RUN patch /usr/local/lib/python3.8/dist-packages/django/contrib/admin/migrations/0001_initial.py /app/admin.patch.additional
RUN rm /app/admin.patch.additional

# required for first time db setup
COPY 0001_initial.py.patch1 /app/
COPY 0001_initial.py.patch2 /app/
COPY apply_initial_migrations.sh /app/

COPY cron /etc/cron.d/dockercron
COPY startup.sh /
RUN service rsyslog start
RUN chmod 0644 /etc/cron.d/dockercron
RUN crontab /etc/cron.d/dockercron
RUN touch /var/log/cron.log
RUN service cron start
RUN chmod 755 /startup.sh
COPY gunicorn.ini manage.py ./
RUN touch /app/.env
COPY parkpasses ./parkpasses
#RUN mkdir /app/parkpasses/cache/
#RUN chmod 777 /app/parkpasses/cache/
#RUN poetry run python manage.py collectstatic --no-input
RUN python manage.py collectstatic --noinput
RUN apt-get install --no-install-recommends -y python-pil
EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/startup.sh"]
#CMD ["gunicorn", "parkstay.wsgi", "--bind", ":8080", "--config", "gunicorn.ini"]

