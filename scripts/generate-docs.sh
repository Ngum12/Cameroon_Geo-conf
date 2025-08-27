#!/bin/bash

# Project Sentinel - Documentation Generator
# Cameroon Defense Force - RESTRICTED
# Generates comprehensive deployment and operational documentation

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
OUTPUT_DIR="./generated-docs"
PRODUCTION_MODE=false
INCLUDE_SENSITIVE=false

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --production         Generate production-specific documentation"
    echo "  --output-dir DIR     Output directory (default: ./generated-docs)"
    echo "  --include-sensitive  Include sensitive configuration examples"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --production                    # Generate production docs"
    echo "  $0 --output-dir /tmp/docs         # Custom output directory"
    echo "  $0 --include-sensitive            # Include sensitive configs"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --production)
            PRODUCTION_MODE=true
            shift
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --include-sensitive)
            INCLUDE_SENSITIVE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            ;;
    esac
done

# Setup output directory
setup_output_dir() {
    log "Setting up output directory: $OUTPUT_DIR"
    
    rm -rf "$OUTPUT_DIR" 2>/dev/null || true
    mkdir -p "$OUTPUT_DIR"/{deployment,operations,troubleshooting,security,architecture}
    
    # Create classification header
    cat > "$OUTPUT_DIR/CLASSIFICATION.md" << 'EOF'
# SECURITY CLASSIFICATION

**🇨🇲 CAMEROON DEFENSE FORCE - RESTRICTED**

All documents in this directory are classified as **RESTRICTED** and are intended for authorized personnel only.

**Distribution:** Authorized Project Sentinel personnel and operations teams only.

**Handling Instructions:**
- Do not distribute outside authorized personnel
- Store in secure systems only
- Review classification before sharing any content
- Report any security incidents immediately

---
EOF
    
    log "Output directory structure created"
}

# Generate system overview
generate_system_overview() {
    log "Generating system overview documentation..."
    
    cat > "$OUTPUT_DIR/architecture/SYSTEM_OVERVIEW.md" << 'EOF'
# Project Sentinel - System Architecture Overview

## System Description
Project Sentinel is a comprehensive OSINT (Open Source Intelligence) analysis system designed for the Cameroon Defense Force. The system provides real-time data collection, processing, and visualization capabilities for intelligence analysis.

## Architecture Components

### 1. Data Ingestion Layer
- **Scrapy Web Crawler**: Automated data collection from news sources
- **Data Validation**: Content verification and deduplication
- **Rate Limiting**: Respectful data collection practices

### 2. NLP Processing Pipeline
- **Translation Service**: Multi-language translation using M2M100
- **Named Entity Recognition**: Entity extraction using XLM-RoBERTa
- **Geolocation Processing**: Geographic information extraction

### 3. Backend API Layer
- **Django REST Framework**: Core API services
- **GeoDjango**: Spatial data processing
- **PostgreSQL + PostGIS**: Geospatial database
- **Redis**: Caching and message queuing

### 4. Frontend Dashboard
- **React + TypeScript**: Modern web interface
- **Mapbox Integration**: Interactive mapping
- **Material-UI**: Professional UI components
- **Real-time Updates**: Live data visualization

### 5. Infrastructure Layer
- **Kubernetes**: Container orchestration
- **Docker**: Service containerization
- **Prometheus + Grafana**: Monitoring and alerting
- **Network Security**: Zero-trust networking

## Data Flow
1. **Collection**: Scrapy crawlers collect news articles
2. **Translation**: Non-English content translated to English
3. **Analysis**: NER service extracts entities and locations
4. **Storage**: Processed data stored in PostGIS database
5. **Visualization**: Dashboard displays intelligence on interactive map

## Security Features
- Network isolation and policies
- Encrypted data transmission
- Access control and authentication
- Audit logging
- Secure secrets management

## Scalability
- Horizontal pod autoscaling
- Load balancing
- Distributed processing
- Efficient resource utilization
EOF

    log "System overview documentation generated"
}

