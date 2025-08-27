# backend/Dockerfile
FROM python:3.11-slim

# System deps (add more only if a package complains)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy dependency manifests first for layer caching
COPY pyproject.toml poetry.lock* /app/

# Install deps into the global environment (no virtualenv)
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi

# Copy the backend code
COPY . /app

# Cloud Run will inject $PORT; make sure your server binds to it
ENV PORT=8080

# Choose ONE start command:
# If pyproject.toml has [tool.poetry.scripts] start = "your_module:main"
CMD ["poetry", "run", "start"]
# Otherwise, comment ^ out and use uvicorn directly (fix the module path):
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
