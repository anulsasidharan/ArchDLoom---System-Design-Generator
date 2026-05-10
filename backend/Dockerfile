FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Node.js + Chromium for @mermaid-js/mermaid-cli diagram rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
        nodejs npm chromium fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Skip Puppeteer's bundled Chromium download; use system Chromium instead
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Install mmdc globally and write the no-sandbox config needed for Docker/root
RUN npm install -g @mermaid-js/mermaid-cli \
    && echo '{"args":["--no-sandbox","--disable-setuid-sandbox","--disable-dev-shm-usage"]}' \
       > /puppeteer-config.json

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock alembic.ini ./
COPY app ./app/
COPY alembic ./alembic/
COPY static ./static/

RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
