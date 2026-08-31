# Purpose: Build the Python development image and provide Codex's Linux sandbox prerequisites.
ARG PYTHON_VARIANT="3.14-bookworm"
ARG UV_VERSION="0.11.32"

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv
FROM mcr.microsoft.com/devcontainers/python:${PYTHON_VARIANT}

COPY --from=uv /uv /uvx /usr/local/bin/

RUN apt-get update \
    && apt-get install -y --no-install-recommends ripgrep \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
    && apt-get install -y --no-install-recommends bubblewrap \
    && rm -rf /var/lib/apt/lists/* \
    && install -d -m 0700 -o vscode -g vscode /home/vscode/.codex \
    && install -d -m 0755 /etc/codex

COPY --chmod=0644 codex-system-config.toml /etc/codex/config.toml

# Keep uv on the container's Python 3.14 interpreter and avoid cross-filesystem
# hard-link warnings when its cache and the bind-mounted workspace differ.
ENV UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
