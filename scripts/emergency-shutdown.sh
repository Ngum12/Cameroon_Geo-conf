#!/bin/bash

# Project Sentinel - Emergency Shutdown Script
# Cameroon Defense Force - RESTRICTED
# Immediate system shutdown for critical situations

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
BLINK='\033[5m'
NC='\033[0m' # No Color

# Default configuration
NAMESPACE="sentinel-prod"
SHUTDOWN_TYPE="graceful"
PRESERVE_DATA=true
CONFIRMATION_REQUIRED=true

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

emergency() {
    echo -e "${BLINK}${BOLD}${RED}[$(date +'%Y-%m-%d %H:%M:%S')] EMERGENCY: $1${NC}"
}

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Emergency shutdown options:"
    echo "  --immediate         Immediate shutdown (no graceful period)"
    echo "  --force            Force shutdown without confirmation"
    echo "  --purge-data       Delete all persistent data (DANGEROUS)"
    echo "  --namespace NS     Kubernetes namespace (default: sentinel-prod)"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "⚠️  WARNING: This script will shut down the entire Project Sentinel system"
    echo "⚠️  Use only in genuine emergencies or maintenance windows"
    echo ""
    echo "Examples:"
    echo "  $0                           # Graceful shutdown with confirmation"
    echo "  $0 --immediate --force       # Immediate shutdown without confirmation"
    echo "  $0 --purge-data             # Shutdown and delete all data (DANGEROUS)"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --immediate)
            SHUTDOWN_TYPE="immediate"
            shift
            ;;
        --force)
            CONFIRMATION_REQUIRED=false
            shift
            ;;
        --purge-data)
            PRESERVE_DATA=false
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
    echo -e "${BLINK}${BOLD}${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLINK}${BOLD}${RED}║                  🆘 EMERGENCY SHUTDOWN 🆘                    ║${NC}"
    echo -e "${BLINK}${BOLD}${RED}║              PROJECT SENTINEL - CAMEROON DEFENSE             ║${NC}"
    echo -e "${BLINK}${BOLD}${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BOLD}⚠️  CRITICAL SYSTEM SHUTDOWN IN PROGRESS ⚠️${NC}"
    echo ""
    echo -e "${BOLD}Shutdown Type:${NC} $SHUTDOWN_TYPE"
    echo -e "${BOLD}Namespace:${NC} $NAMESPACE"
    echo -e "${BOLD}Preserve Data:${NC} $PRESERVE_DATA"
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

