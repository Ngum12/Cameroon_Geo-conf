# Dockerfile for Project Sentinel Translation Service
# Cameroon Defense Force OSINT Analysis System - NLP Pipeline

FROM python:3.11-slim

# Set metadata labels
LABEL maintainer="Project Sentinel ML Team"
LABEL version="1.0"
LABEL description="Translation service using Facebook M2M100 model for Project Sentinel"
LABEL classification="RESTRICTED"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/transformers \
    TORCH_HOME=/app/.cache/torch

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    git \
    curl \
    wget \
    unzip \
    libgomp1 \
    libblas3 \
    liblapack3 \
    libatlas-base-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r nlp && useradd -r -g nlp -m nlp

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .

# Install Python packages
# Install torch with CPU support (change for GPU if needed)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Create necessary directories and set permissions
RUN mkdir -p /app/.cache/huggingface /app/.cache/transformers /app/.cache/torch /app/logs /app/models && \
    chown -R nlp:nlp /app

# Copy application code
COPY translation_service.py .

# Copy any additional model files or configurations if needed
# COPY models/ ./models/

# Switch to non-root user
USER nlp

# CRITICAL: Pre-download the M2M100 model at build time for DEFENSE OPERATIONS
# This is REQUIRED for operational readiness - instant response without internet dependency
# Defense systems cannot wait for model downloads during operations
RUN python -c "from transformers import MarianMTModel, MarianTokenizer; print('Loading Helsinki-NLP opus-mt-fr-en model for defense operations...'); tokenizer = MarianTokenizer.from_pretrained('Helsinki-NLP/opus-mt-fr-en'); model = MarianMTModel.from_pretrained('Helsinki-NLP/opus-mt-fr-en'); print('French→English translation capability READY for deployment');"

# Expose port for FastAPI
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Set up logging directory
VOLUME ["/app/logs", "/app/.cache"]

# Default command to run the service
CMD ["uvicorn", "translation_service_cpu:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]

# Alternative commands for different deployment scenarios:

# For development with auto-reload:
# CMD ["uvicorn", "translation_service:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]

# For production with Gunicorn:
# CMD ["gunicorn", "translation_service:app", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8001"]

# For GPU support (uncomment if using GPU-enabled base image):
# FROM nvidia/cuda:11.8-devel-ubuntu20.04
# RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

