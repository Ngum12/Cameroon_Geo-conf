#!/bin/bash

# Project Sentinel - Restore Script
# Cameroon Defense Force - RESTRICTED
# Restores system from backup archives

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
NAMESPACE="sentinel-prod"
BACKUP_DIR="/opt/sentinel/backups"
RESTORE_TYPE="full"
BACKUP_NAME=""
TEST_MODE=false

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
    echo "  --backup NAME    Backup name/timestamp to restore (default: latest)"
    echo "  --test           Test restore procedure without actual restore"
    echo "  --database-only  Restore database only"
    echo "  --configs-only   Restore configurations only"
    echo "  --namespace NS   Kubernetes namespace (default: sentinel-prod)"
    echo "  --backup-dir DIR Backup directory (default: /opt/sentinel/backups)"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --test                        # Test restore procedure"
    echo "  $0 --backup 20241127-143022      # Restore specific backup"
    echo "  $0 --database-only               # Database restore only"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backup)
            BACKUP_NAME="$2"
            shift 2
            ;;
        --test)
            TEST_MODE=true
            shift
            ;;
        --database-only)
            RESTORE_TYPE="database"
            shift
            ;;
        --configs-only)
            RESTORE_TYPE="configs"
            shift
            ;;
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --backup-dir)
            BACKUP_DIR="$2"
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

# Determine backup location
setup_restore_paths() {
    if [[ -z "$BACKUP_NAME" ]]; then
        RESTORE_PATH="${BACKUP_DIR}/latest"
        if [[ ! -L "$RESTORE_PATH" ]]; then
            error "Latest backup symlink not found"
        fi
        RESTORE_PATH=$(readlink -f "$RESTORE_PATH")
        BACKUP_NAME=$(basename "$RESTORE_PATH")
    else
        RESTORE_PATH="${BACKUP_DIR}/${BACKUP_NAME}"
        if [[ ! -d "$RESTORE_PATH" ]]; then
            error "Backup directory not found: $RESTORE_PATH"
        fi
    fi
    
    log "Restore source: $RESTORE_PATH"
    log "Backup name: $BACKUP_NAME"
}

# Validate backup integrity
validate_backup() {
    log "Validating backup integrity..."
    
    # Check manifest file
    if [[ ! -f "$RESTORE_PATH/manifest.json" ]]; then
        error "Backup manifest not found"
    fi
    
    # Parse manifest
    local backup_type=$(jq -r '.backup_type' "$RESTORE_PATH/manifest.json" 2>/dev/null || echo "unknown")
    local timestamp=$(jq -r '.timestamp' "$RESTORE_PATH/manifest.json" 2>/dev/null || echo "unknown")
    
    log "Backup type: $backup_type"
    log "Backup timestamp: $timestamp"
    
    # Check required components
    local required_files=()
    
    if [[ "$RESTORE_TYPE" == "full" ]] || [[ "$RESTORE_TYPE" == "database" ]]; then
        required_files+=("database/sentinel_db.sql.gz" "database/globals.sql.gz")
    fi
    
    if [[ "$RESTORE_TYPE" == "full" ]] || [[ "$RESTORE_TYPE" == "configs" ]]; then
        required_files+=("configs/all-resources.yaml")
    fi
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$RESTORE_PATH/$file" ]]; then
            error "Required backup file missing: $file"
        fi
    done
    
    log "Backup validation completed"
}

