FROM python:3.11.0a5-alpine3.14

WORKDIR /opt/fuelhook

ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.1.12/supercronic-linux-amd64 \
    SUPERCRONIC=supercronic-linux-amd64 \
    SUPERCRONIC_SHA1SUM=048b95b48b708983effb2e5c935a1ef8483d9e3e

RUN wget "$SUPERCRONIC_URL" \
    && echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - \
    && chmod +x "$SUPERCRONIC" \
    && mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" \
    && ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic \
    && addgroup -S fuelhook && adduser -S fuelhook -G fuelhook \
    && mkdir -p data \
    && chown fuelhook:fuelhook data \
    && apk --no-cache upgrade \
    && apk add --no-cache tzdata

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

LABEL maintainer="matthew@kobayashi.com.au"
