#!/bin/bash

# Project Sentinel Rollback Script
# Emergency rollback for production deployment issues
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
BACKUP_NAMESPACE="sentinel-backup"
REGISTRY="registry.cdf.cm"

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -v VERSION     Rollback to specific version (required)"
    echo "  -c COMPONENT   Rollback specific component only (optional)"
    echo "                 Components: database, nlp, backend, frontend, all"
    echo "  -f             Force rollback without confirmation"
    echo "  -h             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -v v1.0.0                    # Rollback all components to v1.0.0"
    echo "  $0 -v v1.0.0 -c backend         # Rollback only backend to v1.0.0"
    echo "  $0 -v v1.0.0 -f                 # Force rollback without confirmation"
}

# Parse command line arguments
ROLLBACK_VERSION=""
COMPONENT="all"
FORCE_ROLLBACK=false

while getopts "v:c:fh" opt; do
    case $opt in
        v)
            ROLLBACK_VERSION="$OPTARG"
            ;;
        c)
            COMPONENT="$OPTARG"
            ;;
        f)
            FORCE_ROLLBACK=true
            ;;
        h)
            usage
            exit 0
            ;;
        \?)
            error "Invalid option: -$OPTARG"
            ;;
    esac
done

# Validate arguments
if [[ -z "$ROLLBACK_VERSION" ]]; then
    error "Version is required. Use -v to specify the version to rollback to."
fi

# Valid components
VALID_COMPONENTS=("database" "nlp" "backend" "frontend" "all")
if [[ ! " ${VALID_COMPONENTS[@]} " =~ " ${COMPONENT} " ]]; then
    error "Invalid component: $COMPONENT. Valid components: ${VALID_COMPONENTS[*]}"
fi

# Confirmation prompt
confirm_rollback() {
    if [[ "$FORCE_ROLLBACK" == true ]]; then
        return 0
    fi
    
    echo ""
    warn "🚨 EMERGENCY ROLLBACK OPERATION 🚨"
    echo "This will rollback Project Sentinel to version: $ROLLBACK_VERSION"
    echo "Component(s) to rollback: $COMPONENT"
    echo "Namespace: $NAMESPACE"
    echo ""
    warn "This operation may cause service interruption!"
    echo ""
    read -p "Do you want to proceed? (type 'CONFIRM' to continue): " confirmation
    
    if [[ "$confirmation" != "CONFIRM" ]]; then
        log "Rollback cancelled by user"
        exit 0
    fi
}

# Create backup of current state
backup_current_state() {
    log "Creating backup of current deployment state..."
    
    # Create backup namespace if it doesn't exist
    kubectl create namespace "$BACKUP_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # Backup current deployments
    kubectl get deployments -n "$NAMESPACE" -o yaml > "backup-deployments-$(date +%Y%m%d-%H%M%S).yaml"
    kubectl get configmaps -n "$NAMESPACE" -o yaml > "backup-configmaps-$(date +%Y%m%d-%H%M%S).yaml"
    kubectl get secrets -n "$NAMESPACE" -o yaml > "backup-secrets-$(date +%Y%m%d-%H%M%S).yaml"
    
    log "Current state backed up successfully"
}

# Rollback database
rollback_database() {
    if [[ "$COMPONENT" != "database" && "$COMPONENT" != "all" ]]; then
        return 0
    fi
    
    warn "⚠️  Database rollback is potentially destructive!"
    warn "This may result in data loss if the schema has changed."
    
    if [[ "$FORCE_ROLLBACK" != true ]]; then
        read -p "Are you sure you want to rollback the database? (y/N): " db_confirm
        if [[ "$db_confirm" != "y" && "$db_confirm" != "Y" ]]; then
            log "Skipping database rollback"
            return 0
        fi
    fi
    
    log "Rolling back PostgreSQL database..."
    
    # Scale down backend applications first to prevent new connections
    kubectl scale deployment backend-api --replicas=0 -n "$NAMESPACE"
    kubectl scale deployment celery-worker --replicas=0 -n "$NAMESPACE"
    
    # Wait for pods to terminate
    kubectl wait --for=delete pod -l app=backend-api --timeout=60s -n "$NAMESPACE" || true
    kubectl wait --for=delete pod -l app=celery-worker --timeout=60s -n "$NAMESPACE" || true
    
    # Create database backup before rollback
    POSTGRES_POD=$(kubectl get pods -n "$NAMESPACE" -l app=postgres -o jsonpath='{.items[0].metadata.name}')
    kubectl exec "$POSTGRES_POD" -n "$NAMESPACE" -- pg_dump -U postgres sentinel_db > "db-backup-$(date +%Y%m%d-%H%M%S).sql"
    
    # Perform database rollback (this would typically involve restoring from backup)
    # NOTE: Actual implementation would depend on backup strategy
    warn "Database rollback requires manual intervention - backup created"
    
    log "Database rollback preparation completed"
}

