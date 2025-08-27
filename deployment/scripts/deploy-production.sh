#!/bin/bash

# Project Sentinel Production Deployment Script
# Cameroon Defense Force OSINT Analysis System
# Classification: RESTRICTED

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
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

# Configuration
NAMESPACE="sentinel-prod"
REGISTRY="registry.cdf.cm"
PROJECT_VERSION="${PROJECT_VERSION:-prod}"
MAPBOX_TOKEN="${MAPBOX_TOKEN:-}"
DB_PASSWORD="${DB_PASSWORD:-}"

# Check prerequisites
check_prerequisites() {
    log "Checking deployment prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed or not in PATH"
    fi
    
    # Check docker
    if ! command -v docker &> /dev/null; then
        error "docker is not installed or not in PATH"
    fi
    
    # Check helm
    if ! command -v helm &> /dev/null; then
        warn "helm is not installed - monitoring stack will not be deployed"
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        error "Cannot connect to Kubernetes cluster"
    fi
    
    # Check required environment variables
    if [[ -z "$MAPBOX_TOKEN" ]]; then
        error "MAPBOX_TOKEN environment variable is required"
    fi
    
    if [[ -z "$DB_PASSWORD" ]]; then
        error "DB_PASSWORD environment variable is required"
    fi
    
    log "Prerequisites check completed successfully"
}

# Create namespace and secrets
setup_namespace() {
    log "Setting up namespace and secrets..."
    
    # Create namespace
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # Create registry secret
    kubectl create secret docker-registry registry-secret \
        --docker-server="$REGISTRY" \
        --docker-username="${REGISTRY_USER:-admin}" \
        --docker-password="${REGISTRY_PASSWORD:-admin}" \
        --namespace="$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create PostgreSQL secret
    kubectl create secret generic postgres-secret \
        --from-literal=POSTGRES_DB=sentinel_db \
        --from-literal=POSTGRES_USER=sentinel \
        --from-literal=POSTGRES_PASSWORD="$DB_PASSWORD" \
        --namespace="$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create Django secret
    DJANGO_SECRET=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    kubectl create secret generic django-secret \
        --from-literal=SECRET_KEY="$DJANGO_SECRET" \
        --namespace="$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create Mapbox secret for frontend
    kubectl create secret generic mapbox-secret \
        --from-literal=MAPBOX_ACCESS_TOKEN="$MAPBOX_TOKEN" \
        --namespace="$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log "Namespace and secrets created successfully"
}

# Deploy PostgreSQL database
deploy_database() {
    log "Deploying PostgreSQL database..."
    
    kubectl apply -f infrastructure/kubernetes/postgres-deployment.yaml --namespace="$NAMESPACE"
    kubectl apply -f infrastructure/kubernetes/postgres-service.yaml --namespace="$NAMESPACE"
    
    # Wait for PostgreSQL to be ready
    log "Waiting for PostgreSQL to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s --namespace="$NAMESPACE"
    
    # Initialize PostGIS extension
    log "Initializing PostGIS extension..."
    POSTGRES_POD=$(kubectl get pods -n "$NAMESPACE" -l app=postgres -o jsonpath='{.items[0].metadata.name}')
    kubectl exec -it "$POSTGRES_POD" -n "$NAMESPACE" -- psql -U postgres -d sentinel_db -c "CREATE EXTENSION IF NOT EXISTS postgis;"
    
    log "PostgreSQL database deployed successfully"
}

