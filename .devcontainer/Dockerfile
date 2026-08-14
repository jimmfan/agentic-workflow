ARG PYTHON_VARIANT="3.14-bookworm"
ARG UV_VERSION="0.11.32"

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv
FROM mcr.microsoft.com/devcontainers/python:${PYTHON_VARIANT}

COPY --from=uv /uv /uvx /usr/local/bin/

# Keep uv on the container's Python 3.14 interpreter and avoid cross-filesystem
# hard-link warnings when its cache and the bind-mounted workspace differ.
ENV UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
