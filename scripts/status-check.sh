#!/bin/bash

# Project Sentinel - System Status Check Script
# Cameroon Defense Force - RESTRICTED
# Comprehensive health and status verification for production deployment

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
PRODUCTION_MODE=false
VERBOSE=false

# Status counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
    ((WARNING_CHECKS++))
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    ((FAILED_CHECKS++))
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}"
    ((PASSED_CHECKS++))
}

info() {
    if [[ "$VERBOSE" == true ]]; then
        echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
    fi
}

# Check function wrapper
check() {
    local description="$1"
    local command="$2"
    
    ((TOTAL_CHECKS++))
    info "Running check: $description"
    
    if eval "$command" &> /dev/null; then
        success "$description"
        return 0
    else
        error "$description"
        return 1
    fi
}

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --production     Run production-specific checks"
    echo "  --namespace NS   Kubernetes namespace (default: sentinel-prod)"
    echo "  --verbose        Show detailed output"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --production              # Full production status check"
    echo "  $0 --verbose                 # Verbose output"
    echo "  $0 --namespace sentinel-dev  # Check dev namespace"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --production)
            PRODUCTION_MODE=true
            shift
            ;;
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Print header
print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${BLUE}║                PROJECT SENTINEL STATUS CHECK                 ║${NC}"
    echo -e "${BOLD}${BLUE}║              Cameroon Defense Force - RESTRICTED             ║${NC}"
    echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BOLD}Namespace:${NC} $NAMESPACE"
    echo -e "${BOLD}Mode:${NC} $([ "$PRODUCTION_MODE" == true ] && echo "Production" || echo "Development")"
    echo -e "${BOLD}Timestamp:${NC} $(date)"
    echo ""
}

# Check Kubernetes connectivity
check_kubernetes() {
    log "🔗 Checking Kubernetes connectivity..."
    
    check "Kubectl is available and configured" "command -v kubectl"
    check "Can connect to Kubernetes cluster" "kubectl cluster-info"
    check "Namespace '$NAMESPACE' exists" "kubectl get namespace $NAMESPACE"
    
    # Get cluster info
    if [[ "$VERBOSE" == true ]]; then
        echo -e "${BLUE}Cluster Information:${NC}"
        kubectl cluster-info | head -5
        echo ""
    fi
}

# Check pod status
check_pods() {
    log "🚀 Checking pod status..."
    
    local pods=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null || echo "")
    
    if [[ -z "$pods" ]]; then
        error "No pods found in namespace $NAMESPACE"
        return
    fi
    
    # Check individual pods
    while IFS= read -r line; do
        local pod_name=$(echo "$line" | awk '{print $1}')
        local status=$(echo "$line" | awk '{print $3}')
        local ready=$(echo "$line" | awk '{print $2}')
        
        if [[ "$status" == "Running" ]]; then
            check "Pod $pod_name is running" "kubectl get pod $pod_name -n $NAMESPACE"
            
            # Check if all containers are ready
            if [[ "$ready" == *"/"* ]]; then
                local ready_count=$(echo "$ready" | cut -d'/' -f1)
                local total_count=$(echo "$ready" | cut -d'/' -f2)
                
                if [[ "$ready_count" == "$total_count" ]]; then
                    success "Pod $pod_name containers are ready ($ready)"
                else
                    warn "Pod $pod_name containers not all ready ($ready)"
                fi
            fi
        else
            error "Pod $pod_name is in status: $status"
        fi
    done <<< "$pods"
    
    # Show pod summary
    if [[ "$VERBOSE" == true ]]; then
        echo -e "${BLUE}Pod Summary:${NC}"
        kubectl get pods -n "$NAMESPACE" -o wide
        echo ""
    fi
}

# Check service endpoints
check_services() {
    log "🌐 Checking service endpoints..."
    
    local services=$(kubectl get services -n "$NAMESPACE" --no-headers 2>/dev/null || echo "")
    
    if [[ -z "$services" ]]; then
        error "No services found in namespace $NAMESPACE"
        return
    fi
    
    while IFS= read -r line; do
        local service_name=$(echo "$line" | awk '{print $1}')
        local type=$(echo "$line" | awk '{print $2}')
        
        check "Service $service_name exists" "kubectl get service $service_name -n $NAMESPACE"
        
        # Check service endpoints
        local endpoints=$(kubectl get endpoints "$service_name" -n "$NAMESPACE" --no-headers 2>/dev/null | awk '{print $2}')
        if [[ -n "$endpoints" && "$endpoints" != "<none>" ]]; then
            success "Service $service_name has endpoints: $endpoints"
        else
            error "Service $service_name has no endpoints"
        fi
    done <<< "$services"
}