# Build and push container images
build_and_push_images() {
    log "Building and pushing container images..."
    
    # Login to registry
    echo "${REGISTRY_PASSWORD:-admin}" | docker login "$REGISTRY" --username "${REGISTRY_USER:-admin}" --password-stdin
    
    # Build translation service
    log "Building translation service..."
    cd nlp-models/
    docker build -t "$REGISTRY/sentinel/translation-service:$PROJECT_VERSION" -f Dockerfile .
    docker push "$REGISTRY/sentinel/translation-service:$PROJECT_VERSION"
    
    # Build NER service
    log "Building NER service..."
    docker build -t "$REGISTRY/sentinel/ner-service:$PROJECT_VERSION" -f ner_dockerfile .
    docker push "$REGISTRY/sentinel/ner-service:$PROJECT_VERSION"
    cd ..
    
    # Build backend API
    log "Building backend API..."
    cd backend-api/
    docker build -t "$REGISTRY/sentinel/backend-api:$PROJECT_VERSION" .
    docker push "$REGISTRY/sentinel/backend-api:$PROJECT_VERSION"
    cd ..
    
    # Build frontend dashboard
    log "Building frontend dashboard..."
    cd frontend-dashboard/
    # Build with production environment variables
    VITE_API_BASE_URL="https://api.sentinel.cdf.cm" \
    VITE_MAPBOX_ACCESS_TOKEN="$MAPBOX_TOKEN" \
    npm run build
    docker build -t "$REGISTRY/sentinel/dashboard:$PROJECT_VERSION" .
    docker push "$REGISTRY/sentinel/dashboard:$PROJECT_VERSION"
    cd ..
    
    log "Container images built and pushed successfully"
}

# Deploy NLP services
deploy_nlp_services() {
    log "Deploying NLP services..."
    
    # Update image tags in deployment files
    sed -i "s|registry.cdf.cm/sentinel/translation-service:prod|$REGISTRY/sentinel/translation-service:$PROJECT_VERSION|g" deployment/kubernetes/translation-service.yaml
    sed -i "s|registry.cdf.cm/sentinel/ner-service:prod|$REGISTRY/sentinel/ner-service:$PROJECT_VERSION|g" deployment/kubernetes/ner-service.yaml
    
    kubectl apply -f deployment/kubernetes/translation-service.yaml --namespace="$NAMESPACE"
    kubectl apply -f deployment/kubernetes/ner-service.yaml --namespace="$NAMESPACE"
    
    # Wait for services to be ready
    log "Waiting for NLP services to be ready..."
    kubectl wait --for=condition=ready pod -l app=translation-service --timeout=300s --namespace="$NAMESPACE"
    kubectl wait --for=condition=ready pod -l app=ner-service --timeout=300s --namespace="$NAMESPACE"
    
    log "NLP services deployed successfully"
}

# Deploy backend API
deploy_backend_api() {
    log "Deploying backend API..."
    
    # Update image tag
    sed -i "s|registry.cdf.cm/sentinel/backend-api:prod|$REGISTRY/sentinel/backend-api:$PROJECT_VERSION|g" deployment/kubernetes/backend-api.yaml
    
    kubectl apply -f deployment/kubernetes/backend-api.yaml --namespace="$NAMESPACE"
    
    # Wait for backend to be ready
    log "Waiting for backend API to be ready..."
    kubectl wait --for=condition=ready pod -l app=backend-api --timeout=300s --namespace="$NAMESPACE"
    
    log "Backend API deployed successfully"
}

# Deploy frontend dashboard
deploy_frontend() {
    log "Deploying frontend dashboard..."
    
    # Update image tag
    sed -i "s|registry.cdf.cm/sentinel/dashboard:prod|$REGISTRY/sentinel/dashboard:$PROJECT_VERSION|g" deployment/kubernetes/frontend-dashboard.yaml
    
    kubectl apply -f deployment/kubernetes/frontend-dashboard.yaml --namespace="$NAMESPACE"
    
    # Wait for frontend to be ready
    log "Waiting for frontend dashboard to be ready..."
    kubectl wait --for=condition=ready pod -l app=frontend-dashboard --timeout=300s --namespace="$NAMESPACE"
    
    log "Frontend dashboard deployed successfully"
}

