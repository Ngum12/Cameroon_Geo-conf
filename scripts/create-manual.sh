#!/bin/bash

# Project Sentinel - Operator Manual Generator
# Cameroon Defense Force - RESTRICTED  
# Creates comprehensive operator manual for field deployment

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
OUTPUT_FILE="SENTINEL_OPERATOR_MANUAL.md"
INCLUDE_TECHNICAL=true
FORMAT="markdown"

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
    echo "  --output FILE        Output file name (default: SENTINEL_OPERATOR_MANUAL.md)"
    echo "  --format FORMAT      Output format: markdown, pdf, html (default: markdown)"
    echo "  --no-technical       Exclude technical details"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Generate standard manual"
    echo "  $0 --output field_manual.md         # Custom filename"
    echo "  $0 --format pdf                     # PDF format"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --no-technical)
            INCLUDE_TECHNICAL=false
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

# Generate operator manual
generate_manual() {
    log "Generating Project Sentinel Operator Manual..."
    
    cat > "$OUTPUT_FILE" << 'EOF'
# PROJECT SENTINEL
## OPERATOR MANUAL

**🇨🇲 CAMEROON DEFENSE FORCE - RESTRICTED**

---

### DOCUMENT CLASSIFICATION
**RESTRICTED - AUTHORIZED PERSONNEL ONLY**

**Document Control:**
- **Version:** 1.0
- **Effective Date:** 2024
- **Classification:** RESTRICTED
- **Distribution:** Authorized Operations Personnel Only
- **Review Cycle:** Quarterly

---

## TABLE OF CONTENTS

1. [SYSTEM OVERVIEW](#1-system-overview)
2. [OPERATIONAL PROCEDURES](#2-operational-procedures)  
3. [DAILY OPERATIONS](#3-daily-operations)
4. [EMERGENCY PROCEDURES](#4-emergency-procedures)
5. [MAINTENANCE](#5-maintenance)
6. [TROUBLESHOOTING](#6-troubleshooting)
7. [SECURITY PROTOCOLS](#7-security-protocols)
8. [CONTACT INFORMATION](#8-contact-information)
9. [APPENDICES](#9-appendices)

---

## 1. SYSTEM OVERVIEW

### 1.1 Mission Statement
Project Sentinel provides real-time Open Source Intelligence (OSINT) analysis capabilities for the Cameroon Defense Force. The system collects, processes, and visualizes intelligence data from publicly available sources.

### 1.2 System Components
- **Data Collection**: Automated web crawling and data ingestion
- **Language Processing**: Multi-language translation and entity recognition
- **Intelligence Analysis**: Geospatial analysis and event correlation
- **Visualization**: Interactive dashboard with mapping capabilities
- **Infrastructure**: Kubernetes-based cloud deployment

### 1.3 Key Capabilities
✅ **Real-time Data Processing**: Continuous monitoring of news sources  
✅ **Multi-language Support**: Automatic translation to English  
✅ **Geospatial Intelligence**: Location-based event mapping  
✅ **Entity Recognition**: Automatic extraction of persons, organizations, locations  
✅ **Scalable Architecture**: Handles high data volumes  
✅ **Secure Operations**: Military-grade security controls  

### 1.4 System Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│  Processing      │───▶│   Dashboard     │
│   (News/Web)    │    │  (NLP/Analysis)  │    │   (Operators)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Collection    │    │    Database      │    │   Monitoring    │
│   Services      │    │  (PostGIS)       │    │   & Alerts      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## 2. OPERATIONAL PROCEDURES

### 2.1 System Startup
**CRITICAL**: Follow this sequence exactly to ensure proper system initialization.

#### Step 1: Infrastructure Check
```bash
# 1. Verify cluster connectivity
kubectl cluster-info

# 2. Check namespace status
kubectl get namespace sentinel-prod

# 3. Verify node readiness
kubectl get nodes -o wide
```

#### Step 2: Database Initialization
```bash
# 1. Start PostgreSQL service
kubectl get pods -n sentinel-prod -l app=postgres

# 2. Verify database connectivity
kubectl exec -it deployment/postgres -n sentinel-prod -- pg_isready

# 3. Check PostGIS extension
kubectl exec -it deployment/postgres -n sentinel-prod -- psql -U postgres -d sentinel_db -c "SELECT PostGIS_Version();"
```

#### Step 3: Service Deployment
```bash
# 1. Deploy NLP services
kubectl get deployments -n sentinel-prod

# 2. Check service health
./scripts/status-check.sh --production

# 3. Verify API endpoints
curl -f https://api.sentinel.cdf.cm/health/
```

### 2.2 System Shutdown
**WARNING**: Improper shutdown may result in data loss.

#### Graceful Shutdown Sequence:
1. **Stop Data Ingestion**: Scale ingestion services to 0 replicas
2. **Complete Processing**: Wait for processing queues to empty
3. **Stop API Services**: Scale backend API to 0 replicas
4. **Stop Frontend**: Scale dashboard to 0 replicas
5. **Stop Infrastructure**: Scale database and cache services

```bash
# Execute graceful shutdown
kubectl scale deployment data-ingestion --replicas=0 -n sentinel-prod
kubectl scale deployment backend-api --replicas=0 -n sentinel-prod
kubectl scale deployment frontend-dashboard --replicas=0 -n sentinel-prod
```

#### Emergency Shutdown:
```bash
# Use only in critical situations
./scripts/emergency-shutdown.sh --immediate --force
```

---

## 3. DAILY OPERATIONS

### 3.1 Morning Checklist (08:00 Hours)
**Duration**: ~15 minutes

- [ ] **System Status**: Run `./scripts/status-check.sh --production`
- [ ] **Service Health**: Verify all pods are in `Running` state
- [ ] **Resource Usage**: Check CPU and memory utilization < 80%
- [ ] **Data Ingestion**: Confirm articles processed in last 24 hours
- [ ] **Security Alerts**: Review any overnight security events
- [ ] **Backup Status**: Verify previous night's backup completed successfully

#### Commands:
```bash
# Quick health check
kubectl get pods -n sentinel-prod

# Resource utilization
kubectl top nodes
kubectl top pods -n sentinel-prod

# Recent ingestion statistics  
curl -H "Authorization: Bearer $API_TOKEN" \
  https://api.sentinel.cdf.cm/api/v1/statistics/
```

### 3.2 Midday Check (12:00 Hours)
**Duration**: ~10 minutes

- [ ] **Performance Monitoring**: API response times < 500ms
- [ ] **Error Rates**: System error rate < 1%
- [ ] **Processing Queues**: No significant backlogs
- [ ] **Storage Usage**: Database and volume usage trends
- [ ] **Network Connectivity**: External source accessibility

### 3.3 Evening Review (18:00 Hours)  
**Duration**: ~20 minutes

- [ ] **Daily Statistics**: Review processed data summary
- [ ] **System Performance**: Check daily performance trends
- [ ] **Security Review**: Examine access logs and alerts
- [ ] **Backup Initiation**: Start nightly backup process
- [ ] **Maintenance Planning**: Schedule any required updates

#### Daily Backup:
```bash
# Initiate nightly backup
./scripts/backup.sh --full

# Verify backup completion (check after 30 minutes)
ls -la /opt/sentinel/backups/latest/
```

### 3.4 Weekly Tasks

#### Monday - System Health Analysis
- [ ] Run comprehensive diagnostics
- [ ] Review performance trends from past week
- [ ] Plan capacity adjustments
- [ ] Update system documentation

#### Wednesday - Security Audit
- [ ] Review access control logs
- [ ] Check for security updates
- [ ] Verify network policy effectiveness
- [ ] Update security incident log

#### Friday - Backup and Recovery Testing
- [ ] Test backup integrity: `./scripts/restore.sh --test`
- [ ] Verify disaster recovery procedures
- [ ] Update backup retention policies
- [ ] Document any issues found

---

## 4. EMERGENCY PROCEDURES

### 4.1 System Failure Response

#### Level 1 - Service Degradation
**Indicators**: High latency, partial service availability
**Response Time**: 15 minutes

**Actions**:
1. Run status check: `./scripts/status-check.sh --production`
2. Check resource utilization
3. Scale affected services: `kubectl scale deployment <service> --replicas=3`
4. Monitor recovery
5. Document incident

#### Level 2 - Service Outage
**Indicators**: Complete service unavailability
**Response Time**: 5 minutes

**Actions**:
1. **IMMEDIATE**: Notify operations team
2. Run emergency diagnostics
3. Check infrastructure services (database, network)
4. Consider service restart or rollback
5. Execute recovery procedures

```bash
# Emergency restart sequence
kubectl rollout restart deployment/backend-api -n sentinel-prod
kubectl rollout restart deployment/frontend-dashboard -n sentinel-prod

# If restart fails, consider rollback
./scripts/rollback.sh --version previous --component all
```

#### Level 3 - System Compromise
**Indicators**: Security breach, data integrity concerns
**Response Time**: IMMEDIATE

**Actions**:
1. **CRITICAL**: Execute emergency shutdown
2. Isolate affected systems
3. Notify security team immediately
4. Preserve evidence
5. Activate incident response team

```bash
# Emergency security shutdown
./scripts/emergency-shutdown.sh --immediate --preserve-data
```

### 4.2 Recovery Procedures

#### Standard Recovery
```bash
# 1. Assess damage
./scripts/status-check.sh --production

# 2. Restore from backup
./scripts/restore.sh --backup latest

# 3. Verify system functionality
curl -f https://api.sentinel.cdf.cm/health/

# 4. Resume operations
kubectl scale deployment --all --replicas=2 -n sentinel-prod
```

#### Disaster Recovery
1. **Activate backup systems** at secondary location
2. **Restore data** from latest backup
3. **Reconfigure network** routing
4. **Verify system integrity**
5. **Resume operations** with incident documentation

---

## 5. MAINTENANCE

### 5.1 Routine Maintenance

#### Daily (Automated):
- Log rotation and cleanup
- Temporary file cleanup
- Performance metrics collection
- Security event logging

#### Weekly (Manual):
- System update review
- Backup verification
- Performance analysis
- Security audit

#### Monthly (Scheduled):
- Security patches
- Configuration updates
- Disaster recovery testing
- Documentation updates

### 5.2 Maintenance Windows
**Standard Window**: Sunday 02:00-06:00 (4 hours)
**Emergency Window**: Any time with approval

#### Pre-Maintenance:
1. Schedule downtime notification
2. Create system backup
3. Document maintenance plan
4. Prepare rollback procedures

#### During Maintenance:
1. Follow approved procedures
2. Monitor system status
3. Document all changes
4. Test functionality

#### Post-Maintenance:
1. Verify system operation
2. Update documentation
3. Send completion notification
4. Review any issues

---

## 6. TROUBLESHOOTING

### 6.1 Common Issues

#### Issue: Pod Stuck in Pending State
**Symptoms**: Pods show `Pending` status for > 5 minutes
**Diagnosis**: 
```bash
kubectl describe pod <pod-name> -n sentinel-prod
kubectl get events -n sentinel-prod --sort-by='.lastTimestamp'
```
**Resolution**:
- Check cluster resources: `kubectl top nodes`
- Verify PVC binding: `kubectl get pvc -n sentinel-prod`
- Check node selection constraints

#### Issue: Database Connection Failures
**Symptoms**: Backend API returning 500 errors
**Diagnosis**:
```bash
kubectl logs deployment/backend-api -n sentinel-prod
kubectl exec -it deployment/postgres -n sentinel-prod -- pg_isready
```
**Resolution**:
- Restart PostgreSQL: `kubectl rollout restart deployment/postgres -n sentinel-prod`
- Check database credentials
- Verify network connectivity

#### Issue: High Memory Usage
**Symptoms**: Pods being terminated due to memory limits
**Diagnosis**:
```bash
kubectl top pods -n sentinel-prod
kubectl describe pod <pod-name> -n sentinel-prod
```
**Resolution**:
- Scale up replicas: `kubectl scale deployment <name> --replicas=3`
- Increase memory limits in deployment YAML
- Check for memory leaks in application logs

### 6.2 Diagnostic Commands

#### System Health:
```bash
# Overall status
./scripts/status-check.sh --production --verbose

# Pod status
kubectl get pods -n sentinel-prod -o wide

# Resource usage
kubectl top pods -n sentinel-prod
kubectl top nodes

# Service endpoints
kubectl get endpoints -n sentinel-prod
```

#### Application Debugging:
```bash
# Application logs
kubectl logs deployment/backend-api -n sentinel-prod --tail=100

# Database status
kubectl exec -it deployment/postgres -n sentinel-prod -- \
  psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# NLP service health
kubectl port-forward deployment/translation-service 8080:8000 -n sentinel-prod &
curl http://localhost:8080/health
```

#### Network Diagnostics:
```bash
# DNS resolution
kubectl exec -it deployment/backend-api -n sentinel-prod -- \
  nslookup postgres-service.sentinel-prod.svc.cluster.local

# Connectivity test
kubectl exec -it deployment/backend-api -n sentinel-prod -- \
  nc -zv postgres-service 5432
```

---

## 7. SECURITY PROTOCOLS

### 7.1 Access Control
**CRITICAL**: All operators must follow security protocols

#### Authentication Requirements:
- [ ] Multi-factor authentication enabled
- [ ] Strong password policy (12+ characters, mixed case, numbers, symbols)
- [ ] Regular password rotation (every 90 days)
- [ ] Session timeouts configured (4 hours max)

#### Authorization Levels:
1. **System Administrator**: Full access to all components
2. **Operations Manager**: Read/write access to operations functions
3. **Analyst**: Read-only access to dashboard and reports
4. **Auditor**: Read-only access to logs and audit trails

### 7.2 Security Monitoring

#### Continuous Monitoring:
- [ ] Failed login attempts (alert after 5 attempts)
- [ ] Unusual access patterns
- [ ] System configuration changes
- [ ] Network traffic anomalies
- [ ] Resource usage spikes

#### Security Incident Response:
1. **Detect**: Automated alerts + manual reporting
2. **Contain**: Isolate affected systems
3. **Investigate**: Forensic analysis and evidence collection
4. **Eradicate**: Remove threats and close vulnerabilities  
5. **Recover**: Restore services securely
6. **Learn**: Update procedures and training

### 7.3 Data Protection

#### Classification Handling:
- **TOP SECRET**: Critical intelligence requiring highest protection
- **SECRET**: Processed intelligence with restricted access
- **CONFIDENTIAL**: Raw data requiring controlled access
- **RESTRICTED**: System data with limited distribution

#### Security Controls:
- [ ] Encryption at rest (AES-256)
- [ ] Encryption in transit (TLS 1.3)
- [ ] Network segmentation and isolation
- [ ] Regular vulnerability scans
- [ ] Audit logging of all access

---

## 8. CONTACT INFORMATION

### Primary Contacts

#### Operations Team
- **Operations Manager**: +237-XXX-XXXX-XX
- **Lead Operator**: +237-XXX-XXXX-XX  
- **Backup Operator**: +237-XXX-XXXX-XX
- **Email**: operations@sentinel.cdf.cm

#### Technical Support
- **System Administrator**: +237-XXX-XXXX-XX
- **Database Administrator**: +237-XXX-XXXX-XX
- **Network Administrator**: +237-XXX-XXXX-XX
- **Email**: support@sentinel.cdf.cm

#### Security Team
- **Security Officer**: +237-XXX-XXXX-XX (24/7)
- **Incident Response**: +237-XXX-XXXX-XX (Emergency)
- **Email**: security@sentinel.cdf.cm

#### Management
- **Project Manager**: +237-XXX-XXXX-XX
- **Technical Director**: +237-XXX-XXXX-XX
- **Operations Director**: +237-XXX-XXXX-XX

### Emergency Escalation
1. **Level 1**: Operations Team (15 min response)
2. **Level 2**: Technical Support (30 min response)
3. **Level 3**: Management Team (1 hour response)
4. **Critical**: Security Team (Immediate response)

---

## 9. APPENDICES

### Appendix A: Command Reference

#### Essential Commands:
```bash
# System status
./scripts/status-check.sh --production

# Health check
curl https://api.sentinel.cdf.cm/health/

# Resource monitoring
kubectl top pods -n sentinel-prod

# Backup system
./scripts/backup.sh --full

# Emergency rollback
./scripts/rollback.sh --version previous

# Emergency shutdown
./scripts/emergency-shutdown.sh
```

#### Kubernetes Commands:
```bash
# Pod management
kubectl get pods -n sentinel-prod
kubectl describe pod <name> -n sentinel-prod
kubectl logs <pod-name> -n sentinel-prod
kubectl delete pod <name> -n sentinel-prod

# Deployment management
kubectl get deployments -n sentinel-prod
kubectl scale deployment <name> --replicas=3 -n sentinel-prod
kubectl rollout restart deployment/<name> -n sentinel-prod
kubectl rollout status deployment/<name> -n sentinel-prod

# Service management
kubectl get services -n sentinel-prod
kubectl get endpoints -n sentinel-prod
kubectl port-forward service/<name> 8080:80 -n sentinel-prod
```

### Appendix B: Configuration Files

#### Environment Variables:
```bash
# Production environment
export KUBECONFIG="/etc/kubernetes/admin.conf"
export NAMESPACE="sentinel-prod"
export API_BASE_URL="https://api.sentinel.cdf.cm"
export MONITORING_URL="https://grafana.sentinel.cdf.cm"
```

#### Key File Locations:
```
/opt/sentinel/backups/          # Backup files
/var/log/sentinel/             # System logs
/etc/kubernetes/               # Kubernetes config
~/.kube/config                 # kubectl config
./scripts/                     # Operational scripts
```

### Appendix C: Troubleshooting Checklist

#### System Not Responding:
- [ ] Check cluster connectivity: `kubectl cluster-info`
- [ ] Verify pod status: `kubectl get pods -n sentinel-prod`
- [ ] Check resource usage: `kubectl top nodes`
- [ ] Review recent events: `kubectl get events -n sentinel-prod`
- [ ] Check service endpoints: `kubectl get endpoints -n sentinel-prod`

#### Performance Issues:
- [ ] Monitor resource utilization
- [ ] Check processing queues
- [ ] Review application logs
- [ ] Analyze network latency
- [ ] Scale services if needed

#### Security Concerns:
- [ ] Check access logs
- [ ] Review failed authentication attempts
- [ ] Verify network policies
- [ ] Scan for vulnerabilities
- [ ] Update security measures

---

**DOCUMENT END**

**Classification:** RESTRICTED - Cameroon Defense Force Internal Use Only  
**Document Version:** 1.0  
**Last Updated:** 2024  
**Next Review:** Quarterly  

---

*This manual contains sensitive operational information. Unauthorized disclosure is prohibited and may result in disciplinary action.*
EOF

    log "Operator manual generated: $OUTPUT_FILE"
}

# Convert to different formats
convert_format() {
    if [[ "$FORMAT" != "markdown" ]]; then
        log "Converting to $FORMAT format..."
        
        case "$FORMAT" in
            "pdf")
                if command -v pandoc &> /dev/null; then
                    pandoc "$OUTPUT_FILE" -o "${OUTPUT_FILE%.md}.pdf" --pdf-engine=xelatex
                    log "PDF version created: ${OUTPUT_FILE%.md}.pdf"
                else
                    warn "pandoc not installed - cannot create PDF"
                fi
                ;;
            "html")
                if command -v pandoc &> /dev/null; then
                    pandoc "$OUTPUT_FILE" -o "${OUTPUT_FILE%.md}.html" -s --css=style.css
                    log "HTML version created: ${OUTPUT_FILE%.md}.html"
                else
                    warn "pandoc not installed - cannot create HTML"
                fi
                ;;
            *)
                warn "Unsupported format: $FORMAT"
                ;;
        esac
    fi
}

# Add technical appendix
add_technical_appendix() {
    if [[ "$INCLUDE_TECHNICAL" == true ]]; then
        log "Adding technical appendix..."
        
        cat >> "$OUTPUT_FILE" << 'EOF'

### Appendix D: Technical Details

#### System Architecture Diagram
```
                    ┌─────────────────────────────────────┐
                    │           FRONTEND TIER             │
                    │  ┌─────────────────────────────────┐ │
                    │  │    React Dashboard (Nginx)      │ │
                    │  │         (Port 80/443)           │ │
                    │  └─────────────────────────────────┘ │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────┴───────────────────┐
                    │           APPLICATION TIER          │
                    │  ┌─────────────┐  ┌─────────────────┐ │
                    │  │   Django    │  │   NLP Services  │ │
                    │  │   Backend   │  │  (Translation/  │ │
                    │  │  (Port 8000)│  │   NER/Analysis) │ │
                    │  └─────────────┘  └─────────────────┘ │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────┴───────────────────┐
                    │           DATA TIER                 │
                    │  ┌─────────────┐  ┌─────────────────┐ │
                    │  │ PostgreSQL  │  │     Redis       │ │
                    │  │  + PostGIS  │  │    (Cache)      │ │
                    │  │ (Port 5432) │  │  (Port 6379)    │ │
                    │  └─────────────┘  └─────────────────┘ │
                    └─────────────────────────────────────┘
```

#### Network Architecture
- **Public Internet**: Frontend access via HTTPS (443)
- **DMZ Zone**: Load balancers and reverse proxies
- **Application Zone**: Backend services and APIs
- **Data Zone**: Databases and persistent storage
- **Management Zone**: Monitoring and administrative access

#### Security Zones
1. **External Zone**: Public internet and external data sources
2. **DMZ Zone**: Web servers and load balancers
3. **Internal Zone**: Application services and APIs
4. **Secure Zone**: Databases and sensitive data
5. **Management Zone**: Administrative and monitoring systems

#### Resource Requirements
- **Minimum**: 4 CPU cores, 16GB RAM, 100GB SSD
- **Recommended**: 8 CPU cores, 32GB RAM, 500GB NVMe
- **Production**: 16 CPU cores, 64GB RAM, 1TB NVMe + backup storage

#### Performance Metrics
- **API Response Time**: < 500ms (95th percentile)
- **Dashboard Load Time**: < 3 seconds
- **Data Processing Rate**: > 1000 articles/hour
- **Concurrent Users**: Up to 50 simultaneous users
- **Uptime Target**: 99.5% availability

#### Monitoring Endpoints
- **Health Check**: `GET /health/`
- **Metrics**: `GET /metrics/`
- **Status**: `GET /api/v1/status/`
- **Statistics**: `GET /api/v1/statistics/`

#### Database Schema
```sql
-- Core tables
news_articles (id, url, title, content, source, published_date, location)
processed_articles (id, article_id, entities, translations, analysis)
sources (id, name, url, type, active, last_crawled)
processing_queue (id, article_id, status, priority, created_at)

-- Indexes for performance
CREATE INDEX idx_articles_published ON news_articles(published_date);
CREATE INDEX idx_articles_location ON news_articles USING GIST(location);
CREATE INDEX idx_processed_entities ON processed_articles USING GIN(entities);
```
EOF

        log "Technical appendix added"
    fi
}

# Main execution function
main() {
    log "🚀 Starting Project Sentinel operator manual creation"
    log "Output file: $OUTPUT_FILE"
    log "Format: $FORMAT"
    log "Include technical: $INCLUDE_TECHNICAL"
    
    generate_manual
    
    if [[ "$INCLUDE_TECHNICAL" == true ]]; then
        add_technical_appendix
    fi
    
    convert_format
    
    # Calculate file size
    local size=$(du -sh "$OUTPUT_FILE" | cut -f1)
    local lines=$(wc -l < "$OUTPUT_FILE")
    
    log "✅ Project Sentinel operator manual created successfully!"
    log "📖 File: $OUTPUT_FILE"
    log "📊 Size: $size ($lines lines)"
    
    # Show table of contents
    echo ""
    echo "📚 Manual Contents:"
    grep "^##" "$OUTPUT_FILE" | head -10
    echo ""
    
    # Security reminder
    echo -e "${YELLOW}🔐 SECURITY REMINDER:${NC}"
    echo -e "${YELLOW}   This manual contains RESTRICTED information${NC}"
    echo -e "${YELLOW}   Ensure proper handling and distribution controls${NC}"
    echo ""
}

# Execute main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