# Create pre-restore backup
create_pre_restore_backup() {
    if [[ "$TEST_MODE" == true ]]; then
        log "TEST MODE: Skipping pre-restore backup"
        return 0
    fi
    
    log "Creating pre-restore backup..."
    
    local pre_restore_dir="${BACKUP_DIR}/pre-restore-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$pre_restore_dir"
    
    # Quick database backup
    local postgres_pod=$(kubectl get pods -n "$NAMESPACE" -l app=postgres -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [[ -n "$postgres_pod" ]]; then
        kubectl exec -n "$NAMESPACE" "$postgres_pod" -- pg_dump -U postgres -d sentinel_db > "$pre_restore_dir/pre-restore-db.sql" || true
    fi
    
    # Backup current configs
    kubectl get all -n "$NAMESPACE" -o yaml > "$pre_restore_dir/current-resources.yaml" || true
    
    log "Pre-restore backup created: $pre_restore_dir"
}

# Stop running services
stop_services() {
    if [[ "$TEST_MODE" == true ]]; then
        log "TEST MODE: Would stop services in namespace $NAMESPACE"
        return 0
    fi
    
    log "Stopping services..."
    
    # Scale down deployments
    local deployments=$(kubectl get deployments -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
    
    for deployment in $deployments; do
        if [[ "$deployment" != "postgres" ]]; then  # Keep postgres running for restore
            log "Scaling down deployment: $deployment"
            kubectl scale deployment "$deployment" -n "$NAMESPACE" --replicas=0 || warn "Failed to scale down $deployment"
        fi
    done
    
    # Wait for pods to terminate
    sleep 30
    
    log "Services stopped"
}

# Restore database
restore_database() {
    if [[ "$RESTORE_TYPE" != "full" ]] && [[ "$RESTORE_TYPE" != "database" ]]; then
        return 0
    fi
    
    if [[ "$TEST_MODE" == true ]]; then
        log "TEST MODE: Would restore database from $RESTORE_PATH/database/"
        return 0
    fi
    
    log "Restoring database..."
    
    local postgres_pod=$(kubectl get pods -n "$NAMESPACE" -l app=postgres -o jsonpath='{.items[0].metadata.name}')
    
    if [[ -z "$postgres_pod" ]]; then
        error "PostgreSQL pod not found"
    fi
    
    # Drop and recreate database
    log "Recreating database..."
    kubectl exec -n "$NAMESPACE" "$postgres_pod" -- psql -U postgres -c "DROP DATABASE IF EXISTS sentinel_db;"
    kubectl exec -n "$NAMESPACE" "$postgres_pod" -- psql -U postgres -c "CREATE DATABASE sentinel_db;"
    kubectl exec -n "$NAMESPACE" "$postgres_pod" -- psql -U postgres -d sentinel_db -c "CREATE EXTENSION IF NOT EXISTS postgis;"
    
    # Restore globals (users, roles)
    log "Restoring database globals..."
    gunzip -c "$RESTORE_PATH/database/globals.sql.gz" | kubectl exec -i -n "$NAMESPACE" "$postgres_pod" -- psql -U postgres
    
    # Restore main database
    log "Restoring main database..."
    gunzip -c "$RESTORE_PATH/database/sentinel_db.sql.gz" | kubectl exec -i -n "$NAMESPACE" "$postgres_pod" -- psql -U postgres -d sentinel_db
    
    log "Database restoration completed"
}

# Restore configurations
restore_configs() {
    if [[ "$RESTORE_TYPE" != "full" ]] && [[ "$RESTORE_TYPE" != "configs" ]]; then
        return 0
    fi
    
    if [[ "$TEST_MODE" == true ]]; then
        log "TEST MODE: Would restore Kubernetes configurations"
        return 0
    fi
    
    log "Restoring Kubernetes configurations..."
    
    # Apply saved configurations
    if [[ -f "$RESTORE_PATH/configs/all-resources.yaml" ]]; then
        kubectl apply -f "$RESTORE_PATH/configs/all-resources.yaml" -n "$NAMESPACE" || warn "Some resources failed to apply"
    fi
    
    if [[ -f "$RESTORE_PATH/configs/configmaps.yaml" ]]; then
        kubectl apply -f "$RESTORE_PATH/configs/configmaps.yaml" -n "$NAMESPACE" || warn "ConfigMaps failed to apply"
    fi
    
    if [[ -f "$RESTORE_PATH/configs/pvcs.yaml" ]]; then
        kubectl apply -f "$RESTORE_PATH/configs/pvcs.yaml" -n "$NAMESPACE" || warn "PVCs failed to apply"
    fi
    
    log "Configuration restoration completed"
}

# Restore persistent volumes
restore_volumes() {
    if [[ "$RESTORE_TYPE" != "full" ]]; then
        return 0
    fi
    
    if [[ "$TEST_MODE" == true ]]; then
        log "TEST MODE: Would restore persistent volumes from $RESTORE_PATH/volumes/"
        return 0
    fi
    
    log "Restoring persistent volumes..."
    
    # Find volume backups
    local volume_backups=$(find "$RESTORE_PATH/volumes/" -name "*.tar.gz" 2>/dev/null || echo "")
    
    for backup_file in $volume_backups; do
        local pvc_name=$(basename "$backup_file" .tar.gz)
        log "Restoring volume: $pvc_name"
        
        # Create temporary restoration pod
        kubectl run -n "$NAMESPACE" restore-helper-$RANDOM \
            --image=busybox \
            --restart=Never \
            --rm -i \
            --overrides='
{
    "spec": {
        "containers": [
            {
                "name": "restore-helper",
                "image": "busybox",
                "command": ["tar", "xzf", "/backup/'$(basename "$backup_file")'", "-C", "/data"],
                "volumeMounts": [
                    {
                        "name": "data-volume",
                        "mountPath": "/data"
                    },
                    {
                        "name": "backup-volume",
                        "mountPath": "/backup"
                    }
                ]
            }
        ],
        "volumes": [
            {
                "name": "data-volume",
                "persistentVolumeClaim": {
                    "claimName": "'$pvc_name'"
                }
            },
            {
                "name": "backup-volume",
                "hostPath": {
                    "path": "'$RESTORE_PATH/volumes'"
                }
            }
        ]
    }
}' || warn "Failed to restore volume: $pvc_name"
    done
    
    log "Volume restoration completed"
}

# Start services
start_services() {
    if [[ "$TEST_MODE" == true ]]; then
        log "TEST MODE: Would start all services"
        return 0
    fi
    
    log "Starting services..."
    
    # Scale up deployments
    local deployments=$(kubectl get deployments -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
    
    for deployment in $deployments; do
        if [[ "$deployment" != "postgres" ]]; then
            log "Scaling up deployment: $deployment"
            kubectl scale deployment "$deployment" -n "$NAMESPACE" --replicas=2 || warn "Failed to scale up $deployment"
        fi
    done
    
    # Wait for services to start
    sleep 60
    
    log "Services started"
}

# Verify restoration
verify_restore() {
    log "Verifying restoration..."
    
    if [[ "$TEST_MODE" == true ]]; then
        log "TEST MODE: Verification completed successfully"
        return 0
    fi
    
    # Check pod status
    local running_pods=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase=Running --no-headers | wc -l)
    log "Running pods: $running_pods"
    
    # Test database connection
    local postgres_pod=$(kubectl get pods -n "$NAMESPACE" -l app=postgres -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    if [[ -n "$postgres_pod" ]]; then
        kubectl exec -n "$NAMESPACE" "$postgres_pod" -- psql -U postgres -d sentinel_db -c "SELECT COUNT(*) FROM django_migrations;" > /dev/null
        if [[ $? -eq 0 ]]; then
            log "Database connectivity verified"
        else
            warn "Database connectivity check failed"
        fi
    fi
    
    # Run status check
    if command -v "./scripts/status-check.sh" &> /dev/null; then
        log "Running comprehensive status check..."
        ./scripts/status-check.sh --namespace "$NAMESPACE" || warn "Status check reported issues"
    fi
    
    log "Verification completed"
}

# Generate restoration report
generate_report() {
    log "Generating restoration report..."
    
    local report_file="${BACKUP_DIR}/restore-report-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$report_file" << EOF
Project Sentinel Restoration Report
===================================

Restore Details:
- Backup Name: $BACKUP_NAME
- Restore Type: $RESTORE_TYPE
- Test Mode: $TEST_MODE
- Namespace: $NAMESPACE
- Timestamp: $(date)

Restoration Status: $(if [[ "$TEST_MODE" == true ]]; then echo "TEST COMPLETED"; else echo "COMPLETED"; fi)
EOF
    
    if [[ "$TEST_MODE" == false ]]; then
        echo "" >> "$report_file"
        echo "System Status:" >> "$report_file"
        kubectl get pods -n "$NAMESPACE" >> "$report_file" 2>/dev/null || true
    fi
    
    log "Restoration report: $report_file"
}

# Main execution function
main() {
    log "🔄 Starting Project Sentinel restoration process"
    log "Restore type: $RESTORE_TYPE"
    log "Test mode: $TEST_MODE"
    log "Namespace: $NAMESPACE"
    
    # Prerequisites check
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed"
    fi
    
    if ! command -v jq &> /dev/null; then
        error "jq is not installed"
    fi
    
    setup_restore_paths
    validate_backup
    
    if [[ "$TEST_MODE" == false ]]; then
        # Confirmation prompt
        echo -e "${YELLOW}WARNING: This will restore data from backup: $BACKUP_NAME${NC}"
        echo -e "${YELLOW}Current data in namespace '$NAMESPACE' may be overwritten.${NC}"
        echo -n "Continue? (yes/no): "
        read -r confirmation
        
        if [[ "$confirmation" != "yes" ]]; then
            log "Restoration cancelled by user"
            exit 0
        fi
        
        create_pre_restore_backup
        stop_services
    fi
    
    restore_database
    restore_configs
    restore_volumes
    
    if [[ "$TEST_MODE" == false ]]; then
        start_services
    fi
    
    verify_restore
    generate_report
    
    if [[ "$TEST_MODE" == true ]]; then
        log "✅ Project Sentinel restore test completed successfully!"
    else
        log "✅ Project Sentinel restoration completed successfully!"
        log "📊 Restoration report generated"
    fi
}

# Execute main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
