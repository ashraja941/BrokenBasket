# backend/Dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy only dependency manifests first (from backend/)
COPY pyproject.toml poetry.lock* /app/

# Install deps ONLY (do not install the project as a package)
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --no-root

# Now copy the backend source code
COPY . /app

# The server must bind 0.0.0.0:$PORT on Cloud Run
ENV PORT=8080

# Pick ONE start command (adjust module path if needed):
# If you have a poetry script named "start":
CMD ["poetry", "run", "start"]
# otherwise, comment the line above and use a direct uvicorn command, e.g.:
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
