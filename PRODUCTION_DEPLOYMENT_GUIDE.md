# 🚀 Project Sentinel - Production Deployment Guide

🇨🇲 **Cameroon Defense Force - RESTRICTED**

## 📋 Prerequisites

### Infrastructure Requirements
- ✅ Kubernetes cluster (v1.24+)
- ✅ Container registry (private)
- ✅ PostgreSQL 15+ with PostGIS extension
- ✅ Persistent storage (100GB+)
- ✅ Secure network environment

### Required Credentials
```bash
# Environment Variables Needed
export KUBECONFIG="/path/to/kubeconfig"
export REGISTRY_URL="registry.cdf.cm"
export REGISTRY_USERNAME="sentinel-deploy"
export REGISTRY_PASSWORD="secure_password_2024"
export DB_HOST="postgres-prod.cdf.cm"
export DB_PASSWORD="secure_db_password_2024"
export DJANGO_SECRET_KEY="cdf-sentinel-secure-key-@2024"
export MAPBOX_TOKEN="pk.eyJ1..."
```

---

## 🎯 Phase 1: Initial Setup

### 1.1 Clone the Repository
```bash
# On production deployment server
git clone https://github.com/cameroon-defense/project-sentinel.git
cd project-sentinel
```

### 1.2 Setup Environment
```bash
# Create environment file
cat > .env << EOF
KUBECONFIG=/etc/kubernetes/admin.conf
REGISTRY_URL=registry.cdf.cm
REGISTRY_USERNAME=sentinel-deploy
REGISTRY_PASSWORD=${REGISTRY_PASSWORD}
DB_HOST=${DB_HOST}
DB_PASSWORD=${DB_PASSWORD}
DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
MAPBOX_TOKEN=${MAPBOX_TOKEN}
EOF

# Secure the environment file
chmod 600 .env
```

---

## 🐳 Phase 2: Container Building

### 2.1 Build Docker Images
```bash
# Build all images
./scripts/build-images.sh --production --push

# Alternatively build individually
docker build -t ${REGISTRY_URL}/sentinel/backend:prod -f backend-api/Dockerfile.prod .
docker build -t ${REGISTRY_URL}/sentinel/frontend:prod -f frontend-dashboard/Dockerfile.prod .
docker build -t ${REGISTRY_URL}/sentinel/translation:prod -f nlp-models/Dockerfile .
docker build -t ${REGISTRY_URL}/sentinel/ner:prod -f nlp-models/Dockerfile.ner .

# Push to registry
docker push ${REGISTRY_URL}/sentinel/backend:prod
docker push ${REGISTRY_URL}/sentinel/frontend:prod
docker push ${REGISTRY_URL}/sentinel/translation:prod
docker push ${REGISTRY_URL}/sentinel/ner:prod
```

---

## ☸️ Phase 3: Kubernetes Deployment

### 3.1 Create Namespace
```bash
kubectl create namespace sentinel-prod
kubectl label namespace sentinel-prod security-level=restricted
```

### 3.2 Create Secrets
```bash
# Database secret
kubectl create secret generic database-secret \
  --namespace=sentinel-prod \
  --from-literal=password=${DB_PASSWORD} \
  --from-literal=host=${DB_HOST}

# Django secret
kubectl create secret generic django-secret \
  --namespace=sentinel-prod \
  --from-literal=secret-key=${DJANGO_SECRET_KEY}

# Registry credentials
kubectl create secret docker-registry registry-credentials \
  --namespace=sentinel-prod \
  --docker-server=${REGISTRY_URL} \
  --docker-username=${REGISTRY_USERNAME} \
  --docker-password=${REGISTRY_PASSWORD}
```

### 3.3 Deploy Infrastructure
```bash
# Deploy PostgreSQL with PostGIS
kubectl apply -f infrastructure/kubernetes/postgresql/ -n sentinel-prod

# Deploy Redis for caching
kubectl apply -f infrastructure/kubernetes/redis/ -n sentinel-prod
```

