FROM mcr.microsoft.com/devcontainers/python:2-3.14-trixie

# Install Node.js (LTS) and PostgreSQL client
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y curl postgresql-client \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Expose application port
EXPOSE 8100

# Default command: run the startup script (repo must be mounted at /workspace)
CMD ["/workspace/start.sh"]
