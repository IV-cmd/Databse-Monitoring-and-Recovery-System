# Multi-stage build with distroless final image

# Stage 1: Builder stage with full Python environment
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Stage 2: Distroless runtime stage
FROM gcr.io/distroless/python3-debian11 as runtime

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --from=builder /app /app

WORKDIR /app

# Expose port
EXPOSE 8000

# Health check (using wget since curl not available in distroless)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1

# Run the application as non-root (distroless uses non-root by default)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
