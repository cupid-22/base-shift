# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2024 by Robert Bosch GmbH. All rights reserved.
#
# This file is property of Robert Bosch GmbH. Any unauthorized copy, use or
# distribution is an offensive act against international law and may be
# prosecuted under federal law. Its content is company confidential.
# =============================================================================
FROM python:3.11

RUN set -e && \
		apt-get update && \
		apt-get install -y \
        bash \
		vim \
        jq \
        gdb \
        wget

ENV CONTAINER_ROOT /service

RUN mkdir -m 777 -p $CONTAINER_ROOT

WORKDIR $CONTAINER_ROOT

RUN /usr/local/bin/python -m pip install --upgrade pip

ARG LAPI_VERSION
ENV LAPI_VERSION $LAPI_VERSION

COPY dist/* ./

RUN pip install --find-links=./ ./lapi_workflow_manager-${LAPI_VERSION}-py3*.whl

CMD ["python", "-m","lapi.services.workflow_manager.application"]