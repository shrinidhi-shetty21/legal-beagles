ARG FUNCTION_DIR="/function"

FROM python:3.9.13-alpine3.15

COPY ./dockerfiles/lambda/requirements.pip /config/lambda_requirements.pip
RUN apk add --no-cache \
    libpq \
    expat=2.5.0-r0 \
    linux-headers



RUN apk update && \
# Basic Necessary packages for build
    apk --no-cache add --virtual build-deps-alpine build-base libtool autoconf automake musl-dev libexecinfo-dev make cmake gcc && \
    # package required for lambda invocation \
    apk --no-cache add libstdc++ && \
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
    pip install -r /config/lambda_requirements.pip --no-cache-dir && \
# Deleting curl dependencies
    apk del curl-dependencies && \
# Deleting base dependencies
    apk del build-deps-alpine && \
# Deleting LXML dependencies
    apk del lxml-dependencies && \
# deleting postgresql dependencies
    apk del postgresql-deps && \
# Remove cache
    rm -rf /var/cache/*  /app/.cache/*

ARG FUNCTION_DIR
COPY --from=761638476042.dkr.ecr.us-east-1.amazonaws.com/official/awslambdaric:2.0.4 ${FUNCTION_DIR} /usr/local/lib/python3.9/site-packages/

####################
# APP SETUP BEGINS #
####################
# Create directories necessary for app
RUN mkdir -p /app/legal-beagles/
COPY ./src  /app/legal-beagles/src

# Switch to project directory
WORKDIR /usr/local/lib/python3.9/site-packages/core/extractor_lambda/

ENV PYTHONPATH /app/legal-beagles/src/:/usr/local/lib/python3.9/site-packages/core/extractor/third_party/
ENV DJANGO_SETTINGS_MODULE core.extractor_celery.django_settings

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]

######################
# App setup complete #
######################