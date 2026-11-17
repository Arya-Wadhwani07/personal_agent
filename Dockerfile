# syntax=docker/dockerfile:1
FROM tailscale/tailscale:v1.104.7@sha256:72c1e19e0aedca96b8533bbb0b4368564410ff20b17e53b804eb6c1f04a31be4 AS tailnet
FROM python:3.14-slim-bookworm@sha256:3fe1a0b6c2d6b2ebb572906cdabeca75aeb558c0c17db5ffefbcf8094871c32b AS build
ENV UV_CACHE_DIR=/tmp/uv-cache PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY scripts/bootstrap.py scripts/bootstrap.py
RUN python scripts/bootstrap.py && python -m pip install --no-cache-dir uv==0.13.8
COPY src src
RUN uv sync --locked --no-dev
FROM build AS test
RUN uv sync --locked --extra dev
COPY tests tests
COPY scripts scripts
ENV HOME=/tmp/a3-home HERMES_HOME=/tmp/a3-hermes-tests
USER 10001:10001

# Hermes intentionally requires editable installation; keep its verified source at its build path.
FROM python:3.14-slim-bookworm@sha256:3fe1a0b6c2d6b2ebb572906cdabeca75aeb558c0c17db5ffefbcf8094871c32b AS runtime
ENV PATH=/app/.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/state HERMES_HOME=/state/hermes A3_STATE_DIR=/state
WORKDIR /app
COPY --from=build /app /app
COPY --from=tailnet /usr/local/bin/tailscale /usr/local/bin/tailscale
COPY --from=tailnet /usr/local/bin/tailscaled /usr/local/bin/tailscaled
COPY scripts scripts
RUN mkdir -p /state && chown 10001:10001 /state
USER 10001:10001
EXPOSE 8080
ENTRYPOINT ["python", "-m", "personal_agent.runtime"]
