#!/bin/bash

# Project Sentinel - Rollback Script  
# Cameroon Defense Force - RESTRICTED
# Emergency rollback to previous version

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Default configuration
NAMESPACE="sentinel-prod"
ROLLBACK_TARGET=""
DRY_RUN=false
COMPONENT="all"

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

critical() {
    echo -e "${BOLD}${RED}[$(date +'%Y-%m-%d %H:%M:%S')] CRITICAL: $1${NC}"
}

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --version TARGET     Target version to rollback to"
    echo "                       Options: previous, <revision-number>, <image-tag>"
    echo "  --component COMP     Component to rollback (all, backend, frontend, nlp)"
    echo "  --dry-run           Show what would be rolled back without doing it"
    echo "  --namespace NS      Kubernetes namespace (default: sentinel-prod)"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --version previous           # Rollback all to previous version"
    echo "  $0 --component backend --dry-run # Show backend rollback plan"
    echo "  $0 --version v1.2.3             # Rollback to specific version"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --version)
            ROLLBACK_TARGET="$2"
            shift 2
            ;;
        --component)
            COMPONENT="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --namespace)
            NAMESPACE="$2"
            shift 2
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

# Print emergency header
print_emergency_header() {
    echo ""
    echo -e "${BOLD}${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${RED}║                    🚨 EMERGENCY ROLLBACK 🚨                  ║${NC}"
    echo -e "${BOLD}${RED}║              PROJECT SENTINEL - CAMEROON DEFENSE             ║${NC}"  
    echo -e "${BOLD}${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BOLD}Namespace:${NC} $NAMESPACE"
    echo -e "${BOLD}Component:${NC} $COMPONENT"
    echo -e "${BOLD}Target:${NC} $ROLLBACK_TARGET"
    echo -e "${BOLD}Dry Run:${NC} $DRY_RUN"
    echo -e "${BOLD}Timestamp:${NC} $(date)"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed"
    fi
    
    # Test cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        error "Cannot connect to Kubernetes cluster"
    fi
    
    # Check namespace exists
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        error "Namespace '$NAMESPACE' does not exist"
    fi
    
    log "Prerequisites check completed"
}

# Get current deployment status
get_current_status() {
    log "Getting current deployment status..."
    
    # Backend deployments
    echo -e "${BLUE}Backend API Status:${NC}"
    kubectl get deployment backend-api -n "$NAMESPACE" -o wide 2>/dev/null || echo "  Not found"
    
    # Frontend deployments  
    echo -e "${BLUE}Frontend Dashboard Status:${NC}"
    kubectl get deployment frontend-dashboard -n "$NAMESPACE" -o wide 2>/dev/null || echo "  Not found"
    
    # NLP services
    echo -e "${BLUE}Translation Service Status:${NC}"
    kubectl get deployment translation-service -n "$NAMESPACE" -o wide 2>/dev/null || echo "  Not found"
    
    echo -e "${BLUE}NER Service Status:${NC}"
    kubectl get deployment ner-service -n "$NAMESPACE" -o wide 2>/dev/null || echo "  Not found"
    
    echo ""
}

# Get rollback targets
get_rollback_targets() {
    log "Determining rollback targets..."
    
    local deployments=()
    
    case "$COMPONENT" in
        "all")
            deployments=("backend-api" "frontend-dashboard" "translation-service" "ner-service")
            ;;
        "backend")
            deployments=("backend-api")
            ;;
        "frontend")
            deployments=("frontend-dashboard")
            ;;
        "nlp")
            deployments=("translation-service" "ner-service")
            ;;
        *)
            error "Invalid component: $COMPONENT"
            ;;
    esac
    
    for deployment in "${deployments[@]}"; do
        if kubectl get deployment "$deployment" -n "$NAMESPACE" &> /dev/null; then
            echo -e "${BLUE}Rollback target for $deployment:${NC}"
            
            # Get rollout history
            kubectl rollout history deployment "$deployment" -n "$NAMESPACE" || warn "No rollout history for $deployment"
            
            # Determine rollback revision
            if [[ "$ROLLBACK_TARGET" == "previous" ]]; then
                local revision=$(kubectl rollout history deployment "$deployment" -n "$NAMESPACE" --revision=2 2>/dev/null || echo "")
                if [[ -n "$revision" ]]; then
                    echo "  Will rollback to previous revision"
                else
                    warn "No previous revision found for $deployment"
                fi
            elif [[ "$ROLLBACK_TARGET" =~ ^[0-9]+$ ]]; then
                echo "  Will rollback to revision $ROLLBACK_TARGET"
            else
                echo "  Will rollback to image tag: $ROLLBACK_TARGET"
            fi
        else
            warn "Deployment $deployment not found"
        fi
        echo ""
    done
}

