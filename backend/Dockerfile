# CryptoMiner Pro V30 - Backend API Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY server.py .
COPY .env .

# Create logs directory
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose backend port
EXPOSE 8001

# Create non-root user
RUN groupadd -r backend && useradd -r -g backend backend
RUN chown -R backend:backend /app
USER backend

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/api/ || exit 1

# Start backend server
CMD ["python3", "server.py"]