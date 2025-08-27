# PROJECT SENTINEL - PRODUCTION DEPLOYMENT GUIDE

**Classification:** RESTRICTED  
**Authority:** Cameroon Defense Force  
**Version:** 1.0  
**Date:** 2024

---

## 🚀 **DEPLOYMENT SEQUENCE EXECUTION**

This guide provides the complete deployment sequence for Project Sentinel OSINT Analysis System in production environment.

---

## 📋 **PRE-DEPLOYMENT CHECKLIST**

### **Infrastructure Requirements:**
- ✅ Kubernetes cluster (v1.25+) with minimum 16 cores, 32GB RAM
- ✅ PostgreSQL 15 with PostGIS extension support
- ✅ Docker registry access (registry.cdf.cm)
- ✅ Persistent storage class configured (minimum 500GB)
- ✅ Network policies enabled
- ✅ SSL/TLS certificates for external access

### **Access Requirements:**
- ✅ `kubectl` configured for production cluster
- ✅ Docker registry credentials
- ✅ Database admin credentials
- ✅ Mapbox API token for frontend

---

## 🔄 **DEPLOYMENT SEQUENCE**

### **PHASE 1: DevOps Lead - Initialize Production Environment**

#### 1.1 Create Production Namespace
```bash
# Create dedicated namespace for Project Sentinel
kubectl create namespace sentinel-prod

# Set as default namespace for remaining commands
kubectl config set-context --current --namespace=sentinel-prod
```

#### 1.2 Deploy PostgreSQL Database
```bash
# Apply PostgreSQL deployment and service
kubectl apply -f infrastructure/kubernetes/ --namespace=sentinel-prod

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s -n sentinel-prod

# Verify PostgreSQL is running
kubectl get pods -n sentinel-prod -l app=postgres
```

#### 1.3 Initialize PostGIS Extension
```bash
# Get PostgreSQL pod name
POSTGRES_POD=$(kubectl get pods -n sentinel-prod -l app=postgres -o jsonpath='{.items[0].metadata.name}')

# Create PostGIS extension
kubectl exec -it $POSTGRES_POD -n sentinel-prod -- psql -U postgres -d sentinel_db -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# Verify PostGIS installation
kubectl exec -it $POSTGRES_POD -n sentinel-prod -- psql -U postgres -d sentinel_db -c "SELECT PostGIS_Version();"
```

### **PHASE 2: ML Engineer - Deploy NLP Services**

#### 2.1 Build and Push NLP Container Images
```bash
# Build translation service
cd nlp-models/
docker build -t registry.cdf.cm/sentinel/translation-service:prod -f Dockerfile .
docker push registry.cdf.cm/sentinel/translation-service:prod

# Build NER service
docker build -t registry.cdf.cm/sentinel/ner-service:prod -f ner_dockerfile .
docker push registry.cdf.cm/sentinel/ner-service:prod
```

#### 2.2 Deploy NLP Services to Kubernetes
```bash
# Deploy translation service
kubectl apply -f deployment/kubernetes/translation-service.yaml -n sentinel-prod

# Deploy NER service
kubectl apply -f deployment/kubernetes/ner-service.yaml -n sentinel-prod

# Wait for services to be ready
kubectl wait --for=condition=ready pod -l app=translation-service --timeout=300s -n sentinel-prod
kubectl wait --for=condition=ready pod -l app=ner-service --timeout=300s -n sentinel-prod

# Verify NLP services
kubectl get pods -n sentinel-prod -l component=nlp
```

### **PHASE 3: Backend Team - Database Migration & API Deployment**

#### 3.1 Database Migration
```bash
cd backend-api/

# Create production settings if not exists
cp settings.py settings_production.py

# Run database migrations
python manage.py migrate --settings=sentinel_core.settings_production

# Create superuser for admin access
python manage.py createsuperuser --settings=sentinel_core.settings_production
```

