# Dockerfile for Project Sentinel Backend API
# Cameroon Defense Force OSINT Analysis System - Django Backend

FROM python:3.11-slim

# Set metadata labels
LABEL maintainer="Project Sentinel Backend Team"
LABEL version="1.0"
LABEL description="Django backend API for Project Sentinel OSINT system"
LABEL classification="RESTRICTED"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=sentinel_core.settings

# Install system dependencies including GeoDjango requirements
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    git \
    curl \
    wget \
    unzip \
    # GeoDjango dependencies
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    libspatialite-dev \
    # PostgreSQL client
    libpq-dev \
    postgresql-client \
    # Additional utilities
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL library path
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so

# Create non-root user for security
RUN groupadd -r django && useradd -r -g django -m django

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R django:django /app

# Copy project files
COPY . .

# Fix ownership
RUN chown -R django:django /app

# Switch to non-root user
USER django

# Collect static files (will be overridden by volume in production)
RUN python manage.py collectstatic --noinput --clear || true

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Create entrypoint script
USER root
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Wait for database\n\
echo "Waiting for database..."\n\
while ! nc -z ${DB_HOST:-postgres-service} ${DB_PORT:-5432}; do\n\
    sleep 1\n\
done\n\
echo "Database is ready!"\n\
\n\
# Run migrations\n\
echo "Running database migrations..."\n\
python manage.py migrate --noinput\n\
\n\
# Create superuser if it does not exist\n\
echo "Creating superuser..."\n\
python manage.py shell -c "\
from django.contrib.auth import get_user_model;\
User = get_user_model();\
if not User.objects.filter(username='\''admin'\'').exists():\
    User.objects.create_superuser('\''admin'\'', '\''admin@sentinel.cdf.gov.cm'\'', '\''SentinelAdmin2024!'\'');\
    print('\''Superuser created'\'')\
else:\
    print('\''Superuser already exists'\'')" || true\n\
\n\
# Start server\n\
exec "$@"\n\
' > /entrypoint.sh && \
chmod +x /entrypoint.sh && \
chown django:django /entrypoint.sh

USER django

# Set default command
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--worker-class", "sync", "--timeout", "120", "sentinel_core.wsgi:application"]

# Alternative commands for different scenarios:

# Development with Django dev server:
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Production with more workers:
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-connections", "1000", "sentinel_core.wsgi:application"]

# With Celery worker (for async tasks):
# CMD ["celery", "-A", "sentinel_core", "worker", "--loglevel=info"]

# Volume mounts for persistent data
VOLUME ["/app/staticfiles", "/app/media", "/app/logs"]