# Create emergency backup
create_emergency_backup() {
    if [[ "$PRESERVE_DATA" == false ]]; then
        warn "Data preservation disabled - skipping emergency backup"
        return 0
    fi
    
    emergency "Creating emergency backup before shutdown..."
    
    local backup_dir="/tmp/emergency-backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Quick database backup
    local postgres_pod=$(kubectl get pods -n "$NAMESPACE" -l app=postgres -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [[ -n "$postgres_pod" ]]; then
        emergency "Backing up database..."
        kubectl exec -n "$NAMESPACE" "$postgres_pod" -- pg_dump -U postgres -d sentinel_db > "$backup_dir/emergency-db.sql" 2>/dev/null || warn "Database backup failed"
    fi
    
    # Backup configurations
    emergency "Backing up configurations..."
    kubectl get all -n "$NAMESPACE" -o yaml > "$backup_dir/all-resources.yaml" 2>/dev/null || warn "Config backup failed"
    kubectl get secrets -n "$NAMESPACE" -o yaml > "$backup_dir/secrets.yaml" 2>/dev/null || warn "Secrets backup failed"
    kubectl get configmaps -n "$NAMESPACE" -o yaml > "$backup_dir/configmaps.yaml" 2>/dev/null || warn "ConfigMaps backup failed"
    
    # Create backup manifest
    cat > "$backup_dir/emergency-manifest.json" << EOF
{
    "backup_type": "emergency",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "namespace": "$NAMESPACE",
    "shutdown_type": "$SHUTDOWN_TYPE",
    "preserve_data": $PRESERVE_DATA,
    "reason": "Emergency shutdown initiated"
}
EOF
    
    log "Emergency backup created: $backup_dir"
    
    # Secure the backup
    chmod 700 "$backup_dir"
    chmod 600 "$backup_dir"/*
}

# Notify monitoring systems
notify_monitoring() {
    emergency "Notifying monitoring systems..."
    
    # Create alert annotation for Prometheus (if available)
    kubectl annotate namespace "$NAMESPACE" "sentinel.cdf.cm/emergency-shutdown=true" --overwrite 2>/dev/null || true
    kubectl annotate namespace "$NAMESPACE" "sentinel.cdf.cm/shutdown-timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)" --overwrite 2>/dev/null || true
    kubectl annotate namespace "$NAMESPACE" "sentinel.cdf.cm/shutdown-type=$SHUTDOWN_TYPE" --overwrite 2>/dev/null || true
    
    # Log to system journal if available
    if command -v logger &> /dev/null; then
        logger -t "project-sentinel" -p local0.crit "EMERGENCY SHUTDOWN: Type=$SHUTDOWN_TYPE, Namespace=$NAMESPACE, Preserve=$PRESERVE_DATA"
    fi
    
    log "Monitoring systems notified"
}

# Shutdown application services
shutdown_applications() {
    emergency "Shutting down application services..."
    
    # Define shutdown order (reverse of startup dependencies)
    local services=(
        "frontend-dashboard"
        "backend-api" 
        "ner-service"
        "translation-service"
        "data-ingestion"
    )
    
    for service in "${services[@]}"; do
        if kubectl get deployment "$service" -n "$NAMESPACE" &> /dev/null; then
            if [[ "$SHUTDOWN_TYPE" == "graceful" ]]; then
                log "Gracefully shutting down $service..."
                kubectl scale deployment "$service" -n "$NAMESPACE" --replicas=0
                
                # Wait for graceful shutdown
                local timeout=30
                local elapsed=0
                while [[ $elapsed -lt $timeout ]]; do
                    local pods=$(kubectl get pods -n "$NAMESPACE" -l app="$service" --no-headers 2>/dev/null | wc -l)
                    if [[ $pods -eq 0 ]]; then
                        log "$service gracefully shut down"
                        break
                    fi
                    sleep 2
                    elapsed=$((elapsed + 2))
                done
                
                if [[ $elapsed -ge $timeout ]]; then
                    warn "$service did not shut down gracefully, forcing..."
                    kubectl delete pods -n "$NAMESPACE" -l app="$service" --grace-period=5 --force 2>/dev/null || true
                fi
            else
                emergency "Force shutting down $service..."
                kubectl delete deployment "$service" -n "$NAMESPACE" --grace-period=5 --force 2>/dev/null || true
                kubectl delete pods -n "$NAMESPACE" -l app="$service" --grace-period=0 --force 2>/dev/null || true
            fi
        else
            warn "Service $service not found"
        fi
    done
    
    log "Application services shutdown completed"
}

# Shutdown infrastructure services
shutdown_infrastructure() {
    emergency "Shutting down infrastructure services..."
    
    # Redis shutdown
    if kubectl get deployment redis -n "$NAMESPACE" &> /dev/null; then
        if [[ "$SHUTDOWN_TYPE" == "graceful" ]]; then
            log "Gracefully shutting down Redis..."
            kubectl scale deployment redis -n "$NAMESPACE" --replicas=0
            sleep 10
        else
            emergency "Force shutting down Redis..."
            kubectl delete deployment redis -n "$NAMESPACE" --grace-period=5 --force 2>/dev/null || true
            kubectl delete pods -n "$NAMESPACE" -l app=redis --grace-period=0 --force 2>/dev/null || true
        fi
    fi
    
    # PostgreSQL shutdown (last)
    if kubectl get deployment postgres -n "$NAMESPACE" &> /dev/null; then
        if [[ "$SHUTDOWN_TYPE" == "graceful" ]]; then
            log "Gracefully shutting down PostgreSQL..."
            kubectl scale deployment postgres -n "$NAMESPACE" --replicas=0
            sleep 15  # Give more time for database shutdown
        else
            emergency "Force shutting down PostgreSQL..."
            kubectl delete deployment postgres -n "$NAMESPACE" --grace-period=10 --force 2>/dev/null || true
            kubectl delete pods -n "$NAMESPACE" -l app=postgres --grace-period=0 --force 2>/dev/null || true
        fi
    fi
    
    log "Infrastructure services shutdown completed"
}

# Clean up resources
cleanup_resources() {
    emergency "Cleaning up resources..."
    
    # Delete services
    kubectl delete services --all -n "$NAMESPACE" --grace-period=5 2>/dev/null || warn "Service cleanup failed"
    
    # Delete ingress
    kubectl delete ingress --all -n "$NAMESPACE" --grace-period=5 2>/dev/null || warn "Ingress cleanup failed"
    
    # Delete horizontal pod autoscalers
    kubectl delete hpa --all -n "$NAMESPACE" 2>/dev/null || warn "HPA cleanup failed"
    
    # Delete network policies
    kubectl delete networkpolicy --all -n "$NAMESPACE" 2>/dev/null || warn "NetworkPolicy cleanup failed"
    
    # Clean up jobs and cronjobs
    kubectl delete jobs --all -n "$NAMESPACE" --grace-period=5 2>/dev/null || warn "Jobs cleanup failed"
    kubectl delete cronjobs --all -n "$NAMESPACE" 2>/dev/null || warn "CronJobs cleanup failed"
    
    if [[ "$PRESERVE_DATA" == false ]]; then
        critical "⚠️  PURGING ALL DATA ⚠️"
        
        # Delete persistent volume claims (THIS WILL DELETE ALL DATA!)
        kubectl delete pvc --all -n "$NAMESPACE" --grace-period=5 2>/dev/null || warn "PVC cleanup failed"
        
        # Delete secrets
        kubectl delete secrets --all -n "$NAMESPACE" --grace-period=5 2>/dev/null || warn "Secrets cleanup failed"
        
        # Delete configmaps
        kubectl delete configmaps --all -n "$NAMESPACE" --grace-period=5 2>/dev/null || warn "ConfigMaps cleanup failed"
        
        critical "ALL DATA HAS BEEN PURGED"
    else
        log "Data preserved - PVCs and secrets retained"
    fi
    
    log "Resource cleanup completed"
}

# Verify shutdown
verify_shutdown() {
    log "Verifying shutdown completion..."
    
    # Check for remaining pods
    local remaining_pods=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
    
    if [[ $remaining_pods -eq 0 ]]; then
        log "All pods successfully terminated"
    else
        warn "$remaining_pods pods still running:"
        kubectl get pods -n "$NAMESPACE" 2>/dev/null || true
        
        if [[ "$SHUTDOWN_TYPE" == "immediate" ]]; then
            emergency "Force deleting remaining pods..."
            kubectl delete pods --all -n "$NAMESPACE" --grace-period=0 --force 2>/dev/null || true
        fi
    fi
    
    # Check services
    local remaining_services=$(kubectl get services -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
    if [[ $remaining_services -eq 0 ]]; then
        log "All services successfully removed"
    else
        warn "$remaining_services services still exist"
    fi
    
    # Final status
    echo ""
    echo -e "${BOLD}${BLUE}Final System Status:${NC}"
    kubectl get all -n "$NAMESPACE" 2>/dev/null || echo "No resources remaining"
    echo ""
    
    log "Shutdown verification completed"
}

# Generate shutdown report
generate_shutdown_report() {
    log "Generating shutdown report..."
    
    local report_file="/tmp/emergency-shutdown-report-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$report_file" << EOF
Project Sentinel Emergency Shutdown Report
==========================================

Shutdown Details:
- Type: $SHUTDOWN_TYPE
- Namespace: $NAMESPACE
- Data Preserved: $PRESERVE_DATA
- Executed: $(date)
- Executed By: $(whoami)@$(hostname)
- Reason: Emergency shutdown initiated

Final System Status:
EOF
    
    kubectl get all -n "$NAMESPACE" >> "$report_file" 2>/dev/null || echo "No resources remaining" >> "$report_file"
    
    if [[ "$PRESERVE_DATA" == true ]]; then
        echo "" >> "$report_file"
        echo "Persistent Resources (Preserved):" >> "$report_file"
        kubectl get pvc -n "$NAMESPACE" >> "$report_file" 2>/dev/null || echo "No PVCs found" >> "$report_file"
        kubectl get secrets -n "$NAMESPACE" >> "$report_file" 2>/dev/null || echo "No secrets found" >> "$report_file"
    fi
    
    log "Shutdown report: $report_file"
    
    # Display final summary
    echo ""
    echo -e "${BOLD}${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${RED}║                    SHUTDOWN COMPLETED                        ║${NC}"  
    echo -e "${BOLD}${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BOLD}Project Sentinel has been shut down.${NC}"
    echo -e "${BOLD}Type:${NC} $SHUTDOWN_TYPE"
    echo -e "${BOLD}Data:${NC} $(if [[ "$PRESERVE_DATA" == true ]]; then echo "PRESERVED"; else echo "PURGED"; fi)"
    echo -e "${BOLD}Report:${NC} $report_file"
    echo ""
}

# Main execution function
main() {
    print_emergency_header
    
    # Critical confirmation
    if [[ "$CONFIRMATION_REQUIRED" == true ]]; then
        echo -e "${BOLD}${RED}🚨 FINAL CONFIRMATION REQUIRED 🚨${NC}"
        echo ""
        echo -e "${YELLOW}This will immediately shut down the entire Project Sentinel system.${NC}"
        echo -e "${YELLOW}All running services will be terminated.${NC}"
        
        if [[ "$PRESERVE_DATA" == false ]]; then
            echo -e "${BOLD}${RED}⚠️  ALL DATA WILL BE PERMANENTLY DELETED ⚠️${NC}"
        fi
        
        echo ""
        echo -e "${BOLD}Type 'EMERGENCY SHUTDOWN CONFIRMED' to proceed:${NC}"
        read -r confirmation
        
        if [[ "$confirmation" != "EMERGENCY SHUTDOWN CONFIRMED" ]]; then
            log "Emergency shutdown cancelled by user"
            exit 0
        fi
    fi
    
    check_prerequisites
    create_emergency_backup
    notify_monitoring
    
    emergency "🚨 INITIATING EMERGENCY SHUTDOWN 🚨"
    
    shutdown_applications
    shutdown_infrastructure
    cleanup_resources
    verify_shutdown
    generate_shutdown_report
    
    emergency "🆘 EMERGENCY SHUTDOWN COMPLETED 🆘"
    echo -e "${BOLD}${RED}Project Sentinel system has been shut down.${NC}"
    
    if [[ "$PRESERVE_DATA" == false ]]; then
        echo -e "${BOLD}${RED}⚠️  ALL DATA HAS BEEN PERMANENTLY DELETED ⚠️${NC}"
    fi
}

# Execute main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
