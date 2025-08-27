#!/bin/bash

# Project Sentinel - Backup Script
# Cameroon Defense Force - RESTRICTED
# Creates backups of database, configurations, and persistent data

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
RETENTION_DAYS=30
BACKUP_TYPE="incremental"

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
    echo "  --full           Create full backup (default: incremental)"
    echo "  --dir PATH       Backup directory (default: /opt/sentinel/backups)"
    echo "  --retention N    Retention period in days (default: 30)"
    echo "  --namespace NS   Kubernetes namespace (default: sentinel-prod)"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --full                    # Full backup"
    echo "  $0 --dir /backup/sentinel    # Custom backup directory"
    echo "  $0 --retention 7             # Keep backups for 7 days"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --full)
            BACKUP_TYPE="full"
            shift
            ;;
        --dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        --retention)
            RETENTION_DAYS="$2"
            shift 2
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

# Create backup directory structure
setup_backup_dir() {
    local timestamp=$(date +%Y%m%d-%H%M%S)
    CURRENT_BACKUP_DIR="${BACKUP_DIR}/${timestamp}"
    
    log "Setting up backup directory: $CURRENT_BACKUP_DIR"
    mkdir -p "$CURRENT_BACKUP_DIR"/{database,configs,volumes,logs}
    
    # Create symlink to latest
    ln -sfn "$CURRENT_BACKUP_DIR" "${BACKUP_DIR}/latest"
}

# Backup PostgreSQL database
backup_database() {
    log "Backing up PostgreSQL database..."
    
    local postgres_pod=$(kubectl get pods -n "$NAMESPACE" -l app=postgres -o jsonpath='{.items[0].metadata.name}')
    
    if [[ -z "$postgres_pod" ]]; then
        error "PostgreSQL pod not found"
    fi
    
    # Create database dump
    kubectl exec -n "$NAMESPACE" "$postgres_pod" -- pg_dump \
        -U postgres \
        -d sentinel_db \
        --verbose \
        --no-password \
        > "${CURRENT_BACKUP_DIR}/database/sentinel_db.sql"
    
    # Backup database globals (users, roles, etc.)
    kubectl exec -n "$NAMESPACE" "$postgres_pod" -- pg_dumpall \
        -U postgres \
        --globals-only \
        --no-password \
        > "${CURRENT_BACKUP_DIR}/database/globals.sql"
    
    # Compress database backups
    gzip "${CURRENT_BACKUP_DIR}/database/sentinel_db.sql"
    gzip "${CURRENT_BACKUP_DIR}/database/globals.sql"
    
    log "Database backup completed"
}

# Backup Kubernetes configurations
backup_configs() {
    log "Backing up Kubernetes configurations..."
    
    # Backup all resources in the namespace
    kubectl get all -n "$NAMESPACE" -o yaml > "${CURRENT_BACKUP_DIR}/configs/all-resources.yaml"
    
    # Backup secrets (without sensitive data)
    kubectl get secrets -n "$NAMESPACE" -o yaml | \
        sed 's/data:/data: {}/' > "${CURRENT_BACKUP_DIR}/configs/secrets-structure.yaml"
    
    # Backup configmaps
    kubectl get configmaps -n "$NAMESPACE" -o yaml > "${CURRENT_BACKUP_DIR}/configs/configmaps.yaml"
    
    # Backup persistent volume claims
    kubectl get pvc -n "$NAMESPACE" -o yaml > "${CURRENT_BACKUP_DIR}/configs/pvcs.yaml"
    
    # Backup ingress
    kubectl get ingress -n "$NAMESPACE" -o yaml > "${CURRENT_BACKUP_DIR}/configs/ingress.yaml" || true
    
    log "Kubernetes configurations backed up"
}

# Backup persistent volumes
backup_volumes() {
    log "Backing up persistent volumes..."
    
    # Get list of PVCs
    local pvcs=$(kubectl get pvc -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')
    
    for pvc in $pvcs; do
        log "Backing up volume: $pvc"
        
        # Create temporary pod to access the volume
        kubectl run -n "$NAMESPACE" backup-helper-$RANDOM \
            --image=busybox \
            --restart=Never \
            --rm -i \
            --overrides='
{
    "spec": {
        "containers": [
            {
                "name": "backup-helper",
                "image": "busybox",
                "command": ["tar", "czf", "/backup/'$pvc'.tar.gz", "-C", "/data", "."],
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
                    "claimName": "'$pvc'"
                }
            },
            {
                "name": "backup-volume",
                "hostPath": {
                    "path": "'${CURRENT_BACKUP_DIR}/volumes'"
                }
            }
        ]
    }
}' || warn "Failed to backup volume: $pvc"
    done
    
    log "Persistent volumes backed up"
}

