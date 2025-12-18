FROM alpine:3.23.2@sha256:865b95f46d98cf867a156fe4a135ad3fe50d2056aa3f25ed31662dff6da4eb62

# Dependencies
RUN apk --no-cache add \
    curl \
    jq \
    tzdata

# uv
COPY --from=ghcr.io/astral-sh/uv:0.9.18@sha256:5713fa8217f92b80223bc83aac7db36ec80a84437dbc0d04bbc659cae030d8c9 /uv /uvx /bin/

# Supercronic
# renovate: datasource=github-releases packageName=aptible/supercronic
ARG SUPERCRONIC_VERSION="v0.2.41"
ARG SUPERCRONIC="supercronic-linux-amd64"
ARG SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/${SUPERCRONIC_VERSION}/${SUPERCRONIC}
RUN export SUPERCRONIC_SHA256SUM=$(curl -fsSL \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    https://api.github.com/repos/aptible/supercronic/releases \
    | jq -r '.[] | select(.name == $ENV.SUPERCRONIC_VERSION) | .assets[] | select(.name == $ENV.SUPERCRONIC) | .digest') \
    && echo "SHA256 digest from API: ${SUPERCRONIC_SHA256SUM}" \
    && curl -fsSLO "$SUPERCRONIC_URL" \
    && echo "${SUPERCRONIC_SHA256SUM}  ${SUPERCRONIC}" | sed -e 's/^sha256://' | sha256sum -c - \
    && chmod +x "$SUPERCRONIC" \
    && mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" \
    && ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic

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
ENTRYPOINT ["/usr/local/bin/supercronic", "/opt/fuelhook/crontab/fuelhook-cron"]
LABEL org.opencontainers.image.authors="MattKobayashi <matthew@kobayashi.au>"
