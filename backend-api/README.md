# Project Sentinel Backend API

**Classification:** RESTRICTED  
**Authority:** Cameroon Defense Force  
**Component:** Django Backend API for OSINT Analysis System

## Overview

This is the main backend API for Project Sentinel, built with Django and Django REST Framework. It orchestrates the complete OSINT intelligence pipeline, integrating data ingestion, NLP processing, and providing APIs for the frontend dashboard.

## Architecture

### Core Components

1. **NewsArticle Model**: Stores raw and processed article data with GeoDjango location support
2. **Processing Pipeline**: Integrates with Translation and NER services
3. **REST API**: Provides endpoints for frontend data consumption
4. **GeoJSON Support**: Enables map-based visualization of intelligence data
5. **Admin Interface**: Comprehensive admin panel for article management

### Database Schema

#### NewsArticle Model
- `id`: UUID primary key
- `url`: Original article URL
- `title`: Article title
- `source`: News source name
- `raw_text`: Original article content
- `processed_json`: NLP processing results (translation, entities, etc.)
- `published_date`: Article publication date
- `location`: PostGIS Point field for geographic data
- Additional metadata fields for classification, priority, processing status

## API Endpoints

### Core Endpoints

#### POST `/api/v1/process-article/`
Process a new article through the complete NLP pipeline.

**Request:**
```json
{
  "url": "https://example.com/article",
  "title": "Article Title",
  "source": "News Source",
  "raw_text": "Article content...",
  "published_date": "2024-01-01T12:00:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Article processed successfully",
  "article": {
    "id": "uuid",
    "title": "Article Title",
    "processing_status": "processed",
    "entities": [...],
    "translated_text": "...",
    "coordinates": {"latitude": 3.848, "longitude": 11.502}
  }
}
```

#### GET `/api/v1/events/`
Returns processed articles as GeoJSON for map visualization.

**Query Parameters:**
- `limit`: Maximum articles to return (default: 100)
- `days`: Number of days back to search (default: 30)
- `source`: Filter by news source
- `priority`: Filter by priority level (1-4)

**Response:** GeoJSON FeatureCollection with article features

#### GET `/api/v1/articles/`
List articles with filtering and pagination.

#### GET `/api/v1/articles/{id}/`
Retrieve detailed information about a specific article.

#### GET `/api/v1/statistics/`
Returns system statistics and analytics.

### Health Check
#### GET `/health/`
Service health status.

## Installation & Setup

### Prerequisites

1. **Python 3.11+**
2. **PostgreSQL with PostGIS extension**
3. **Redis** (for Celery task queue)
4. **GDAL/GEOS libraries** (for GeoDjango)

### Local Development Setup

1. **Install System Dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install python3-dev postgresql postgresql-contrib postgis redis-server
   sudo apt-get install gdal-bin libgdal-dev libgeos-dev libproj-dev
   
   # macOS
   brew install postgresql postgis redis gdal geos proj
   ```

2. **Setup Database:**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE sentinel_db;
   CREATE USER sentinel WITH PASSWORD 'your_password';
   ALTER USER sentinel CREATEDB;
   GRANT ALL PRIVILEGES ON DATABASE sentinel_db TO sentinel;
   \c sentinel_db
   CREATE EXTENSION postgis;
   \q
   ```

3. **Install Python Dependencies:**
   ```bash
   cd backend-api
   pip install -r requirements.txt
   ```

4. **Configure Environment:**
   Create `.env` file with:
   ```bash
   DEBUG=True
   SECRET_KEY=your-secret-key
   DB_NAME=sentinel_db
   DB_USER=sentinel
   DB_PASSWORD=your_password
   DB_HOST=localhost
   TRANSLATION_SERVICE_URL=http://localhost:8001
   NER_SERVICE_URL=http://localhost:8002
   ```

5. **Run Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Development Server:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

### Docker Deployment

1. **Build Image:**
   ```bash
   docker build -t project-sentinel/backend-api .
   ```

2. **Run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

## Integration with NLP Services

The backend integrates with the NLP processing pipeline:

1. **Language Detection**: Automatically detects French/English content
2. **Translation Service**: Calls translation API if content is not in English
3. **NER Service**: Extracts named entities from English text
4. **Location Geocoding**: Maps location entities to coordinates

### Processing Flow

```
Raw Article → Language Detection → Translation (if needed) → 
NER Extraction → Location Geocoding → Database Storage → 
API Response
```

## GeoDjango Features

- **PostGIS Integration**: Full spatial database support
- **Location Mapping**: Articles mapped to geographic coordinates
- **Spatial Queries**: Distance-based and region-based filtering
- **GeoJSON API**: Standards-compliant geographic data format
- **Admin Map Interface**: Interactive map in Django admin

## Security Features

- **Classification Levels**: UNCLASSIFIED, RESTRICTED, CONFIDENTIAL, SECRET
- **CORS Configuration**: Controlled frontend access
- **Input Validation**: Comprehensive data validation
- **SQL Injection Protection**: Django ORM security
- **XSS Protection**: Built-in Django security middleware

## Monitoring & Logging

- **Structured Logging**: JSON-formatted application logs
- **Processing Logs**: Detailed operation tracking
- **Health Checks**: Service availability monitoring
- **Statistics API**: System performance metrics

## Database Migrations

Key migrations include:

1. **Initial Migration**: Creates NewsArticle and ProcessingLog models
2. **GeoDjango Setup**: Adds PostGIS spatial fields
3. **Indexes**: Performance optimization indexes

Run migrations:
```bash
python manage.py makemigrations dashboard
python manage.py migrate
```

## Testing

Run the test suite:
```bash
# Unit tests
python manage.py test

# With coverage
pytest --cov=sentinel_core

# Integration tests
pytest tests/integration/
```

## Production Deployment

### Environment Variables

Set in production environment:

```bash
DEBUG=False
SECRET_KEY=production-secret-key
ALLOWED_HOSTS=api.sentinel.cdf.gov.cm
DB_HOST=postgres-service
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Docker Production Setup

```bash
# Build production image
docker build -f Dockerfile.prod -t project-sentinel/backend-api:prod .

# Deploy with Kubernetes
kubectl apply -f kubernetes/
```

### Performance Tuning

- **Database Indexes**: Optimized for common queries
- **Connection Pooling**: PostgreSQL connection management
- **Caching**: Redis-based response caching
- **Static Files**: WhiteNoise for static file serving

## Troubleshooting

### Common Issues

1. **GeoDjango Setup**: Ensure GDAL/GEOS libraries are installed
2. **Database Connection**: Check PostgreSQL service and credentials
3. **NLP Service Integration**: Verify translation/NER services are running
4. **Migration Errors**: Run migrations in correct order

### Debugging

```bash
# Enable debug mode
export DEBUG=True

# Detailed logging
export LOG_LEVEL=DEBUG

# Database query logging
export DJANGO_LOG_LEVEL=DEBUG
```

## API Documentation

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **Schema**: `http://localhost:8000/api/schema/`

## Contributing

1. Follow Django best practices
2. Write comprehensive tests
3. Document API changes
4. Use proper commit messages
5. Security review for sensitive features

## License

**RESTRICTED** - Cameroon Defense Force Internal Use Only

---

*This system is classified RESTRICTED and is intended for authorized personnel only.*