### 3.4 Deploy Application Services
```bash
# Deploy NLP services
kubectl apply -f nlp-models/kubernetes/translation-service.yaml -n sentinel-prod
kubectl apply -f nlp-models/kubernetes/ner-service.yaml -n sentinel-prod

# Deploy backend
kubectl apply -f backend-api/kubernetes/ -n sentinel-prod

# Deploy frontend
kubectl apply -f frontend-dashboard/kubernetes/ -n sentinel-prod
```

---

## 🔒 Phase 4: Security Configuration

### 4.1 Network Policies
```bash
# Apply network security policies
kubectl apply -f security/network-policies/ -n sentinel-prod
```

### 4.2 TLS Configuration
```bash
# Apply TLS certificates (if using ingress)
kubectl apply -f security/tls/ -n sentinel-prod
```

---

## 📊 Phase 5: Monitoring Setup

### 5.1 Deploy Monitoring
```bash
# Deploy Prometheus and Grafana
kubectl apply -f monitoring/prometheus/ -n sentinel-prod
kubectl apply -f monitoring/grafana/ -n sentinel-prod
```

### 5.2 Setup Alerts
```bash
# Configure alerting rules
kubectl apply -f monitoring/alerts/ -n sentinel-prod
```

---

## 🧪 Phase 6: Verification

### 6.1 Check Deployment Status
```bash
# Verify all pods are running
kubectl get pods -n sentinel-prod -w

# Check services
kubectl get services -n sentinel-prod

# Verify ingress
kubectl get ingress -n sentinel-prod
```

### 6.2 Test Services
```bash
# Test backend API
curl https://api.sentinel.cdf.cm/health

# Test frontend
curl https://sentinel.cdf.cm

# Test NLP services
curl https://nlp.sentinel.cdf.cm/health
```

### 6.3 Validate Database
```bash
# Check database connection
kubectl exec -it deployment/backend -n sentinel-prod -- python manage.py check_db

# Run migrations
kubectl exec -it deployment/backend -n sentinel-prod -- python manage.py migrate
```

---

## 🔄 Phase 7: Initial Data Load

### 7.1 Load Initial Data
```bash
# Load initial news sources
kubectl exec -it deployment/backend -n sentinel-prod -- python manage.py loaddata initial_sources.json

# Start data ingestion
kubectl exec -it deployment/backend -n sentinel-prod -- python manage.py start_ingestion
```

---

## 🚨 Phase 8: Emergency Procedures

### 8.1 Backup Configuration
```bash
# Create backup script
./scripts/backup.sh --full

# Test restore procedure
./scripts/restore.sh --test
```

### 8.2 Rollback Procedure
```bash
# Rollback to previous version
./scripts/rollback.sh --version previous

# Emergency shutdown
./scripts/emergency-shutdown.sh
```

---

## 📝 Phase 9: Documentation Handover

### 9.1 Generate Documentation
```bash
# Generate deployment documentation
./scripts/generate-docs.sh --production

# Create operator manual
./scripts/create-manual.sh
```

---

## ✅ Final Verification Checklist

- [ ] All pods in Running state
- [ ] Services responding to health checks
- [ ] Database migrations completed
- [ ] SSL certificates valid
- [ ] Monitoring operational
- [ ] Backups configured
- [ ] Documentation complete
- [ ] Security audit passed

---

## 🎯 Deployment Complete

```bash
# Final status check
./scripts/status-check.sh --production

# Display deployment information
echo "Project Sentinel Deployment Complete"
echo "Dashboard URL: https://sentinel.cdf.cm"
echo "API Endpoint: https://api.sentinel.cdf.cm"
echo "Monitoring: https://grafana.sentinel.cdf.cm"
```

---

**Classification:** RESTRICTED - Cameroon Defense Force Internal Use Only
