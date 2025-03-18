FROM python:3.13.2-alpine3.20@sha256:e885b40c1ed9f3134030e99a27bd61e98e376bf6d6709cccfb3c0aa6e856f56a
WORKDIR /opt/fuelhook
RUN addgroup -S fuelhook && adduser -S fuelhook -G fuelhook \
    && mkdir -p data \
    && chown fuelhook:fuelhook data \
    && apk --no-cache add supercronic tzdata
USER fuelhook
COPY fuelhook-cron ./crontab/fuelhook-cron
COPY main.py main.py
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
ENV TZ=UTC
ENV REGION=0
ENV WEBHOOK_URL=
VOLUME ["/opt/fuelhook/data"]
ENTRYPOINT ["supercronic", "./crontab/fuelhook-cron"]
LABEL org.opencontainers.image.authors="MattKobayashi <matthew@kobayashi.au>"
