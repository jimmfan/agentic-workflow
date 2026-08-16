# Evaluation-infrastructure repair for the immutable database_migration v5 image.
#
# The registry task Dockerfile uses `npm@latest`, which resolved to npm 12.0.2
# on 2026-08-16. npm 12 requires Node >=22.22.2, while the task intentionally
# pins Node 22.12.0. This derived image keeps the task's environment unchanged
# except for freezing the last compatible npm 11 release used by this harness.

FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

LABEL harbor.evaluation.source-dockerfile-sha256="2222a0ab6392d0ab835c2a34064faef80819339d803d076783faed9a21c0f9d9"
LABEL harbor.evaluation.npm-version="11.16.0"
LABEL harbor.evaluation.codex-nvm-bridge="home-to-usr-local"

ENV DEBIAN_FRONTEND=noninteractive
ENV HOME=/tmp/agent_home
ENV UV_CACHE_DIR=/tmp/uv-cache
ENV PIP_CACHE_DIR=/tmp/pip-cache
ENV PYTHONUNBUFFERED=1
ENV TERM=xterm
ENV COLUMNS=240
ENV LINES=60

RUN apt-get update  && apt-get install -y --no-install-recommends         build-essential         ca-certificates         curl         git         procps         util-linux         docker-cli         pkg-config         libssl-dev         sqlite3  && (apt-get install -y --no-install-recommends docker-compose-plugin         || apt-get install -y --no-install-recommends docker-compose-v2         || apt-get install -y --no-install-recommends docker-compose)  && mkdir -p /usr/local/lib/docker/cli-plugins /usr/lib/docker/cli-plugins  && if [ -x /usr/bin/docker-compose ]; then         ln -sf /usr/bin/docker-compose /usr/local/lib/docker/cli-plugins/docker-compose;         ln -sf /usr/bin/docker-compose /usr/lib/docker/cli-plugins/docker-compose;     fi  && rm -rf /var/lib/apt/lists/*

ENV NVM_DIR=/usr/local/nvm
ENV NODE_VERSION=22.12.0
SHELL ["/bin/bash", "-lc"]
RUN mkdir -p "$NVM_DIR"  && curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash  && . "$NVM_DIR/nvm.sh"  && nvm install "$NODE_VERSION"  && nvm alias default "$NODE_VERSION"  && nvm use default  && npm install -g npm@11.16.0  && NODE_PATH="$(nvm which node)"  && NODE_BIN_DIR="$(dirname "$NODE_PATH")"  && ln -sf "$NODE_BIN_DIR/node" /usr/local/bin/node  && ln -sf "$NODE_BIN_DIR/npm" /usr/local/bin/npm  && ln -sf "$NODE_BIN_DIR/npx" /usr/local/bin/npx
ENV PATH="$NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH"

ENV CARGO_HOME=$HOME/.cargo
ENV RUSTUP_HOME=$HOME/.rustup
RUN curl -fsSL https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable
ENV PATH="$CARGO_HOME/bin:$PATH"

RUN groupadd -g 1000 agent  && useradd -m -u 1000 -g 1000 -d "$HOME" -s /bin/bash agent  && (getent group docker >/dev/null || groupadd docker)  && usermod -aG docker agent  && mkdir -p /app /assets /workspace "$HOME" "$UV_CACHE_DIR" "$PIP_CACHE_DIR" "$CARGO_HOME" "$RUSTUP_HOME"  && ln -s "$NVM_DIR" "$HOME/.nvm"  && chown -R agent:agent /app /workspace "$HOME" "$UV_CACHE_DIR" "$PIP_CACHE_DIR"  && chmod 1777 /tmp "$UV_CACHE_DIR" "$PIP_CACHE_DIR"

WORKDIR /app