#### 3.2 Build and Deploy Django Backend
```bash
# Collect static files
python manage.py collectstatic --noinput --settings=sentinel_core.settings_production

# Build backend container
docker build -t registry.cdf.cm/sentinel/backend-api:prod -f Dockerfile .
docker push registry.cdf.cm/sentinel/backend-api:prod

# Deploy to Kubernetes
kubectl apply -f deployment/kubernetes/backend-api.yaml -n sentinel-prod

# Wait for deployment
kubectl wait --for=condition=ready pod -l app=backend-api --timeout=300s -n sentinel-prod
```

### **PHASE 4: Frontend Team - Production Build & Deployment**

#### 4.1 Build Frontend Application
```bash
cd frontend-dashboard/

# Install dependencies
npm ci --production

# Create production build
VITE_API_BASE_URL=https://api.sentinel.cdf.cm \
VITE_MAPBOX_ACCESS_TOKEN=$MAPBOX_TOKEN \
npm run build
```

#### 4.2 Deploy Frontend Dashboard
```bash
# Build frontend container
docker build -t registry.cdf.cm/sentinel/dashboard:prod -f Dockerfile .
docker push registry.cdf.cm/sentinel/dashboard:prod

# Deploy to Kubernetes
kubectl apply -f deployment/kubernetes/frontend-dashboard.yaml -n sentinel-prod

# Wait for deployment
kubectl wait --for=condition=ready pod -l app=frontend-dashboard --timeout=300s -n sentinel-prod
```

---

## 🔐 **SECURITY PROTOCOLS**

### **Immediate Security Actions:**

#### 1. Enable Mutual TLS
```bash
# Apply network policies
kubectl apply -f deployment/kubernetes/network-policies.yaml -n sentinel-prod

# Install and configure Istio service mesh (if available)
istioctl install --set values.defaultRevision=default
kubectl label namespace sentinel-prod istio-injection=enabled
```

#### 2. Rotate Credentials
```bash
# Generate new database password
NEW_DB_PASSWORD=$(openssl rand -base64 32)

# Update database secret
kubectl create secret generic postgres-secret \
  --from-literal=POSTGRES_DB=sentinel_db \
  --from-literal=POSTGRES_USER=sentinel \
  --from-literal=POSTGRES_PASSWORD="$NEW_DB_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f - -n sentinel-prod

# Restart PostgreSQL to apply new credentials
kubectl rollout restart deployment postgres-deployment -n sentinel-prod
```

#### 3. Enable Audit Logging
```bash
# Apply audit logging configuration
kubectl apply -f deployment/kubernetes/audit-policy.yaml -n sentinel-prod
```

---

## 📊 **MONITORING & ALERTING**

### **Deploy Monitoring Stack:**

#### 1. Prometheus & Grafana
```bash
# Add Helm repositories
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set grafana.adminPassword="$GRAFANA_ADMIN_PASSWORD"

# Apply Project Sentinel monitoring configuration
kubectl apply -f deployment/monitoring/ -n sentinel-prod
```

#### 2. Configure Alerts
```bash
# Apply alert rules
kubectl apply -f deployment/monitoring/alert-rules.yaml -n monitoring

# Configure alert manager
kubectl apply -f deployment/monitoring/alertmanager-config.yaml -n monitoring
```

---

## ✅ **VERIFICATION & TESTING**

### **System Health Checks:**

#### 1. Database Connectivity
```bash
# Test PostgreSQL connection
kubectl exec -it $(kubectl get pods -n sentinel-prod -l app=postgres -o jsonpath='{.items[0].metadata.name}') -n sentinel-prod -- pg_isready

# Test PostGIS functionality
kubectl exec -it $(kubectl get pods -n sentinel-prod -l app=postgres -o jsonpath='{.items[0].metadata.name}') -n sentinel-prod -- psql -U postgres -d sentinel_db -c "SELECT ST_Distance(ST_MakePoint(11.5021, 3.8480), ST_MakePoint(9.7679, 4.0511));"
```

