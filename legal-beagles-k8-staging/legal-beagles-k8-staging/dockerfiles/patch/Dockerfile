FROM python:3.9.13-alpine3.15

RUN apk add --no-cache \
    libpq \
    expat=2.5.0-r0 \
    linux-headers

RUN apk update && \
# Basic Necessary packages for build
    apk --no-cache add --virtual build-deps-alpine build-base && \
# For LXML
    apk --no-cache add --virtual lxml-dependencies libxslt-dev && \
# For postgresql client to take backup
     apk add postgresql-client && \
# For psycopg2
    apk add --no-cache --virtual postgresql-deps libpq-dev && \
# install core
    pip install uc-core3==3.2406060702 --extra-index-url https://gitlab.unicourt.net/api/v4/projects/2887/packages/pypi/simple && \
# Deleting base dependencies
    apk del build-deps-alpine && \
# deleting postgresql dependencies
    apk del postgresql-deps && \
# Remove cache
    rm -rf /var/cache/*  /root/.cache/*

####################
# APP SETUP BEGINS #
####################
# Create directories necessary for patch pod
RUN mkdir -p /root/codaxtr-extractor/
COPY ./src  /root/codaxtr-extractor/src
COPY ./patch  /root/codaxtr-extractor/patch

# Create output directory
RUN mkdir -p /root/codaxtr-extractor/patch/output/

# Switch to project directory
WORKDIR /root/codaxtr-extractor/patch

ENV PYTHONPATH /root/codaxtr-extractor/src/:/usr/local/lib/python3.9/site-packages/core/extractor/third_party/
ENV DJANGO_SETTINGS_MODULE=core.extractor_celery.django_settings