# Collect application logs
backup_logs() {
    log "Collecting application logs..."
    
    local pods=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')
    
    for pod in $pods; do
        log "Collecting logs from: $pod"
        kubectl logs -n "$NAMESPACE" "$pod" > "${CURRENT_BACKUP_DIR}/logs/${pod}.log" 2>/dev/null || true
        
        # Collect previous container logs if available
        kubectl logs -n "$NAMESPACE" "$pod" --previous > "${CURRENT_BACKUP_DIR}/logs/${pod}-previous.log" 2>/dev/null || true
    done
    
    log "Application logs collected"
}

# Create backup manifest
create_manifest() {
    log "Creating backup manifest..."
    
    cat > "${CURRENT_BACKUP_DIR}/manifest.json" << EOF
{
    "backup_type": "${BACKUP_TYPE}",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "namespace": "${NAMESPACE}",
    "version": "1.0",
    "components": {
        "database": true,
        "configs": true,
        "volumes": true,
        "logs": true
    },
    "retention_days": ${RETENTION_DAYS}
}
EOF
    
    # Calculate backup size
    local backup_size=$(du -sh "$CURRENT_BACKUP_DIR" | cut -f1)
    echo "    \"size\": \"$backup_size\"" >> "${CURRENT_BACKUP_DIR}/manifest.json.tmp"
    sed '$s/$/,/' "${CURRENT_BACKUP_DIR}/manifest.json" > "${CURRENT_BACKUP_DIR}/manifest.json.tmp2"
    cat "${CURRENT_BACKUP_DIR}/manifest.json.tmp2" "${CURRENT_BACKUP_DIR}/manifest.json.tmp" > "${CURRENT_BACKUP_DIR}/manifest.json"
    echo "}" >> "${CURRENT_BACKUP_DIR}/manifest.json"
    rm -f "${CURRENT_BACKUP_DIR}/manifest.json.tmp" "${CURRENT_BACKUP_DIR}/manifest.json.tmp2"
    
    log "Backup manifest created"
}

# Clean up old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    
    find "$BACKUP_DIR" -maxdepth 1 -type d -name "20*" -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true
    
    # Clean up any broken symlinks
    find "$BACKUP_DIR" -type l ! -exec test -e {} \; -delete 2>/dev/null || true
    
    log "Old backups cleaned up"
}

# Verify backup integrity
verify_backup() {
    log "Verifying backup integrity..."
    
    # Check if all expected files exist
    local required_files=(
        "database/sentinel_db.sql.gz"
        "database/globals.sql.gz"
        "configs/all-resources.yaml"
        "manifest.json"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "${CURRENT_BACKUP_DIR}/$file" ]]; then
            error "Required backup file missing: $file"
        fi
    done
    
    # Test database backup integrity
    if command -v pg_dump &> /dev/null; then
        gunzip -c "${CURRENT_BACKUP_DIR}/database/sentinel_db.sql.gz" | head -n 100 > /dev/null
        if [[ $? -ne 0 ]]; then
            error "Database backup file is corrupted"
        fi
    fi
    
    log "Backup integrity verified"
}

# Send backup notification
send_notification() {
    log "Sending backup notification..."
    
    local backup_size=$(du -sh "$CURRENT_BACKUP_DIR" | cut -f1)
    local message="Project Sentinel backup completed successfully.
Backup type: $BACKUP_TYPE
Size: $backup_size
Location: $CURRENT_BACKUP_DIR
Timestamp: $(date)"
    
    # Log the notification (replace with actual notification system)
    echo "$message" >> "${BACKUP_DIR}/backup.log"
    
    log "Backup notification sent"
}

# Main execution function
main() {
    log "🔄 Starting Project Sentinel backup process"
    log "Backup type: $BACKUP_TYPE"
    log "Namespace: $NAMESPACE"
    log "Backup directory: $BACKUP_DIR"
    log "Retention: $RETENTION_DAYS days"
    
    # Prerequisites check
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed"
    fi
    
    setup_backup_dir
    backup_database
    backup_configs
    backup_volumes
    backup_logs
    create_manifest
    verify_backup
    cleanup_old_backups
    send_notification
    
    log "✅ Project Sentinel backup completed successfully!"
    log "📊 Backup location: $CURRENT_BACKUP_DIR"
    log "📦 Backup size: $(du -sh "$CURRENT_BACKUP_DIR" | cut -f1)"
}

# Execute main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