# Execute rollback
execute_rollback() {
    local deployments=()
    
    case "$COMPONENT" in
        "all")
            deployments=("backend-api" "frontend-dashboard" "translation-service" "ner-service")
            ;;
        "backend")
            deployments=("backend-api")
            ;;
        "frontend") 
            deployments=("frontend-dashboard")
            ;;
        "nlp")
            deployments=("translation-service" "ner-service")
            ;;
    esac
    
    for deployment in "${deployments[@]}"; do
        if ! kubectl get deployment "$deployment" -n "$NAMESPACE" &> /dev/null; then
            warn "Skipping $deployment - not found"
            continue
        fi
        
        log "Rolling back $deployment..."
        
        if [[ "$DRY_RUN" == true ]]; then
            echo "  DRY RUN: Would execute rollback for $deployment"
            continue
        fi
        
        # Execute rollback based on target type
        if [[ "$ROLLBACK_TARGET" == "previous" ]]; then
            # Rollback to previous revision
            kubectl rollout undo deployment "$deployment" -n "$NAMESPACE"
            
        elif [[ "$ROLLBACK_TARGET" =~ ^[0-9]+$ ]]; then
            # Rollback to specific revision
            kubectl rollout undo deployment "$deployment" -n "$NAMESPACE" --to-revision="$ROLLBACK_TARGET"
            
        else
            # Rollback to specific image tag
            local container_name=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.spec.template.spec.containers[0].name}')
            local image_base=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.spec.template.spec.containers[0].image}' | cut -d':' -f1)
            
            kubectl set image deployment "$deployment" -n "$NAMESPACE" "$container_name=${image_base}:${ROLLBACK_TARGET}"
        fi
        
        if [[ $? -eq 0 ]]; then
            log "Rollback initiated for $deployment"
        else
            critical "Rollback failed for $deployment"
        fi
    done
}

# Wait for rollback completion
wait_for_rollback() {
    if [[ "$DRY_RUN" == true ]]; then
        log "DRY RUN: Would wait for rollback completion"
        return 0
    fi
    
    log "Waiting for rollback to complete..."
    
    local deployments=()
    
    case "$COMPONENT" in
        "all")
            deployments=("backend-api" "frontend-dashboard" "translation-service" "ner-service")
            ;;
        "backend")
            deployments=("backend-api")
            ;;
        "frontend")
            deployments=("frontend-dashboard")
            ;;
        "nlp")
            deployments=("translation-service" "ner-service")
            ;;
    esac
    
    local timeout=300  # 5 minutes
    local start_time=$(date +%s)
    
    while true; do
        local all_ready=true
        
        for deployment in "${deployments[@]}"; do
            if kubectl get deployment "$deployment" -n "$NAMESPACE" &> /dev/null; then
                local ready_replicas=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
                local desired_replicas=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}')
                
                if [[ "$ready_replicas" != "$desired_replicas" ]]; then
                    all_ready=false
                    break
                fi
            fi
        done
        
        if [[ "$all_ready" == true ]]; then
            log "All deployments are ready"
            break
        fi
        
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [[ $elapsed -gt $timeout ]]; then
            critical "Rollback timeout reached ($timeout seconds)"
            return 1
        fi
        
        echo -n "."
        sleep 10
    done
    
    echo ""
}