# Generate deployment documentation
generate_deployment_docs() {
    log "Generating deployment documentation..."
    
    # Quick Start Guide
    cat > "$OUTPUT_DIR/deployment/QUICK_START.md" << 'EOF'
# Project Sentinel - Quick Start Guide

## Prerequisites
- Kubernetes cluster (v1.24+)
- kubectl configured
- Docker registry access
- 100GB+ storage available

## Rapid Deployment (5 minutes)

### 1. Clone Repository
```bash
git clone https://github.com/cameroon-defense/project-sentinel.git
cd project-sentinel
```

### 2. Set Environment Variables
```bash
export REGISTRY_URL="registry.cdf.cm"
export DB_PASSWORD="secure_password_2024"
export DJANGO_SECRET_KEY="your-secret-key"
export MAPBOX_TOKEN="your-mapbox-token"
```

### 3. Deploy Infrastructure
```bash
# Create namespace
kubectl create namespace sentinel-prod

# Deploy PostgreSQL
kubectl apply -f infrastructure/kubernetes/postgresql/ -n sentinel-prod

# Deploy Redis
kubectl apply -f infrastructure/kubernetes/redis/ -n sentinel-prod
```

### 4. Build and Deploy Services
```bash
# Build images
./scripts/build-images.sh --production --push

# Deploy NLP services
kubectl apply -f nlp-models/kubernetes/ -n sentinel-prod

# Deploy backend
kubectl apply -f backend-api/kubernetes/ -n sentinel-prod

# Deploy frontend
kubectl apply -f frontend-dashboard/kubernetes/ -n sentinel-prod
```

### 5. Verify Deployment
```bash
./scripts/status-check.sh --production
```

## Access Points
- Dashboard: https://sentinel.cdf.cm
- API: https://api.sentinel.cdf.cm
- Monitoring: https://grafana.sentinel.cdf.cm

## Next Steps
- Review full deployment guide
- Configure monitoring alerts
- Set up backup procedures
- Review security settings
EOF

    # Troubleshooting Guide
    cat > "$OUTPUT_DIR/troubleshooting/COMMON_ISSUES.md" << 'EOF'
# Project Sentinel - Troubleshooting Guide

## Common Issues and Solutions

### 1. Pod Startup Issues

#### Pods Stuck in Pending State
**Symptoms**: Pods show `Pending` status
**Causes**: 
- Insufficient cluster resources
- PVC not bound
- Node selector constraints

**Solutions**:
```bash
# Check cluster resources
kubectl top nodes
kubectl describe pod <pod-name> -n sentinel-prod

# Check PVC status
kubectl get pvc -n sentinel-prod

# Check node availability
kubectl get nodes -o wide
```

#### Image Pull Errors
**Symptoms**: `ImagePullBackOff` or `ErrImagePull`
**Solutions**:
```bash
# Check registry credentials
kubectl get secrets -n sentinel-prod registry-credentials

# Verify image exists
docker pull registry.cdf.cm/sentinel/backend:prod

# Re-create registry secret if needed
kubectl create secret docker-registry registry-credentials \
  --docker-server=registry.cdf.cm \
  --docker-username=<username> \
  --docker-password=<password> \
  -n sentinel-prod
```

### 2. Database Connection Issues

#### Cannot Connect to Database
**Symptoms**: Backend API fails with database errors
**Solutions**:
```bash
# Check PostgreSQL pod status
kubectl get pods -n sentinel-prod -l app=postgres

# Test database connectivity
kubectl exec -it deployment/postgres -n sentinel-prod -- psql -U postgres -c "SELECT 1;"

# Check database credentials
kubectl get secret postgres-secret -n sentinel-prod -o yaml
```

#### PostGIS Extension Missing
**Symptoms**: GeoDjango errors about PostGIS
**Solutions**:
```bash
# Install PostGIS extension
kubectl exec -it deployment/postgres -n sentinel-prod -- psql -U postgres -d sentinel_db -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### 3. NLP Service Issues

#### Model Loading Errors
**Symptoms**: Translation or NER services fail to start
**Solutions**:
```bash
# Check model cache PVC
kubectl get pvc -n sentinel-prod | grep model

# Clear model cache if corrupted
kubectl exec -it deployment/translation-service -n sentinel-prod -- rm -rf /app/.cache/*

# Restart service to re-download models
kubectl rollout restart deployment/translation-service -n sentinel-prod
```

### 4. Frontend Access Issues

#### 502 Bad Gateway
**Symptoms**: Frontend shows 502 error
**Solutions**:
```bash
# Check backend API status
kubectl get pods -n sentinel-prod -l app=backend-api

# Check service endpoints
kubectl get endpoints backend-api -n sentinel-prod

# Verify ingress configuration
kubectl get ingress -n sentinel-prod
```

### 5. Performance Issues

#### High Memory Usage
**Solutions**:
```bash
# Check resource usage
kubectl top pods -n sentinel-prod

# Scale up if needed
kubectl scale deployment <service> --replicas=3 -n sentinel-prod

# Check HPA status
kubectl get hpa -n sentinel-prod
```

## Emergency Procedures

### Complete System Recovery
```bash
# 1. Emergency backup
./scripts/backup.sh --full

# 2. System status check
./scripts/status-check.sh --production

# 3. If recovery needed
./scripts/restore.sh --backup latest

# 4. Emergency rollback if needed
./scripts/rollback.sh --version previous
```

### Getting Help
1. Check system logs: `kubectl logs -n sentinel-prod <pod-name>`
2. Run diagnostics: `./scripts/status-check.sh --verbose`
3. Review monitoring dashboards
4. Contact Project Sentinel operations team
EOF

    log "Deployment documentation generated"
}

# Generate operations documentation
generate_operations_docs() {
    log "Generating operations documentation..."
    
    cat > "$OUTPUT_DIR/operations/DAILY_OPERATIONS.md" << 'EOF'
# Project Sentinel - Daily Operations Guide

## Daily Checklist

### Morning Startup (08:00)
- [ ] Run system status check: `./scripts/status-check.sh --production`
- [ ] Review overnight monitoring alerts
- [ ] Check data ingestion statistics
- [ ] Verify all services are healthy
- [ ] Review security logs for anomalies

### Midday Check (12:00)
- [ ] Monitor resource usage trends
- [ ] Check processing queue lengths
- [ ] Verify API response times < 500ms
- [ ] Review error rates (should be < 1%)
- [ ] Check backup completion status

### Evening Shutdown (18:00)
- [ ] Run final status check
- [ ] Initiate daily backup: `./scripts/backup.sh --full`
- [ ] Review daily statistics report
- [ ] Plan any maintenance windows
- [ ] Update operational log

## Weekly Tasks

### Monday - System Health Review
- Run comprehensive diagnostics
- Review performance trends
- Update security patches if available
- Clean up old logs and temporary files

### Wednesday - Backup Verification
- Test restore procedure: `./scripts/restore.sh --test`
- Verify backup integrity
- Update disaster recovery documentation
- Review data retention policies

### Friday - Security Audit
- Review access logs
- Check security alert history
- Verify network policy effectiveness
- Update security documentation

## Monthly Tasks
- [ ] Full system performance review
- [ ] Update operational documentation
- [ ] Security vulnerability assessment
- [ ] Disaster recovery drill
- [ ] Capacity planning review

## Emergency Contacts
- Operations Team: +237-XXX-XXXX-XX
- Security Team: +237-XXX-XXXX-XX
- Infrastructure Team: +237-XXX-XXXX-XX
- Project Manager: +237-XXX-XXXX-XX
EOF

    # Monitoring Guide
    cat > "$OUTPUT_DIR/operations/MONITORING_GUIDE.md" << 'EOF'
# Project Sentinel - Monitoring and Alerting Guide

## Key Metrics to Monitor

### System Health Metrics
1. **Pod Status**
   - All pods should be in `Running` state
   - Ready containers should equal desired containers
   - Alert if any pod restarts > 5 times/hour

2. **Resource Usage**
   - CPU usage < 80% sustained
   - Memory usage < 85% sustained  
   - Disk usage < 90%
   - Alert on resource exhaustion

3. **API Performance**
   - Response time < 500ms (95th percentile)
   - Error rate < 1%
   - Request throughput monitoring
   - Alert on performance degradation

### Application Metrics
1. **Data Ingestion**
   - Articles processed per hour
   - Translation service latency
   - NER processing success rate
   - Failed ingestion attempts

2. **Database Performance**
   - Connection pool usage
   - Query execution time
   - Database size growth
   - Backup completion status

## Alert Configuration

### Critical Alerts (Immediate Response)
- Any service down > 5 minutes
- Database connection failures
- Persistent volume errors
- Security policy violations
- API error rate > 5%

### Warning Alerts (Response within 1 hour)
- High resource usage (>80%)
- Slow API responses (>1s)
- Failed backup jobs
- Model loading failures
- Network connectivity issues

### Info Alerts (Response within 4 hours)
- Unusual traffic patterns
- Configuration changes
- Completed maintenance tasks
- Performance trend alerts

## Grafana Dashboards

### Executive Dashboard
- System health overview
- Key performance indicators
- Current operational status
- Recent alerts summary

### Technical Dashboard
- Detailed resource metrics
- Service-specific performance
- Database statistics
- Network traffic analysis

### Security Dashboard
- Access attempt monitoring
- Failed authentication logs
- Network policy violations
- Vulnerability scan results

## Prometheus Alerting Rules

Key alerting rules configured:

```yaml
# High CPU Usage
alert: HighCPUUsage
expr: cpu_usage > 80
for: 5m
severity: warning

# Service Down
alert: ServiceDown
expr: up == 0
for: 1m
severity: critical

# High Memory Usage
alert: HighMemoryUsage
expr: memory_usage > 85
for: 5m
severity: warning

# Database Connection Failure
alert: DatabaseDown
expr: database_up == 0
for: 1m
severity: critical
```

## Response Procedures

### Critical Alert Response
1. Acknowledge alert immediately
2. Run: `./scripts/status-check.sh --production`
3. Identify root cause
4. Implement immediate fix
5. Document incident
6. Update monitoring if needed

### Performance Degradation
1. Check resource utilization
2. Scale services if needed
3. Review recent changes
4. Consider rollback if necessary
5. Monitor for improvement

### Security Incident
1. Isolate affected components
2. Document all evidence
3. Report to security team
4. Implement containment
5. Perform forensic analysis
EOF

    log "Operations documentation generated"
}

# Generate security documentation
generate_security_docs() {
    log "Generating security documentation..."
    
    cat > "$OUTPUT_DIR/security/SECURITY_POLICY.md" << 'EOF'
# Project Sentinel - Security Policy

## Security Classification
**RESTRICTED - CAMEROON DEFENSE FORCE**

## Access Control

### Role-Based Access Control (RBAC)
1. **Administrator** - Full system access
2. **Operator** - Operations and monitoring access
3. **Analyst** - Dashboard and API read access
4. **Auditor** - Log and audit access only

### Authentication Requirements
- Multi-factor authentication mandatory
- Password complexity requirements
- Session timeout: 4 hours
- Account lockout after 5 failed attempts

### Network Security
- Zero-trust network model
- Pod-to-pod encryption (mTLS)
- Network policies restrict traffic
- DMZ isolation for external interfaces

## Data Protection

### Classification Levels
1. **TOP SECRET** - Critical intelligence data
2. **SECRET** - Processed intelligence reports
3. **CONFIDENTIAL** - Raw data and metadata
4. **RESTRICTED** - System configuration

### Encryption Standards
- Data at rest: AES-256
- Data in transit: TLS 1.3
- Key management: Kubernetes secrets + external HSM
- Certificate rotation: 90 days

### Data Retention
- Raw articles: 30 days
- Processed intelligence: 6 months
- Audit logs: 1 year
- Backup data: 3 months

## Security Controls

### Container Security
- Non-root containers only
- Read-only root filesystems
- Resource limits enforced
- Regular vulnerability scanning
- Image signing and verification

### Kubernetes Security
- Pod Security Standards enforced
- Network policies active
- RBAC configured
- Admission controllers enabled
- Regular security updates

### Monitoring and Auditing
- All API calls logged
- User activity tracked
- File integrity monitoring
- Intrusion detection active
- Security event correlation

## Incident Response

### Classification Levels
1. **P1 - Critical**: Data breach, system compromise
2. **P2 - High**: Unauthorized access, service disruption
3. **P3 - Medium**: Policy violation, suspicious activity
4. **P4 - Low**: Configuration issue, minor violation

### Response Procedures
1. **Detection**: Automated monitoring + manual reporting
2. **Containment**: Isolate affected systems
3. **Investigation**: Forensic analysis
4. **Eradication**: Remove threats and vulnerabilities
5. **Recovery**: Restore services securely
6. **Lessons Learned**: Update policies and procedures

## Compliance Requirements
- Cameroon Defense Force security standards
- ISO 27001 controls implementation
- Regular security assessments
- Penetration testing (quarterly)
- Security awareness training

## Contact Information
- **Security Officer**: +237-XXX-XXXX-XX
- **Incident Response Team**: security-incident@cdf.cm
- **Emergency Contact**: +237-XXX-XXXX-XX (24/7)
EOF

    if [[ "$INCLUDE_SENSITIVE" == true ]]; then
        log "Including sensitive configuration examples..."
        
        cat > "$OUTPUT_DIR/security/SENSITIVE_CONFIGS.md" << 'EOF'
# Project Sentinel - Sensitive Configuration Examples

⚠️ **WARNING: This document contains sensitive information**
⚠️ **Restrict access to authorized personnel only**

## Database Configuration

### Production Database Connection
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: sentinel-prod
type: Opaque
data:
  POSTGRES_DB: c2VudGluZWxfZGI=  # sentinel_db
  POSTGRES_USER: cG9zdGdyZXM=      # postgres  
  POSTGRES_PASSWORD: <BASE64_ENCODED_PASSWORD>
```

### Django Settings
```python
# settings_production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'sentinel_db',
        'USER': 'postgres',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'postgres-service.sentinel-prod.svc.cluster.local',
        'PORT': '5432',
    }
}

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = ['api.sentinel.cdf.cm', 'localhost']
```

## Registry Configuration

### Docker Registry Secret
```bash
kubectl create secret docker-registry registry-credentials \
  --docker-server=registry.cdf.cm \
  --docker-username=sentinel-deploy \
  --docker-password=<REGISTRY_PASSWORD> \
  --namespace=sentinel-prod
```

## SSL/TLS Certificates

### Certificate Creation
```bash
# Create private key
openssl genrsa -out sentinel.key 2048

# Create certificate signing request
openssl req -new -key sentinel.key -out sentinel.csr

# Create certificate secret
kubectl create secret tls sentinel-tls \
  --cert=sentinel.crt \
  --key=sentinel.key \
  --namespace=sentinel-prod
```

## Monitoring Credentials

### Grafana Admin Password
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: grafana-credentials
  namespace: monitoring
type: Opaque
data:
  admin-user: YWRtaW4=  # admin
  admin-password: <BASE64_ENCODED_PASSWORD>
```

## External API Keys

### Mapbox Token
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mapbox-secret
  namespace: sentinel-prod
type: Opaque
data:
  token: <BASE64_ENCODED_MAPBOX_TOKEN>
```

⚠️ **SECURITY REMINDERS:**
- Never commit these values to version control
- Rotate credentials regularly (90 days)
- Use strong, unique passwords
- Monitor access to this documentation
- Report any credential compromise immediately
EOF
    fi
    
    log "Security documentation generated"
}

# Generate API documentation
generate_api_docs() {
    log "Generating API documentation..."
    
    cat > "$OUTPUT_DIR/deployment/API_REFERENCE.md" << 'EOF'
# Project Sentinel - API Reference

## Base URL
- **Production**: `https://api.sentinel.cdf.cm`
- **Development**: `http://localhost:8000`

## Authentication
All API endpoints require authentication via JWT tokens or API keys.

```bash
# Get authentication token
curl -X POST https://api.sentinel.cdf.cm/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

## Core Endpoints

### Health Check
**GET** `/health/`

Returns system health status.

```bash
curl https://api.sentinel.cdf.cm/health/
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-27T10:30:00Z",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "nlp": "healthy"
  }
}
```

### Articles
**GET** `/api/v1/articles/`

Retrieve processed articles.

**Parameters:**
- `limit`: Number of results (default: 20, max: 100)
- `offset`: Pagination offset
- `source`: Filter by news source
- `date_from`: Start date (YYYY-MM-DD)
- `date_to`: End date (YYYY-MM-DD)

```bash
curl -H "Authorization: Bearer <token>" \
  https://api.sentinel.cdf.cm/api/v1/articles/?limit=10&source=bbc
```

**Response:**
```json
{
  "count": 1250,
  "next": "https://api.sentinel.cdf.cm/api/v1/articles/?offset=10",
  "previous": null,
  "results": [
    {
      "id": 1,
      "url": "https://example.com/article",
      "title": "Example Article",
      "source": "BBC",
      "published_date": "2024-01-27T08:00:00Z",
      "processed_json": {
        "entities": [...],
        "locations": [...],
        "sentiment": "neutral"
      },
      "location": {
        "type": "Point",
        "coordinates": [11.5021, 3.8480]
      }
    }
  ]
}
```

### GeoJSON Events
**GET** `/api/v1/events/geojson/`

Get events in GeoJSON format for mapping.

```bash
curl -H "Authorization: Bearer <token>" \
  https://api.sentinel.cdf.cm/api/v1/events/geojson/
```

**Response:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [11.5021, 3.8480]
      },
      "properties": {
        "title": "Article Title",
        "source": "BBC",
        "url": "https://example.com/article",
        "entities": ["Cameroon", "Government"],
        "event_type": "Political"
      }
    }
  ]
}
```

### Statistics
**GET** `/api/v1/statistics/`

Get system statistics and metrics.

```bash
curl -H "Authorization: Bearer <token>" \
  https://api.sentinel.cdf.cm/api/v1/statistics/
```

**Response:**
```json
{
  "articles_today": 156,
  "articles_total": 12450,
  "sources_active": 15,
  "processing_queue": 23,
  "last_update": "2024-01-27T10:25:00Z",
  "top_entities": [
    {"name": "Cameroon", "count": 89},
    {"name": "Yaoundé", "count": 67}
  ]
}
```

## NLP Service Endpoints

### Translation
**POST** `/nlp/translate/`

Translate text to English.

```bash
curl -X POST https://api.sentinel.cdf.cm/nlp/translate/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"text": "Bonjour le monde", "source_lang": "fr"}'
```

### Named Entity Recognition
**POST** `/nlp/analyze-entities/`

Extract named entities from text.

```bash
curl -X POST https://api.sentinel.cdf.cm/nlp/analyze-entities/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"text": "President Biya visited Douala yesterday."}'
```

## Error Responses

### Common Error Codes
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Error Format
```json
{
  "error": "Authentication required",
  "code": 401,
  "details": "Valid JWT token must be provided"
}
```

## Rate Limiting
- **Default**: 100 requests/hour per user
- **Authenticated**: 1000 requests/hour per user
- **Premium**: 10000 requests/hour per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1643284800
```

## SDKs and Libraries
- **Python**: `pip install sentinel-api-client`
- **JavaScript**: `npm install @cdf/sentinel-client`
- **cURL Examples**: Available in this documentation
EOF

    log "API documentation generated"
}

# Generate final index
generate_index() {
    log "Generating documentation index..."
    
    cat > "$OUTPUT_DIR/README.md" << EOF
# Project Sentinel - Generated Documentation

**🇨🇲 CAMEROON DEFENSE FORCE - RESTRICTED**

Generated on: $(date)
Production Mode: $PRODUCTION_MODE
Include Sensitive: $INCLUDE_SENSITIVE

## Documentation Structure

### 📋 Deployment
- [Quick Start Guide](./deployment/QUICK_START.md) - Get up and running in 5 minutes
- [Production Deployment Guide](../PRODUCTION_DEPLOYMENT_GUIDE.md) - Comprehensive deployment instructions
- [API Reference](./deployment/API_REFERENCE.md) - Complete API documentation

### 🏗️ Architecture  
- [System Overview](./architecture/SYSTEM_OVERVIEW.md) - High-level system architecture
- [Component Diagrams](./architecture/) - Detailed component relationships

### ⚙️ Operations
- [Daily Operations](./operations/DAILY_OPERATIONS.md) - Day-to-day operational procedures
- [Monitoring Guide](./operations/MONITORING_GUIDE.md) - Monitoring and alerting setup

### 🔧 Troubleshooting
- [Common Issues](./troubleshooting/COMMON_ISSUES.md) - Solutions to frequent problems
- [Emergency Procedures](./troubleshooting/) - Crisis response protocols

### 🔒 Security
- [Security Policy](./security/SECURITY_POLICY.md) - Comprehensive security guidelines
$(if [[ "$INCLUDE_SENSITIVE" == true ]]; then echo "- [Sensitive Configurations](./security/SENSITIVE_CONFIGS.md) - Configuration examples (RESTRICTED)"; fi)

## Additional Resources
- [Project Repository](https://github.com/cameroon-defense/project-sentinel)
- [Original Mission Status](../important.md)
- [Operational Scripts](../scripts/)

## Getting Help
1. Check the troubleshooting guide first
2. Review system logs and monitoring dashboards
3. Contact the Project Sentinel operations team
4. Escalate to security team for security issues

---

**Classification**: RESTRICTED - Cameroon Defense Force Internal Use Only
**Version**: $(date +%Y.%m.%d)
**Generated by**: Project Sentinel Documentation Generator
EOF

    log "Documentation index generated"
}

# Create archive
create_archive() {
    log "Creating documentation archive..."
    
    local archive_name="sentinel-docs-$(date +%Y%m%d-%H%M%S)"
    local archive_path="${OUTPUT_DIR}/../${archive_name}.tar.gz"
    
    tar -czf "$archive_path" -C "$(dirname "$OUTPUT_DIR")" "$(basename "$OUTPUT_DIR")"
    
    log "Documentation archive created: $archive_path"
    
    # Calculate size
    local size=$(du -sh "$archive_path" | cut -f1)
    log "Archive size: $size"
}

# Main execution function
main() {
    log "🚀 Starting Project Sentinel documentation generation"
    log "Production mode: $PRODUCTION_MODE"
    log "Output directory: $OUTPUT_DIR" 
    log "Include sensitive: $INCLUDE_SENSITIVE"
    
    setup_output_dir
    generate_system_overview
    generate_deployment_docs
    generate_operations_docs
    generate_security_docs
    generate_api_docs
    generate_index
    create_archive
    
    log "✅ Documentation generation completed successfully!"
    log "📚 Documentation available at: $OUTPUT_DIR"
    
    # Show summary
    echo ""
    echo "📊 Generated Documentation Summary:"
    find "$OUTPUT_DIR" -name "*.md" | wc -l | xargs echo "  Total files:"
    du -sh "$OUTPUT_DIR" | cut -f1 | xargs echo "  Total size:"
    echo ""
}

# Execute main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
