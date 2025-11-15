#!/bin/bash

# PROJECT SENTINEL - Database Restore Script
# Restore PostgreSQL database from backup

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

BACKUP_DIR="$HOME/sentinel_backups"

echo -e "${YELLOW}Project Sentinel - Database Restore${NC}"
echo "======================================"
echo ""

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}✗ Backup directory not found: $BACKUP_DIR${NC}"
    exit 1
fi

# List available backups
echo -e "${GREEN}Available backups:${NC}"
echo ""
BACKUPS=($(ls -t "$BACKUP_DIR"/sentinel_backup_*.sql.gz 2>/dev/null))

if [ ${#BACKUPS[@]} -eq 0 ]; then
    echo -e "${RED}✗ No backups found in $BACKUP_DIR${NC}"
    exit 1
fi

# Display backups with numbers
for i in "${!BACKUPS[@]}"; do
    BACKUP_FILE="${BACKUPS[$i]}"
    BACKUP_NAME=$(basename "$BACKUP_FILE")
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    BACKUP_DATE=$(stat -c %y "$BACKUP_FILE" 2>/dev/null || stat -f "%Sm" "$BACKUP_FILE")
    echo "$((i+1)). $BACKUP_NAME ($BACKUP_SIZE) - $BACKUP_DATE"
done

echo ""
read -p "Enter backup number to restore (or 'q' to quit): " BACKUP_NUM

if [ "$BACKUP_NUM" = "q" ]; then
    echo "Cancelled."
    exit 0
fi

# Validate input
if ! [[ "$BACKUP_NUM" =~ ^[0-9]+$ ]] || [ "$BACKUP_NUM" -lt 1 ] || [ "$BACKUP_NUM" -gt ${#BACKUPS[@]} ]; then
    echo -e "${RED}✗ Invalid selection${NC}"
    exit 1
fi

SELECTED_BACKUP="${BACKUPS[$((BACKUP_NUM-1))]}"
echo ""
echo -e "${YELLOW}Selected backup: $(basename "$SELECTED_BACKUP")${NC}"
echo ""
echo -e "${RED}⚠ WARNING: This will OVERWRITE the current database!${NC}"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running!${NC}"
    exit 1
fi

# Check if PostgreSQL container is running
if ! docker ps | grep -q sentinel-postgres; then
    echo -e "${RED}✗ PostgreSQL container is not running!${NC}"
    echo "Start services with: docker-compose up -d"
    exit 1
fi

echo ""
echo -e "${YELLOW}Stopping dependent services...${NC}"
docker-compose stop backend human-interface rl-system frontend

echo -e "${YELLOW}Decompressing backup...${NC}"
TMP_FILE="/tmp/sentinel_restore_$$.sql"
gunzip -c "$SELECTED_BACKUP" > "$TMP_FILE"

echo -e "${YELLOW}Dropping existing database...${NC}"
docker-compose exec -T postgres psql -U sentinel_user -d postgres -c "DROP DATABASE IF EXISTS sentinel_db;"

echo -e "${YELLOW}Creating new database...${NC}"
docker-compose exec -T postgres psql -U sentinel_user -d postgres -c "CREATE DATABASE sentinel_db;"

echo -e "${YELLOW}Restoring database...${NC}"
if cat "$TMP_FILE" | docker-compose exec -T postgres psql -U sentinel_user -d sentinel_db; then
    echo -e "${GREEN}✓ Database restored successfully${NC}"
    
    # Cleanup
    rm "$TMP_FILE"
    
    echo ""
    echo -e "${YELLOW}Restarting services...${NC}"
    docker-compose up -d
    
    echo ""
    echo -e "${GREEN}✓ Restore complete!${NC}"
    echo ""
    echo "Services are starting up. Wait 30 seconds and check status with:"
    echo "docker-compose ps"
else
    echo -e "${RED}✗ Restore failed!${NC}"
    rm "$TMP_FILE"
    
    echo ""
    echo "Attempting to restart services..."
    docker-compose up -d
    exit 1
fi




