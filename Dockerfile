FROM python:3.13.5-alpine@sha256:e08874637f2704667426cb3b8d14581b9cb12dd2c237c8419f65446669443921
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
