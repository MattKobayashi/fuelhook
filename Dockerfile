FROM python:3.9-alpine3.12

WORKDIR /opt/fuelhook

COPY fuelhook-cron /etc/cron.d/fuelhook-cron
COPY app.py app.py

RUN chmod 0644 /etc/cron.d/fuelhook-cron \
    && crontab /etc/cron.d/fuelhook-cron \
    && touch /var/log/cron.log \
    && pip install requests \
    && apk add --no-cache tzdata

ENV TZ=Australia/Brisbane
ENV REGION=0
ENV DISCORD_WH_URL=

ENTRYPOINT ["crond", "-f"]
