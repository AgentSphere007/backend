FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  UV_PROJECT_ENVIRONMENT=.venv
RUN pip install --no-cache-dir uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --group release
COPY src ./src
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uv", "run", "python", "-m", "src.main"]
