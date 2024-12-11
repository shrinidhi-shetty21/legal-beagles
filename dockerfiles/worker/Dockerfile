FROM python:3.9.13-alpine3.15

COPY ./dockerfiles/worker/requirements.pip /config/worker_requirements.pip
RUN apk add --no-cache \
    libpq \
    expat=2.5.0-r0 \
    linux-headers

RUN apk update && \
# Basic Necessary packages for build
    apk --no-cache add --virtual build-deps-alpine build-base && \
# For PyCurl
    apk --no-cache add --virtual curl-dependencies curl-dev && \
# For LXML
    apk --no-cache add --virtual lxml-dependencies libxslt-dev && \
# For PyCurl
    apk --no-cache add libcurl && \
# For psycopg2
    apk add --no-cache --virtual postgresql-deps libpq-dev && \
# install core
    pip install uc-core3==3.2406060702 --extra-index-url https://gitlab.unicourt.net/api/v4/projects/2887/packages/pypi/simple && \
# install odyssey
    pip install uc-codaxtr-odyssey==0.2308210952 --extra-index-url https://gitlab.unicourt.net/api/v4/projects/2887/packages/pypi/simple && \
# Other requirements
    pip install -r /config/worker_requirements.pip --no-cache-dir && \
# Deleting curl dependencies
    apk del curl-dependencies && \
# Deleting base dependencies
    apk del build-deps-alpine && \
# Deleting LXML dependencies
    apk del lxml-dependencies && \
# deleting postgresql dependencies
    apk del postgresql-deps && \
# Remove cache
    rm -rf /var/cache/*  /root/.cache/*


####################
# APP SETUP BEGINS #
####################
# Create directories necessary for app
RUN mkdir -p /root/legal-beagles/
COPY ./src  /root/legal-beagles/src

# Switch to project directory
WORKDIR /usr/local/lib/python3.9/site-packages/core

ENV PYTHONPATH /root/legal-beagles/src/:/usr/local/lib/python3.9/site-packages/core/extractor/third_party/
ENV DJANGO_SETTINGS_MODULE core.extractor_celery.django_settings
######################
# App setup complete #
######################