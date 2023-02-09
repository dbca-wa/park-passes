# syntax = docker/dockerfile:1.2

# Prepare the base environment.
FROM ubuntu:22.04 as builder_base_oim_parkpasses

LABEL maintainer="asi@dbca.wa.gov.au"

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Australia/Perth
ENV EMAIL_HOST="emailserver"
ENV DEFAULT_FROM_EMAIL='no-reply@dbca.wa.gov.au'
ENV NON_PROD_EMAIL='none@none.com'
ENV PRODUCTION_EMAIL=False
ENV EMAIL_INSTANCE='DEV'
ENV SECRET_KEY="ThisisNotRealKey"
ENV OSCAR_SHOP_NAME='Park Passes'
ENV BPAY_ALLOWED=False

# Use Australian Mirrors
RUN sed 's/archive.ubuntu.com/au.archive.ubuntu.com/g' /etc/apt/sources.list > /etc/apt/sourcesau.list
RUN mv /etc/apt/sourcesau.list /etc/apt/sources.list
# Use Australian Mirrors

# Stop docker removing the cached os level packages
RUN rm -f /etc/apt/apt.conf.d/docker-clean

RUN --mount=type=cache,target=/var/cache/apt apt-get clean && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install --no-install-recommends -y curl wget git libmagic-dev gcc binutils libproj-dev gdal-bin vim postgresql-client htop libspatialindex-dev \
	    python3-setuptools python3-dev python3-pip tzdata cron rsyslog gunicorn libpq-dev patch postgresql-client mtr python3-pil libreoffice ttf-mscorefonts-installer ca-certificates

# Flush the font cache
RUN fc-cache -vr

RUN update-ca-certificates

# install node 16
RUN touch install_node.sh
RUN curl -fsSL https://deb.nodesource.com/setup_16.x -o install_node.sh
RUN chmod +x install_node.sh && ./install_node.sh
RUN apt-get install -y nodejs
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip install --upgrade pip

WORKDIR /app
COPY parkpasses ./parkpasses
COPY gunicorn.ini manage.py 0001_initial.py.patch1 0001_initial.py.patch2 apply_initial_migrations.sh ./
ENV POETRY_VERSION=1.2.1
RUN pip install "poetry==$POETRY_VERSION"
RUN poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-interaction --no-ansi
RUN rm -rf /var/lib/{apt,dpkg,cache,log}/ /tmp/* /var/tmp/*
RUN cd /app/parkpasses/frontend/parkpasses; npm install --omit=dev
RUN cd /app/parkpasses/frontend/parkpasses; npm run build

#WORKDIR /app
RUN touch /app/.env
RUN python manage.py collectstatic --no-input
COPY .git ./.git

# Install the project (ensure that frontend projects have been built prior to this step).
COPY timezone /etc/timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN touch /app/rand_hash
COPY cron /etc/cron.d/dockercron
RUN chmod 0644 /etc/cron.d/dockercron
RUN crontab /etc/cron.d/dockercron
RUN touch /var/log/cron.log
RUN service cron start

COPY ./startup.sh /
RUN chmod 755 /startup.sh
EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/startup.sh"]