# Rollback NLP services
rollback_nlp_services() {
    if [[ "$COMPONENT" != "nlp" && "$COMPONENT" != "all" ]]; then
        return 0
    fi
    
    log "Rolling back NLP services to version $ROLLBACK_VERSION..."
    
    # Update image tags to rollback version
    kubectl set image deployment/translation-service \
        translation-service="$REGISTRY/sentinel/translation-service:$ROLLBACK_VERSION" \
        -n "$NAMESPACE"
    
    kubectl set image deployment/ner-service \
        ner-service="$REGISTRY/sentinel/ner-service:$ROLLBACK_VERSION" \
        -n "$NAMESPACE"
    
    # Wait for rollout to complete
    kubectl rollout status deployment/translation-service -n "$NAMESPACE" --timeout=300s
    kubectl rollout status deployment/ner-service -n "$NAMESPACE" --timeout=300s
    
    # Verify services are healthy
    kubectl wait --for=condition=ready pod -l app=translation-service --timeout=120s -n "$NAMESPACE"
    kubectl wait --for=condition=ready pod -l app=ner-service --timeout=120s -n "$NAMESPACE"
    
    log "NLP services rolled back successfully"
}

# Rollback backend API
rollback_backend() {
    if [[ "$COMPONENT" != "backend" && "$COMPONENT" != "all" ]]; then
        return 0
    fi
    
    log "Rolling back backend API to version $ROLLBACK_VERSION..."
    
    # Update image tag to rollback version
    kubectl set image deployment/backend-api \
        backend-api="$REGISTRY/sentinel/backend-api:$ROLLBACK_VERSION" \
        -n "$NAMESPACE"
    
    kubectl set image deployment/celery-worker \
        celery-worker="$REGISTRY/sentinel/backend-api:$ROLLBACK_VERSION" \
        -n "$NAMESPACE"
    
    # Wait for rollout to complete
    kubectl rollout status deployment/backend-api -n "$NAMESPACE" --timeout=300s
    kubectl rollout status deployment/celery-worker -n "$NAMESPACE" --timeout=300s
    
    # Verify backend is healthy
    kubectl wait --for=condition=ready pod -l app=backend-api --timeout=120s -n "$NAMESPACE"
    kubectl wait --for=condition=ready pod -l app=celery-worker --timeout=120s -n "$NAMESPACE"
    
    # Test API health
    kubectl port-forward -n "$NAMESPACE" svc/backend-api 8000:8000 &
    PF_PID=$!
    sleep 10
    
    if curl -f http://localhost:8000/health/ >/dev/null 2>&1; then
        log "Backend API health check passed"
    else
        warn "Backend API health check failed - manual verification required"
    fi
    
    kill $PF_PID 2>/dev/null || true
    
    log "Backend API rolled back successfully"
}