# Verify rollback
verify_rollback() {
    log "Verifying rollback..."
    
    if [[ "$DRY_RUN" == true ]]; then
        log "DRY RUN: Would verify rollback completion"
        return 0
    fi
    
    # Check pod status
    echo -e "${BLUE}Pod Status After Rollback:${NC}"
    kubectl get pods -n "$NAMESPACE" -o wide
    
    # Check service endpoints
    echo -e "${BLUE}Service Endpoints:${NC}"
    kubectl get endpoints -n "$NAMESPACE"
    
    # Test API endpoints if available
    local backend_pod=$(kubectl get pods -n "$NAMESPACE" -l app=backend-api -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [[ -n "$backend_pod" ]]; then
        log "Testing backend API..."
        kubectl port-forward -n "$NAMESPACE" "$backend_pod" 8000:8000 &
        local pf_pid=$!
        sleep 5
        
        if curl -f http://localhost:8000/health/ --connect-timeout 5 &>/dev/null; then
            log "Backend API health check passed"
        else
            warn "Backend API health check failed"
        fi
        
        kill $pf_pid 2>/dev/null || true
    fi
    
    # Run comprehensive status check
    if [[ -f "./scripts/status-check.sh" ]]; then
        log "Running comprehensive status check..."
        ./scripts/status-check.sh --namespace "$NAMESPACE" || warn "Status check reported issues"
    fi
    
    log "Rollback verification completed"
}

# Generate rollback report
generate_rollback_report() {
    log "Generating rollback report..."
    
    local report_file="/tmp/rollback-report-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$report_file" << EOF
Project Sentinel Emergency Rollback Report
==========================================

Rollback Details:
- Component: $COMPONENT
- Target: $ROLLBACK_TARGET
- Namespace: $NAMESPACE
- Dry Run: $DRY_RUN
- Executed: $(date)
- Status: $(if [[ "$DRY_RUN" == true ]]; then echo "DRY RUN COMPLETED"; else echo "ROLLBACK COMPLETED"; fi)

Deployment Status After Rollback:
EOF
    
    if [[ "$DRY_RUN" == false ]]; then
        kubectl get deployments -n "$NAMESPACE" -o wide >> "$report_file" 2>/dev/null || true
        echo "" >> "$report_file"
        echo "Pod Status:" >> "$report_file"
        kubectl get pods -n "$NAMESPACE" -o wide >> "$report_file" 2>/dev/null || true
    fi
    
    log "Rollback report: $report_file"
    
    # Display report summary
    echo ""
    echo -e "${BOLD}${GREEN}ROLLBACK SUMMARY:${NC}"
    if [[ "$DRY_RUN" == true ]]; then
        echo -e "${BLUE}✅ Dry run completed successfully${NC}"
        echo -e "${BLUE}   No changes were made to the system${NC}"
    else
        echo -e "${GREEN}✅ Rollback completed successfully${NC}"
        echo -e "${GREEN}   System has been rolled back to: $ROLLBACK_TARGET${NC}"
    fi
    echo ""
}

# Main execution function
main() {
    print_emergency_header
    
    # Validate required parameters
    if [[ -z "$ROLLBACK_TARGET" ]]; then
        error "Rollback target not specified. Use --version to specify target."
    fi
    
    check_prerequisites
    get_current_status
    get_rollback_targets
    
    # Confirmation for production rollback
    if [[ "$DRY_RUN" == false ]]; then
        echo -e "${BOLD}${YELLOW}⚠️  CRITICAL CONFIRMATION REQUIRED ⚠️${NC}"
        echo -e "${YELLOW}You are about to rollback Project Sentinel in production.${NC}"
        echo -e "${YELLOW}Component: $COMPONENT${NC}"
        echo -e "${YELLOW}Target: $ROLLBACK_TARGET${NC}"
        echo -e "${YELLOW}Namespace: $NAMESPACE${NC}"
        echo ""
        echo -n "Type 'EMERGENCY ROLLBACK' to confirm: "
        read -r confirmation
        
        if [[ "$confirmation" != "EMERGENCY ROLLBACK" ]]; then
            log "Rollback cancelled by user"
            exit 0
        fi
    fi
    
    execute_rollback
    wait_for_rollback
    verify_rollback
    generate_rollback_report
    
    if [[ "$DRY_RUN" == true ]]; then
        log "🔍 Emergency rollback dry run completed successfully!"
    else
        log "🚨 Emergency rollback completed successfully!"
        echo -e "${BOLD}${GREEN}System has been rolled back to: $ROLLBACK_TARGET${NC}"
    fi
}

# Execute main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
