# Prepare the base environment.
FROM ubuntu:20.04 as builder_base_oim_parkpasses

LABEL maintainer="asi@dbca.wa.gov.au"

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
ENV SITE_PREFIX='parkpass-dev'
ENV SITE_DOMAIN='dbca.wa.gov.au'
ENV OSCAR_SHOP_NAME='Parks & Wildlife'
ENV BPAY_ALLOWED=False
ARG BRANCH_ARG
ARG REPO_ARG
ARG REPO_NO_DASH_ARG
ENV BRANCH=$BRANCH_ARG
ENV REPO=$REPO_ARG
ENV REPO_NO_DASH=$REPO_NO_DASH_ARG

RUN apt-get clean
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install --no-install-recommends -y curl wget git libmagic-dev gcc binutils libproj-dev gdal-bin
RUN apt-get -y install ca-certificates
RUN apt-get install --no-install-recommends -y vim postgresql-client htop libspatialindex-dev
RUN apt-get install --no-install-recommends -y python3-setuptools python3-dev python3-pip tzdata cron rsyslog python3.8-venv gunicorn
RUN apt-get install --no-install-recommends -y libpq-dev patch
RUN apt-get install --no-install-recommends -y postgresql-client mtr
RUN apt-get install --no-install-recommends -y python-pil
RUN apt-get install --no-install-recommends -y libreoffice
RUN update-ca-certificates
# install node 16
RUN touch install_node.sh
RUN curl -fsSL https://deb.nodesource.com/setup_16.x -o install_node.sh
RUN chmod +x install_node.sh && ./install_node.sh
RUN apt-get install -y nodejs
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip install --upgrade pip

WORKDIR /app
RUN git clone -v -b $BRANCH https://github.com/dbca-wa/$REPO.git .

ENV POETRY_VERSION=1.1.13
RUN pip install "poetry==$POETRY_VERSION"
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

WORKDIR $REPO_NO_DASH/frontend/$REPO_NO_DASH/
RUN npm install --omit=dev
RUN npm run build
RUN rm -rf node_modules/

WORKDIR /app
RUN touch /app/.env
RUN python manage.py collectstatic --no-input
RUN git log --pretty=medium -30 > ./git_history_recent

# Install the project (ensure that frontend projects have been built prior to this step).
COPY ./timezone /etc/timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Patch also required on local environments after a venv rebuild
# (in local) patch /home/<username>/park-passes/.venv/lib/python3.8/site-packages/django/contrib/admin/migrations/0001_initial.py admin.patch.additional
RUN patch /usr/local/lib/python3.8/dist-packages/django/contrib/admin/migrations/0001_initial.py /app/admin.patch.additional

RUN touch /app/rand_hash
COPY ./cron /etc/cron.d/dockercron
RUN service rsyslog start
RUN chmod 0644 /etc/cron.d/dockercron
RUN crontab /etc/cron.d/dockercron
RUN touch /var/log/cron.log
RUN service cron start
COPY ./startup.sh /
RUN chmod 755 /startup.sh
EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/startup.sh"]
