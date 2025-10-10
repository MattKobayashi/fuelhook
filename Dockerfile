FROM alpine:3.22.2@sha256:4b7ce07002c69e8f3d704a9c5d6fd3053be500b7f1c69fc0d80990c2ad8dd412

# renovate: datasource=repology depName=alpine_3_22/supercronic
ENV SUPERCRONIC_VERSION="0.2.33-r7"
# renovate: datasource=repology depName=alpine_3_22/tzdata versioning=loose
ENV TZDATA_VERSION="2025b-r0"
# renovate: datasource=repology depName=alpine_3_22/uv
ENV UV_VERSION="0.7.22-r0"

RUN apk add --no-cache \
    supercronic="${SUPERCRONIC_VERSION}" \
    tzdata="${TZDATA_VERSION}" \
    uv="${UV_VERSION}"

WORKDIR /opt/fuelhook
RUN addgroup -S fuelhook && adduser -S fuelhook -G fuelhook \
    && chown -R fuelhook:fuelhook /opt/fuelhook \
    && mkdir -p /opt/fuelhook/data
USER fuelhook
COPY fuelhook-cron /opt/fuelhook/crontab/fuelhook-cron
COPY main.py pyproject.toml /opt/fuelhook/
ENV TZ=UTC
ENV REGION=0
ENV WEBHOOK_URL=
VOLUME ["/opt/fuelhook/data"]
ENTRYPOINT ["/usr/bin/supercronic", "/opt/fuelhook/crontab/fuelhook-cron"]
LABEL org.opencontainers.image.authors="MattKobayashi <matthew@kobayashi.au>"