# Apply security policies
apply_security() {
    log "Applying security policies..."
    
    kubectl apply -f deployment/kubernetes/network-policies.yaml --namespace="$NAMESPACE"
    
    log "Security policies applied successfully"
}

# Deploy monitoring
deploy_monitoring() {
    if ! command -v helm &> /dev/null; then
        warn "Skipping monitoring deployment - helm not available"
        return
    fi
    
    log "Deploying monitoring stack..."
    
    # Add Helm repositories
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo update
    
    # Install Prometheus
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring --create-namespace \
        --set grafana.adminPassword="${GRAFANA_ADMIN_PASSWORD:-admin123}" \
        --wait
    
    # Apply custom monitoring rules
    kubectl apply -f deployment/monitoring/prometheus-rules.yaml --namespace="$NAMESPACE"
    
    log "Monitoring stack deployed successfully"
}

# Verify deployment
verify_deployment() {
    log "Verifying deployment..."
    
    # Check all pods are running
    log "Checking pod status..."
    kubectl get pods -n "$NAMESPACE"
    
    # Check services
    log "Checking service status..."
    kubectl get svc -n "$NAMESPACE"
    
    # Test database connectivity
    log "Testing database connectivity..."
    POSTGRES_POD=$(kubectl get pods -n "$NAMESPACE" -l app=postgres -o jsonpath='{.items[0].metadata.name}')
    kubectl exec "$POSTGRES_POD" -n "$NAMESPACE" -- pg_isready
    
    # Test API endpoints
    log "Testing API endpoints..."
    kubectl port-forward -n "$NAMESPACE" svc/backend-api 8000:8000 &
    PF_PID=$!
    sleep 5
    
    if curl -f http://localhost:8000/health/; then
        log "Backend API health check passed"
    else
        warn "Backend API health check failed"
    fi
    
    kill $PF_PID 2>/dev/null || true
    
    log "Deployment verification completed"
}

# Generate deployment report
generate_report() {
    log "Generating deployment report..."
    
    REPORT_FILE="deployment-report-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$REPORT_FILE" << EOF
PROJECT SENTINEL DEPLOYMENT REPORT
==================================
Classification: RESTRICTED
Date: $(date)
Namespace: $NAMESPACE
Version: $PROJECT_VERSION

DEPLOYMENT STATUS:
================
EOF
    
    echo "Pods:" >> "$REPORT_FILE"
    kubectl get pods -n "$NAMESPACE" -o wide >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    echo "Services:" >> "$REPORT_FILE"
    kubectl get svc -n "$NAMESPACE" -o wide >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    echo "Ingresses:" >> "$REPORT_FILE"
    kubectl get ingress -n "$NAMESPACE" -o wide >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    log "Deployment report generated: $REPORT_FILE"
}

# Main deployment function
main() {
    log "Starting Project Sentinel production deployment..."
    log "Namespace: $NAMESPACE"
    log "Version: $PROJECT_VERSION"
    
    check_prerequisites
    setup_namespace
    deploy_database
    build_and_push_images
    deploy_nlp_services
    deploy_backend_api
    deploy_frontend
    apply_security
    deploy_monitoring
    verify_deployment
    generate_report
    
    log "🎉 Project Sentinel production deployment completed successfully!"
    log "Dashboard URL: https://dashboard.sentinel.cdf.cm"
    log "API URL: https://api.sentinel.cdf.cm"
    log "Monitoring: Access through Prometheus/Grafana in monitoring namespace"
    
    echo ""
    echo "NEXT STEPS:"
    echo "1. Configure DNS records for dashboard.sentinel.cdf.cm and api.sentinel.cdf.cm"
    echo "2. Set up SSL certificates if not using cert-manager"
    echo "3. Configure monitoring alerts and notification channels"
    echo "4. Run initial data ingestion tests"
    echo "5. Conduct analyst training sessions"
    echo ""
    echo "🇨🇲 Project Sentinel is now operational for the Cameroon Defense Force!"
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
