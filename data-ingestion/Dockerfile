# Dockerfile for Project Sentinel News Spider
# Cameroon Defense Force OSINT Analysis System

FROM python:3.11-slim

# Set metadata labels for container identification
LABEL maintainer="Project Sentinel DevOps Team"
LABEL version="1.0"
LABEL description="News ingestion spider for Project Sentinel OSINT system"
LABEL classification="RESTRICTED"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SCRAPY_SETTINGS_MODULE=spider_settings \
    PYTHONPATH=/app

# Create non-root user for security
RUN groupadd -r scrapy && useradd -r -g scrapy scrapy

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    libssl-dev \
    zlib1g-dev \
    libjpeg-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy spider code and configuration
COPY news_spider.py .
COPY items.py .
COPY config/ ./config/

# Create necessary directories
RUN mkdir -p /app/data /app/logs && \
    chown -R scrapy:scrapy /app

# Switch to non-root user
USER scrapy

# Set up environment for Scrapy
ENV SCRAPY_PROJECT=news_ingestion

# Expose port for monitoring (optional)
EXPOSE 6080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import scrapy; print('Scrapy is available')" || exit 1

# Default command to run the spider
CMD ["scrapy", "crawl", "cmr_news_spider", "-o", "/app/data/news_articles.jsonl", "-s", "LOG_FILE=/app/logs/spider.log"]

# Volume for persistent data storage
VOLUME ["/app/data", "/app/logs"]