#### 2. NLP Services Health
```bash
# Test translation service
kubectl port-forward -n sentinel-prod svc/translation-service 8001:8000 &
curl -X POST http://localhost:8001/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Bonjour le Cameroun", "source_lang": "fr"}'

# Test NER service
kubectl port-forward -n sentinel-prod svc/ner-service 8002:8000 &
curl -X POST http://localhost:8002/analyze-entities \
  -H "Content-Type: application/json" \
  -d '{"text": "Paul Biya visited Yaoundé yesterday."}'
```

#### 3. Backend API Health
```bash
# Test Django API
kubectl port-forward -n sentinel-prod svc/backend-api 8000:8000 &
curl http://localhost:8000/health/
curl http://localhost:8000/api/v1/statistics/
```

#### 4. Frontend Dashboard Access
```bash
# Get frontend service details
kubectl get svc frontend-dashboard -n sentinel-prod

# Test dashboard accessibility
curl -I http://dashboard.sentinel.cdf.cm/health
```

---

## 📈 **OPERATIONAL CAPABILITY METRICS**

### **Initial Operational Capability (IOC) - 24 Hours:**
- [ ] All 5 services running and healthy
- [ ] Database migrations completed successfully
- [ ] Minimum 5 news sources configured and ingesting data
- [ ] Real-time processing pipeline operational (translation + NER)
- [ ] Dashboard accessible to authorized personnel
- [ ] First operational intelligence report generated

### **Full Operational Capability (FOC) - 72 Hours:**
- [ ] Complete news source catalog integrated (15+ sources)
- [ ] Performance benchmarks met:
  - [ ] API response time < 500ms (95th percentile)
  - [ ] Processing pipeline throughput > 100 articles/hour
  - [ ] System uptime > 99.5%
- [ ] Monitoring and alerting fully operational
- [ ] Security protocols implemented and tested
- [ ] Analyst training completed
- [ ] First comprehensive system health report generated

---

## 🚨 **TROUBLESHOOTING**

### **Common Issues:**

#### PostgreSQL Issues:
```bash
# Check PostgreSQL logs
kubectl logs -f -n sentinel-prod -l app=postgres

# Restart PostgreSQL if needed
kubectl rollout restart deployment postgres-deployment -n sentinel-prod
```

#### NLP Services Issues:
```bash
# Check service logs
kubectl logs -f -n sentinel-prod -l component=nlp

# Check resource usage
kubectl top pods -n sentinel-prod -l component=nlp
```

#### Network Connectivity Issues:
```bash
# Test inter-service communication
kubectl exec -it $(kubectl get pods -n sentinel-prod -l app=backend-api -o jsonpath='{.items[0].metadata.name}') -n sentinel-prod -- wget -qO- http://translation-service:8000/health
```

---

## 📞 **ESCALATION PROCEDURES**

### **On-Call Rotation:**
1. **Primary**: Senior DevOps Engineer
2. **Secondary**: Lead Backend Developer
3. **Escalation**: ML Engineering Lead
4. **Critical**: Project Manager + CDF Command

### **Contact Channels:**
- **Emergency**: Secure radio channel ALPHA-7
- **Non-urgent**: Encrypted messaging system
- **Documentation**: Internal wiki system

---

## 🔄 **MAINTENANCE PROCEDURES**

### **Daily:**
- Monitor system health dashboard
- Check processing pipeline statistics
- Verify data ingestion rates

### **Weekly:**
- Review system performance metrics
- Update news source configurations
- Security patch assessment

### **Monthly:**
- Full system backup and disaster recovery test
- Performance optimization review
- Capacity planning assessment

---

**This deployment guide ensures Project Sentinel achieves Full Operational Capability within 72 hours while maintaining security and reliability standards required for defense operations.**

---

*Classification: RESTRICTED - Cameroon Defense Force Internal Use Only*
