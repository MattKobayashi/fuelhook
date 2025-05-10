FROM python:3.13.3-alpine3.21@sha256:452682e4648deafe431ad2f2391d726d7c52f0ff291be8bd4074b10379bb89ff
WORKDIR /opt/fuelhook
RUN addgroup -S fuelhook && adduser -S fuelhook -G fuelhook \
    && mkdir -p data \
    && chown fuelhook:fuelhook data \
    && apk --no-cache add supercronic tzdata uv
USER fuelhook
COPY fuelhook-cron /opt/fuelhook/crontab/fuelhook-cron
COPY main.py main.py
ENV TZ=UTC
ENV REGION=0
ENV WEBHOOK_URL=
VOLUME ["/opt/fuelhook/data"]
ENTRYPOINT ["/usr/bin/supercronic", "/opt/fuelhook/crontab/fuelhook-cron"]
LABEL org.opencontainers.image.authors="MattKobayashi <matthew@kobayashi.au>"
