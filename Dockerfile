# CryptoMiner Pro V30 - Main Application Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY cryptominer.py .
COPY mining_engine.py .
COPY scrypt_miner.py .
COPY ai_optimizer.py .
COPY install.py .
COPY mining_config.template .

# Create necessary directories
RUN mkdir -p logs data models

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose web monitoring port
EXPOSE 8001

# Create non-root user for security
RUN groupadd -r cryptominer && useradd -r -g cryptominer cryptominer
RUN chown -R cryptominer:cryptominer /app
USER cryptominer

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/api/ || exit 1

# Default command
CMD ["python3", "cryptominer.py", "--help"]