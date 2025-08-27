# NLP Processing Pipeline - Project Sentinel

**Classification:** RESTRICTED  
**Authority:** Cameroon Defense Force  
**Component:** AI-Powered OSINT Analysis System

## Overview

This directory contains the Natural Language Processing (NLP) pipeline components for Project Sentinel, including translation services and Named Entity Recognition (NER) capabilities for multilingual OSINT analysis.

## Components

### 1. Translation Service (`translation_service.py`)

FastAPI-based service that translates text from multiple languages to English using Facebook's M2M100 model.

#### Features
- **Multi-language Support**: 100+ languages including French, English, Arabic, Spanish
- **Automatic Language Detection**: Detects source language automatically
- **High Performance**: Optimized for batch processing of news articles
- **RESTful API**: Easy integration with other Project Sentinel components
- **Health Monitoring**: Built-in health checks and status endpoints

#### API Endpoints

##### POST `/translate`
Translate text to English.

**Request:**
```json
{
  "text": "Le président du Cameroun a annoncé de nouvelles mesures",
  "source_lang": "auto"
}
```

**Response:**
```json
{
  "translated_text": "The President of Cameroon announced new measures",
  "detected_language": "fr",
  "confidence_score": 0.85,
  "processing_time": 1.23
}
```

##### GET `/health`
Service health check and model status.

##### GET `/languages`
List of supported languages.

## Installation & Deployment

### Option 1: Docker Deployment (Recommended)

```bash
# Build the Docker image
docker build -t project-sentinel/translation-service .

# Run the container
docker run -p 8001:8001 --name translation-service project-sentinel/translation-service

# Check service status
curl http://localhost:8001/health
```

### Option 2: Local Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python translation_service.py

# Or with uvicorn
uvicorn translation_service:app --host 0.0.0.0 --port 8001 --reload
```

## Testing

Run the test suite to verify functionality:

```bash
# Start the service first (in another terminal)
python translation_service.py

# Run tests
python test_translation.py
```

## Integration with Data Ingestion

The translation service integrates with the news spider in the `data-ingestion` directory:

```python
# Example integration
import httpx

async def translate_article(text, source_lang="auto"):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://translation-service:8001/translate",
            json={"text": text, "source_lang": source_lang}
        )
        return response.json()

# Use in spider pipeline
translated_article = await translate_article(article['text'])
article['translated_text'] = translated_article['translated_text']
```

## Kubernetes Deployment

Deploy as part of the Project Sentinel infrastructure:

```yaml
# translation-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: translation-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: translation-service
  template:
    metadata:
      labels:
        app: translation-service
    spec:
      containers:
      - name: translation
        image: project-sentinel/translation-service:latest
        ports:
        - containerPort: 8001
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        env:
        - name: TORCH_HOME
          value: "/app/.cache/torch"
```

## Performance Considerations

### Model Loading
- First startup takes 30-60 seconds to download the M2M100 model (~1.2GB)
- Model is cached after first download
- Consider pre-downloading in Docker image for faster startup

### Resource Requirements
- **Memory**: 2-4GB RAM minimum
- **CPU**: 2+ cores recommended
- **Storage**: 2GB for model cache
- **GPU**: Optional, improves performance significantly

### Scaling
- Service is stateless and can be horizontally scaled
- Use load balancer for multiple instances
- Consider GPU acceleration for high throughput

## Security Considerations

- Service runs as non-root user in container
- No sensitive data stored in service
- Input validation prevents injection attacks
- Rate limiting recommended for production deployment

## Monitoring & Logging

The service provides structured logging and health metrics:

- **Health endpoint**: Monitor service availability
- **Processing metrics**: Track translation performance
- **Error logging**: Detailed error reporting
- **Resource monitoring**: Memory and CPU usage

## Language Support

Primary languages for Cameroonian OSINT:
- **French** (fr) - Primary official language
- **English** (en) - Secondary official language  
- **Arabic** (ar) - Northern regions
- **Spanish** (es) - Regional context
- **Portuguese** (pt) - Regional context

Full list of 100+ supported languages available via `/languages` endpoint.

## Future Enhancements

1. **Named Entity Recognition (NER)**
   - Extract persons, locations, organizations
   - Custom NER models for Cameroonian context

2. **Sentiment Analysis**
   - Analyze news sentiment and emotional tone
   - Track public opinion trends

3. **Text Summarization**
   - Generate article summaries
   - Extract key information

4. **Custom Model Fine-tuning**
   - Fine-tune on Cameroonian news data
   - Improve domain-specific translation quality

## Troubleshooting

### Common Issues

1. **Model download fails**
   - Check internet connection
   - Verify disk space (>2GB required)

2. **Service startup timeout**
   - Increase container memory limits
   - Allow more time for model loading

3. **Translation quality issues**
   - Verify source language detection
   - Check input text length (max 10,000 chars)

### Logs and Debugging

```bash
# Check service logs
docker logs translation-service

# Enable debug logging
export LOG_LEVEL=debug
python translation_service.py
```

## Contact

For technical support or questions about the NLP pipeline:

**Project Sentinel Development Team**  
**Cameroon Defense Force - Intelligence Division**

---

*This document is classified RESTRICTED and is intended for authorized personnel only.*
