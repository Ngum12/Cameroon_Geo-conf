#!/bin/bash

# PROJECT SENTINEL - Database Backup Script
# Automated PostgreSQL backup with rotation

# Configuration
BACKUP_DIR="$HOME/sentinel_backups"
RETENTION_DAYS=7
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="sentinel_backup_${DATE}.sql"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Project Sentinel - Database Backup${NC}"
echo "======================================"
echo ""

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running!${NC}"
    exit 1
fi

# Check if PostgreSQL container is running
if ! docker ps | grep -q sentinel-postgres; then
    echo -e "${RED}✗ PostgreSQL container is not running!${NC}"
    exit 1
fi

echo -e "${YELLOW}Creating backup...${NC}"

# Create backup
if docker-compose exec -T postgres pg_dump -U sentinel_user sentinel_db > "$BACKUP_DIR/$BACKUP_FILE"; then
    # Compress backup
    gzip "$BACKUP_DIR/$BACKUP_FILE"
    
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/${BACKUP_FILE}.gz" | cut -f1)
    echo -e "${GREEN}✓ Backup created successfully${NC}"
    echo "File: $BACKUP_DIR/${BACKUP_FILE}.gz"
    echo "Size: $BACKUP_SIZE"
    echo ""
    
    # Cleanup old backups
    echo -e "${YELLOW}Cleaning up old backups (older than $RETENTION_DAYS days)...${NC}"
    find "$BACKUP_DIR" -name "sentinel_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    
    # List current backups
    echo ""
    echo -e "${GREEN}Current backups:${NC}"
    ls -lh "$BACKUP_DIR"/sentinel_backup_*.sql.gz 2>/dev/null | awk '{print $9, "(" $5 ")"}'
    
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/sentinel_backup_*.sql.gz 2>/dev/null | wc -l)
    echo ""
    echo -e "${GREEN}Total backups: $BACKUP_COUNT${NC}"
    
else
    echo -e "${RED}✗ Backup failed!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Backup complete!${NC}"




