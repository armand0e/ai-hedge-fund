# Unified image to run backend and frontend via app/run.sh
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install Node.js 20 and basic tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg ca-certificates bash git \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1 \
    && poetry config virtualenvs.create false

WORKDIR /app

# Leverage layer caching for Python deps
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-interaction --no-ansi

# Copy project
COPY . /app/

# Build frontend assets (production)
WORKDIR /app/app/frontend
RUN npm ci && npm run build

# Ensure run script is executable
WORKDIR /app
RUN chmod +x /app/app/run.sh

# Default container runtime settings for dev servers
ENV DISABLE_BROWSER=1 \
    BACKEND_HOST=0.0.0.0 \
    BACKEND_PORT=8000 \
    FRONTEND_HOST=0.0.0.0 \
    FRONTEND_PORT=5173 \
    FRONTEND_DEV=0

EXPOSE 5173 8000

# Start both services via the provided script
CMD ["bash", "-lc", "cd app && ./run.sh"]
