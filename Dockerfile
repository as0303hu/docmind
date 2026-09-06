# Stage 1: Builder - create a venv and install the package
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY pyproject.toml pyproject.lock* ./
COPY setup.cfg* ./
COPY . .

# Create a virtualenv and install the package into it
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip setuptools wheel \
    && /opt/venv/bin/pip install .

# Stage 2: Runtime image
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/list/*

RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser

WORKDIR /app

# Copy the virtualenv from the builder and add to PATH
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source
COPY --from=builder /app /app

USER appuser

EXPOSE 8000

# Default command to run the FastAPI app
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]