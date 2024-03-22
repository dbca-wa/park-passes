# syntax = docker/dockerfile:1.2

# Prepare the base environment.
FROM ubuntu:22.04 as builder_base_oim_parkpasses

LABEL maintainer="asi@dbca.wa.gov.au"

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Australia/Perth \
    EMAIL_HOST="emailserver" \
    DEFAULT_FROM_EMAIL='no-reply@dbca.wa.gov.au' \
    NON_PROD_EMAIL='none@none.com' \
    PRODUCTION_EMAIL=False \
    EMAIL_INSTANCE='DEV' \
    SECRET_KEY="ThisisNotRealKey" \
    OSCAR_SHOP_NAME='Park Passes' \
    BPAY_ALLOWED=False \
    POETRY_VERSION=1.6.1

# Use Australian Mirrors
RUN sed 's/archive.ubuntu.com/au.archive.ubuntu.com/g' /etc/apt/sources.list > /etc/apt/sourcesau.list && \
    mv /etc/apt/sourcesau.list /etc/apt/sources.list && \
    rm -f /etc/apt/apt.conf.d/docker-clean

# Install system level dependencies, flush the font cache and update ca certificates.
RUN --mount=type=cache,target=/var/cache/apt apt-get update && \
    apt-get upgrade -y && \
    apt-get install --no-install-recommends -y \
    curl \
    wget \
    git \
    libmagic-dev \
    gcc \
    binutils \
    libproj-dev \
    gdal-bin \
    vim \
    postgresql-client \
    htop \
    python3-setuptools \
    python3-dev \
    python3-pip \
    tzdata \
    cron \
    rsyslog \
    gunicorn \
    libpq-dev \
    patch \
    mtr \
    python3-pil \
    libreoffice \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/* && \
    update-ca-certificates

# Install the arial font manually as ttf-mscorefonts-installer was breaking the build
COPY parkpasses/static/parkpasses/fonts/arial.ttf ./
RUN install -m644 arial.ttf /usr/share/fonts/truetype/ && \
    rm arial.ttf && \
    fc-cache -vr

# install node 16
RUN ln -s /usr/bin/python3 /usr/bin/python && \
    touch install_node.sh && \
    curl -fsSL https://deb.nodesource.com/setup_16.x -o install_node.sh && \
    chmod +x install_node.sh && ./install_node.sh && \
    apt-get install -y nodejs && \
    pip install --upgrade pip


FROM builder_base_oim_parkpasses as python_dependencies_parkpasses
WORKDIR /app
# Copy these files accross to the image the first time you deploy to a new environment
# and run the apply_initial_migrations.sh script.
# COPY 0001_initial.py.patch1 0001_initial.py.patch2 apply_initial_migrations.sh ./
COPY gunicorn.ini manage.py pyproject.toml poetry.lock ./
RUN pip install "poetry==$POETRY_VERSION" && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/ /tmp/* /var/tmp/*


# Do a clean install and build of the vue 3 application
FROM python_dependencies_parkpasses as collect_static_parkpasses
COPY parkpasses ./parkpasses
RUN touch /app/.env && \
    python manage.py collectstatic --no-input


FROM collect_static_parkpasses as install_build_vue3_parkpasses
RUN cd /app/parkpasses/frontend/parkpasses; npm ci --omit=dev && \
    cd /app/parkpasses/frontend/parkpasses; npm run build


FROM install_build_vue3_parkpasses as configure_and_launch_parkpasses

COPY .git ./.git

# Install the project (ensure that frontend projects have been built prior to this step).
COPY timezone /etc/timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    touch /app/rand_hash

COPY cron /etc/cron.d/dockercron
RUN chmod 0644 /etc/cron.d/dockercron && \
    crontab /etc/cron.d/dockercron && \
    touch /var/log/cron.log && \
    wget https://raw.githubusercontent.com/dbca-wa/wagov_utils/main/wagov_utils/bin/health_check.sh -O /bin/health_check.sh && \
    chmod 755 /bin/health_check.sh

COPY startup.sh /
RUN chmod 755 /startup.sh
EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/startup.sh"]
