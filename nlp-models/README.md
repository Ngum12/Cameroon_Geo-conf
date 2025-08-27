# NLP Processing Pipeline - Project Sentinel

**Classification:** RESTRICTED  
**Authority:** Cameroon Defense Force  
**Component:** AI-Powered OSINT Analysis System

## Overview

This directory contains the Natural Language Processing (NLP) pipeline components for Project Sentinel, including translation services and Named Entity Recognition (NER) capabilities for multilingual OSINT analysis.

## Components

### 1. Translation Service (`translation_service.py`)

FastAPI-based service that translates text from multiple languages to English using Facebook's M2M100 model.

### 2. Named Entity Recognition Service (`ner_service.py`)

FastAPI-based service that extracts named entities (persons, locations, organizations) from English text using XLM-RoBERTa model fine-tuned on CoNLL-03 dataset.

#### Translation Service Features
- **Multi-language Support**: 100+ languages including French, English, Arabic, Spanish
- **Automatic Language Detection**: Detects source language automatically
- **High Performance**: Optimized for batch processing of news articles
- **RESTful API**: Easy integration with other Project Sentinel components
- **Health Monitoring**: Built-in health checks and status endpoints

#### NER Service Features
- **High-Accuracy Entity Extraction**: Uses state-of-the-art XLM-RoBERTa model
- **Multiple Entity Types**: PERSON, LOCATION, ORGANIZATION, MISCELLANEOUS
- **Confidence Scoring**: Each entity includes confidence score (0.0-1.0)
- **Text Position Mapping**: Start/end positions for each entity
- **Entity Grouping**: Grouped analysis by entity type
- **Confidence Filtering**: High-confidence entity extraction
- **Batch Processing**: Efficient processing of multiple texts

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

##### POST `/analyze-entities` (NER Service)
Extract named entities from English text.

**Request:**
```json
{
  "text": "President Paul Biya of Cameroon visited Yaoundé today."
}
```

**Response:**
```json
{
  "entities": [
    {
      "word": "Paul Biya",
      "entity_group": "PERSON",
      "confidence": 0.9998,
      "start": 10,
      "end": 19
    },
    {
      "word": "Cameroon", 
      "entity_group": "LOCATION",
      "confidence": 0.9995,
      "start": 23,
      "end": 31
    },
    {
      "word": "Yaoundé",
      "entity_group": "LOCATION", 
      "confidence": 0.9992,
      "start": 40,
      "end": 47
    }
  ],
  "entity_count": 3,
  "processing_time": 0.45,
  "text_length": 56
}
```

##### GET `/entity-types` (NER Service)
List supported entity types and descriptions.

##### POST `/analyze-entities/grouped` (NER Service)  
Analyze entities and return grouped by type.

##### POST `/analyze-entities/high-confidence` (NER Service)
Return only high-confidence entities above specified threshold.

## Installation & Deployment

### Option 1: Docker Deployment (Recommended)

#### Translation Service
```bash
# Build the Docker image
docker build -t project-sentinel/translation-service .

# Run the container
docker run -p 8001:8001 --name translation-service project-sentinel/translation-service

# Check service status
curl http://localhost:8001/health
```

#### NER Service
```bash
# Build the NER Docker image 
docker build -f ner_dockerfile -t project-sentinel/ner-service .

# Run the NER container (note: different port 8002)
docker run -p 8002:8002 --name ner-service project-sentinel/ner-service

# Check NER service status  
curl http://localhost:8002/health
```

### Option 2: Local Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the translation service
python translation_service.py
# Or with uvicorn
uvicorn translation_service:app --host 0.0.0.0 --port 8001 --reload

# Run the NER service (in separate terminal)
python ner_service.py  
# Or with uvicorn
uvicorn ner_service:app --host 0.0.0.0 --port 8002 --reload
```

## Testing

Run the test suites to verify functionality:

```bash
# Test Translation Service
# Start the translation service first (in another terminal)
python translation_service.py

# Run translation tests
python test_translation.py

# Test NER Service  
# Start the NER service first (in another terminal)
python ner_service.py

# Run NER tests
python test_ner.py
```

## Integration with Data Ingestion

Both services integrate with the news spider in the `data-ingestion` directory:

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

async def extract_entities(text):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://ner-service:8002/analyze-entities",
            json={"text": text}
        )
        return response.json()

# Use in spider pipeline
translated_article = await translate_article(article['text'])
article['translated_text'] = translated_article['translated_text']

# Extract entities from translated text
entities_result = await extract_entities(article['translated_text'])
article['entities'] = entities_result['entities']
article['entity_count'] = entities_result['entity_count']
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
