# ==============================================================================
# Stage 1: Build Dependencies
# ==============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install system dependencies if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies into virtual env
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==============================================================================
# Stage 2: Final Runtime Image
# ==============================================================================
FROM python:3.11-slim AS runner

WORKDIR /app

# Copy virtual environment and binary paths
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy project source directories and files
COPY pipeline/ pipeline/
COPY tracing/ tracing/
COPY analysis/ analysis/
COPY eval/ eval/
COPY api/ api/
COPY ui/ ui/
COPY utils/ utils/
COPY schema.sql .
COPY .env.example .env

# Expose ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000
EXPOSE 8501

# Default runtime command to print scaffold version details
CMD ["python", "-c", "import utils.settings; print('Observability Scaffold initialized successfully.')"]
