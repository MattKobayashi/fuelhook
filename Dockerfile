FROM python:3.13.4-alpine3.22@sha256:b4d299311845147e7e47c970566906caf8378a1f04e5d3de65b5f2e834f8e3bf
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
