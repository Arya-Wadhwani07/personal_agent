# syntax=docker/dockerfile:1
FROM tailscale/tailscale:v1.104.7@sha256:72c1e19e0aedca96b8533bbb0b4368564410ff20b17e53b804eb6c1f04a31be4 AS tailnet
FROM python:3.14-slim-trixie@sha256:9aaa474097d094040649f2162a627c0049b408f52138d980916788d80f04802f AS build
ENV UV_CACHE_DIR=/tmp/uv-cache PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
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
ENV PATH=/app/.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/state HERMES_HOME=/state/hermes A3_STATE_DIR=/state
WORKDIR /app
# Security update absent from the pinned base; explicit package version preserves reviewability.
RUN apt-get update && apt-get install -y --no-install-recommends zlib1g=1:1.3.dfsg+really1.3.1-1+deb13u1 && rm -rf /var/lib/apt/lists/*
COPY --from=build /app /app
COPY --from=tailnet /usr/local/bin/tailscale /usr/local/bin/tailscale
COPY --from=tailnet /usr/local/bin/tailscaled /usr/local/bin/tailscaled
COPY scripts scripts
# I install dependencies in the build stage; the runtime needs no package installer.
RUN /usr/local/bin/python -m pip uninstall -y pip && mkdir -p /state && chown 10001:10001 /state
USER 10001:10001
EXPOSE 8080
ENTRYPOINT ["python", "-m", "personal_agent.runtime"]
