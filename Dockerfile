FROM python:3.13.0-alpine3.20

WORKDIR /opt/fuelhook

RUN addgroup -S fuelhook && adduser -S fuelhook -G fuelhook \
    && mkdir -p data \
    && chown fuelhook:fuelhook data \
    && apk --no-cache add supercronic tzdata

USER fuelhook

COPY fuelhook-cron ./crontab/fuelhook-cron
COPY app.py app.py
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV TZ=UTC \
    REGION=0 \
    WEBHOOK_URL=

VOLUME ["/opt/fuelhook/data"]

ENTRYPOINT ["supercronic", "./crontab/fuelhook-cron"]

LABEL org.opencontainers.image.authors="MattKobayashi <matthew@kobayashi.au>"
