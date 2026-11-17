# syntax=docker/dockerfile:1
FROM --platform=$BUILDPLATFORM golang:1.27-alpine@sha256:70bd7ddea8b6cbe5d6943cde279d6b67feb10cc924fb9100d1d8757c1575b280 AS tailnet
ARG TARGETARCH
ENV GOTOOLCHAIN=local GOMAXPROCS=4
COPY scripts/build_tailnet.sh /build_tailnet.sh
RUN sh /build_tailnet.sh

FROM python:3.14-slim-trixie@sha256:9aaa474097d094040649f2162a627c0049b408f52138d980916788d80f04802f AS sqlite
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev make gettext libattr1-dev perl && rm -rf /var/lib/apt/lists/*
COPY scripts/build_sqlite.py /build_sqlite.py
RUN python /build_sqlite.py
COPY scripts/build_acl.py /build_acl.py
RUN python /build_acl.py
FROM python:3.14-slim-trixie@sha256:9aaa474097d094040649f2162a627c0049b408f52138d980916788d80f04802f AS build
ENV UV_CACHE_DIR=/tmp/uv-cache PYTHONDONTWRITEBYTECODE=1 LD_LIBRARY_PATH=/usr/local/lib
WORKDIR /app
COPY --from=sqlite /out/libsqlite3.so.0 /usr/local/lib/libsqlite3.so.0
RUN ldconfig && python -c "import sqlite3; assert sqlite3.sqlite_version == '3.54.1'"
COPY pyproject.toml uv.lock ./
COPY scripts/bootstrap.py scripts/bootstrap.py
RUN python scripts/bootstrap.py && python -m pip install --no-cache-dir uv==0.13.8
COPY src src
COPY skills skills
RUN uv sync --locked --no-dev
FROM build AS test
RUN uv sync --locked --extra dev
COPY tests tests
COPY scripts scripts
ENV HOME=/tmp/a3-home HERMES_HOME=/tmp/a3-hermes-tests
USER 10001:10001

# Hermes intentionally requires editable installation; keep its verified source at its build path.
FROM python:3.14-slim-trixie@sha256:9aaa474097d094040649f2162a627c0049b408f52138d980916788d80f04802f AS runtime
ENV LD_LIBRARY_PATH=/usr/local/lib PATH=/app/.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/state HERMES_HOME=/state/hermes A3_STATE_DIR=/state
WORKDIR /app
# Security update absent from the pinned base; explicit package version preserves reviewability.
RUN apt-get update && apt-get install -y --no-install-recommends zlib1g=1:1.3.dfsg+really1.3.1-1+deb13u1 && rm -rf /var/lib/apt/lists/*
COPY --from=build /app /app
COPY --from=tailnet /out/tailscale /usr/local/bin/tailscale
COPY --from=tailnet /out/tailscaled /usr/local/bin/tailscaled
COPY --from=tailnet /out/go.mod /out/go.sum /usr/local/share/a3-tailnet/
COPY --from=sqlite /out/libsqlite3.so.0 /usr/local/lib/libsqlite3.so.0
COPY --from=sqlite /out/sqlite-security.deb /out/acl-security.deb /tmp/
RUN dpkg -i /tmp/sqlite-security.deb /tmp/acl-security.deb && rm /tmp/sqlite-security.deb /tmp/acl-security.deb && ldconfig && python -c "import sqlite3; assert sqlite3.sqlite_version == '3.54.1'"
COPY scripts scripts
RUN A3_IMAGE_BUILD=1 python scripts/harden_image.py
# I install dependencies in the build stage; the runtime needs no package installer.
RUN /usr/local/bin/python -m pip uninstall -y pip && mkdir -p /state && chown 10001:10001 /state
USER 10001:10001
EXPOSE 8080
ENTRYPOINT ["python", "-m", "personal_agent.runtime"]