# Rollback frontend dashboard
rollback_frontend() {
    if [[ "$COMPONENT" != "frontend" && "$COMPONENT" != "all" ]]; then
        return 0
    fi
    
    log "Rolling back frontend dashboard to version $ROLLBACK_VERSION..."
    
    # Update image tag to rollback version
    kubectl set image deployment/frontend-dashboard \
        frontend-dashboard="$REGISTRY/sentinel/dashboard:$ROLLBACK_VERSION" \
        -n "$NAMESPACE"
    
    # Wait for rollout to complete
    kubectl rollout status deployment/frontend-dashboard -n "$NAMESPACE" --timeout=300s
    
    # Verify frontend is healthy
    kubectl wait --for=condition=ready pod -l app=frontend-dashboard --timeout=120s -n "$NAMESPACE"
    
    log "Frontend dashboard rolled back successfully"
}

# Verify rollback
verify_rollback() {
    log "Verifying rollback..."
    
    # Check all pods are running
    log "Checking pod status..."
    kubectl get pods -n "$NAMESPACE" -o wide
    
    # Check deployment statuses
    log "Checking deployment statuses..."
    kubectl get deployments -n "$NAMESPACE" -o wide
    
    # Test critical endpoints
    log "Testing critical endpoints..."
    
    # Test backend API
    kubectl port-forward -n "$NAMESPACE" svc/backend-api 8000:8000 &
    PF_PID=$!
    sleep 5
    
    if curl -f http://localhost:8000/health/ >/dev/null 2>&1; then
        log "✅ Backend API health check passed"
    else
        error "❌ Backend API health check failed"
    fi
    
    if curl -f http://localhost:8000/api/v1/statistics/ >/dev/null 2>&1; then
        log "✅ Backend API statistics endpoint accessible"
    else
        warn "⚠️ Backend API statistics endpoint not accessible"
    fi
    
    kill $PF_PID 2>/dev/null || true
    
    log "Rollback verification completed"
}

# Generate rollback report
generate_rollback_report() {
    log "Generating rollback report..."
    
    REPORT_FILE="rollback-report-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$REPORT_FILE" << EOF
PROJECT SENTINEL ROLLBACK REPORT
================================
Classification: RESTRICTED
Date: $(date)
Rollback Version: $ROLLBACK_VERSION
Component(s): $COMPONENT
Namespace: $NAMESPACE

ROLLBACK STATUS:
===============
EOF
    
    echo "Pods after rollback:" >> "$REPORT_FILE"
    kubectl get pods -n "$NAMESPACE" -o wide >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    echo "Deployments after rollback:" >> "$REPORT_FILE"
    kubectl get deployments -n "$NAMESPACE" -o wide >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    echo "Services after rollback:" >> "$REPORT_FILE"
    kubectl get svc -n "$NAMESPACE" -o wide >> "$REPORT_FILE"
    
    log "Rollback report generated: $REPORT_FILE"
}

# Clean up old resources if needed
cleanup_old_resources() {
    log "Cleaning up old resources..."
    
    # Remove old ReplicaSets
    kubectl delete replicasets -n "$NAMESPACE" --selector="app in (backend-api,frontend-dashboard,translation-service,ner-service)" --field-selector='status.replicas=0'
    
    # Prune unused config maps and secrets older than 7 days
    # This would typically be implemented with proper labeling and date checking
    
    log "Cleanup completed"
}

# Main rollback function
main() {
    log "🚨 Starting Project Sentinel emergency rollback..."
    log "Target version: $ROLLBACK_VERSION"
    log "Component(s): $COMPONENT"
    log "Namespace: $NAMESPACE"
    
    confirm_rollback
    backup_current_state
    
    # Perform rollback in reverse dependency order
    rollback_frontend
    rollback_backend
    rollback_nlp_services
    rollback_database
    
    verify_rollback
    generate_rollback_report
    cleanup_old_resources
    
    log "🎯 Project Sentinel rollback to $ROLLBACK_VERSION completed!"
    log "📊 Report generated: Check rollback report for details"
    
    echo ""
    echo "POST-ROLLBACK CHECKLIST:"
    echo "1. ✅ Verify all services are operational"
    echo "2. ✅ Test critical user workflows"
    echo "3. ✅ Check monitoring and alerts"
    echo "4. ✅ Notify stakeholders of rollback completion"
    echo "5. ✅ Investigate root cause of original issue"
    echo ""
    warn "🔍 Remember to investigate the root cause that required this rollback!"
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