# Check database connectivity
check_database() {
    log "🗄️ Checking database connectivity..."
    
    local postgres_pod=$(kubectl get pods -n "$NAMESPACE" -l app=postgres -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [[ -z "$postgres_pod" ]]; then
        error "PostgreSQL pod not found"
        return
    fi
    
    check "PostgreSQL pod is running" "kubectl get pod $postgres_pod -n $NAMESPACE"
    check "PostgreSQL is ready" "kubectl exec -n $NAMESPACE $postgres_pod -- pg_isready -U postgres"
    check "Can connect to sentinel database" "kubectl exec -n $NAMESPACE $postgres_pod -- psql -U postgres -d sentinel_db -c 'SELECT 1;'"
    check "PostGIS extension is available" "kubectl exec -n $NAMESPACE $postgres_pod -- psql -U postgres -d sentinel_db -c 'SELECT PostGIS_Version();'"
    
    # Check database statistics
    if [[ "$VERBOSE" == true ]]; then
        echo -e "${BLUE}Database Statistics:${NC}"
        kubectl exec -n "$NAMESPACE" "$postgres_pod" -- psql -U postgres -d sentinel_db -c "
        SELECT 
            schemaname,
            tablename,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes
        FROM pg_stat_user_tables 
        ORDER BY n_tup_ins DESC 
        LIMIT 5;"
        echo ""
    fi
}

# Check API endpoints
check_api_endpoints() {
    log "🔌 Checking API endpoints..."
    
    # Backend API health check
    local backend_pod=$(kubectl get pods -n "$NAMESPACE" -l app=backend-api -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [[ -n "$backend_pod" ]]; then
        check "Backend API pod is running" "kubectl get pod $backend_pod -n $NAMESPACE"
        
        # Port forward and test API (in background)
        kubectl port-forward -n "$NAMESPACE" "$backend_pod" 8000:8000 &
        local pf_pid=$!
        sleep 5
        
        check "Backend API health endpoint" "curl -f http://localhost:8000/health/ --connect-timeout 5"
        check "Backend API statistics endpoint" "curl -f http://localhost:8000/api/v1/statistics/ --connect-timeout 5"
        
        # Clean up port forward
        kill $pf_pid 2>/dev/null || true
    else
        error "Backend API pod not found"
    fi
    
    # NLP Services health check
    local translation_pod=$(kubectl get pods -n "$NAMESPACE" -l app=translation-service -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    local ner_pod=$(kubectl get pods -n "$NAMESPACE" -l app=ner-service -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [[ -n "$translation_pod" ]]; then
        kubectl port-forward -n "$NAMESPACE" "$translation_pod" 8001:8000 &
        local trans_pf_pid=$!
        sleep 3
        
        check "Translation service health" "curl -f http://localhost:8001/health --connect-timeout 5"
        
        kill $trans_pf_pid 2>/dev/null || true
    fi
    
    if [[ -n "$ner_pod" ]]; then
        kubectl port-forward -n "$NAMESPACE" "$ner_pod" 8002:8000 &
        local ner_pf_pid=$!
        sleep 3
        
        check "NER service health" "curl -f http://localhost:8002/health --connect-timeout 5"
        
        kill $ner_pf_pid 2>/dev/null || true
    fi
}

# Check resource usage
check_resources() {
    log "📊 Checking resource usage..."
    
    # Node resource usage
    if kubectl top nodes &>/dev/null; then
        echo -e "${BLUE}Node Resource Usage:${NC}"
        kubectl top nodes
        echo ""
    else
        warn "Metrics server not available - cannot check node resources"
    fi
    
    # Pod resource usage
    if kubectl top pods -n "$NAMESPACE" &>/dev/null; then
        echo -e "${BLUE}Pod Resource Usage:${NC}"
        kubectl top pods -n "$NAMESPACE"
        echo ""
    else
        warn "Metrics server not available - cannot check pod resources"
    fi
    
    # Check PVC usage
    local pvcs=$(kubectl get pvc -n "$NAMESPACE" --no-headers 2>/dev/null || echo "")
    if [[ -n "$pvcs" ]]; then
        echo -e "${BLUE}Persistent Volume Claims:${NC}"
        kubectl get pvc -n "$NAMESPACE"
        echo ""
    fi
}

# Check ingress and external access
check_ingress() {
    log "🌍 Checking ingress and external access..."
    
    local ingresses=$(kubectl get ingress -n "$NAMESPACE" --no-headers 2>/dev/null || echo "")
    
    if [[ -n "$ingresses" ]]; then
        while IFS= read -r line; do
            local ingress_name=$(echo "$line" | awk '{print $1}')
            local hosts=$(echo "$line" | awk '{print $2}')
            
            check "Ingress $ingress_name exists" "kubectl get ingress $ingress_name -n $NAMESPACE"
            
            # Test external access for production mode
            if [[ "$PRODUCTION_MODE" == true ]]; then
                for host in $(echo "$hosts" | tr ',' ' '); do
                    if [[ "$host" != "*" ]]; then
                        check "External access to https://$host" "curl -f -k --connect-timeout 10 https://$host/health || curl -f -k --connect-timeout 10 https://$host/ || curl -f -k --connect-timeout 10 http://$host/health || curl -f -k --connect-timeout 10 http://$host/"
                    fi
                done
            fi
        done <<< "$ingresses"
    else
        warn "No ingress resources found"
    fi
}

# Check security configurations
check_security() {
    log "🔐 Checking security configurations..."
    
    # Check network policies
    local netpols=$(kubectl get networkpolicy -n "$NAMESPACE" --no-headers 2>/dev/null || echo "")
    if [[ -n "$netpols" ]]; then
        success "Network policies are configured"
    else
        warn "No network policies found"
    fi
    
    # Check secrets
    local secrets=$(kubectl get secrets -n "$NAMESPACE" --no-headers 2>/dev/null || echo "")
    local required_secrets=("postgres-secret" "django-secret" "registry-credentials")
    
    for secret in "${required_secrets[@]}"; do
        if echo "$secrets" | grep -q "$secret"; then
            success "Required secret '$secret' exists"
        else
            error "Required secret '$secret' is missing"
        fi
    done
    
    # Check RBAC (if applicable)
    if kubectl get rolebinding -n "$NAMESPACE" &>/dev/null; then
        local bindings=$(kubectl get rolebinding -n "$NAMESPACE" --no-headers | wc -l)
        if [[ "$bindings" -gt 0 ]]; then
            success "RBAC configurations present ($bindings role bindings)"
        fi
    fi
}

# Check monitoring and logging
check_monitoring() {
    log "📈 Checking monitoring and logging..."
    
    # Check if monitoring namespace exists
    if kubectl get namespace monitoring &>/dev/null; then
        success "Monitoring namespace exists"
        
        # Check Prometheus
        if kubectl get deployment prometheus-server -n monitoring &>/dev/null; then
            success "Prometheus server is deployed"
        else
            warn "Prometheus server not found"
        fi
        
        # Check Grafana
        if kubectl get deployment grafana -n monitoring &>/dev/null; then
            success "Grafana is deployed"
        else
            warn "Grafana not found"
        fi
    else
        warn "Monitoring namespace not found"
    fi
    
    # Check log aggregation
    if kubectl get daemonset fluentd -n kube-system &>/dev/null; then
        success "Log aggregation (Fluentd) is running"
    elif kubectl get daemonset filebeat -n kube-system &>/dev/null; then
        success "Log aggregation (Filebeat) is running"
    else
        warn "No log aggregation system found"
    fi
}

# Generate status report
generate_report() {
    echo ""
    echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${BLUE}║                    STATUS REPORT SUMMARY                     ║${NC}"
    echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${BOLD}Total Checks:${NC} $TOTAL_CHECKS"
    echo -e "${GREEN}${BOLD}Passed:${NC} $PASSED_CHECKS"
    echo -e "${YELLOW}${BOLD}Warnings:${NC} $WARNING_CHECKS"
    echo -e "${RED}${BOLD}Failed:${NC} $FAILED_CHECKS"
    echo ""
    
    # Calculate success rate
    local success_rate=0
    if [[ $TOTAL_CHECKS -gt 0 ]]; then
        success_rate=$(( (PASSED_CHECKS * 100) / TOTAL_CHECKS ))
    fi
    
    echo -e "${BOLD}Success Rate:${NC} ${success_rate}%"
    
    # Overall status
    if [[ $FAILED_CHECKS -eq 0 && $WARNING_CHECKS -eq 0 ]]; then
        echo -e "${GREEN}${BOLD}Overall Status: ✅ HEALTHY${NC}"
    elif [[ $FAILED_CHECKS -eq 0 ]]; then
        echo -e "${YELLOW}${BOLD}Overall Status: ⚠️  HEALTHY WITH WARNINGS${NC}"
    elif [[ $success_rate -ge 75 ]]; then
        echo -e "${YELLOW}${BOLD}Overall Status: ⚠️  DEGRADED${NC}"
    else
        echo -e "${RED}${BOLD}Overall Status: ❌ UNHEALTHY${NC}"
    fi
    
    echo ""
    echo -e "${BOLD}System URLs:${NC}"
    echo "  Dashboard: https://sentinel.cdf.cm"
    echo "  API: https://api.sentinel.cdf.cm"
    echo "  Monitoring: https://grafana.sentinel.cdf.cm"
    echo ""
    
    # Exit code based on results
    if [[ $FAILED_CHECKS -eq 0 ]]; then
        return 0
    else
        return 1
    fi
}

# Main execution function
main() {
    print_header
    
    # Prerequisites
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v curl &> /dev/null; then
        warn "curl is not installed - some API checks will be skipped"
    fi
    
    # Run all checks
    check_kubernetes
    check_pods
    check_services
    check_database
    check_api_endpoints
    check_resources
    check_ingress
    check_security
    check_monitoring
    
    # Generate final report
    generate_report
}

# Execute main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
