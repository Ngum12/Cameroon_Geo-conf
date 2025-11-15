# PROJECT SENTINEL - POSTGRESQL BACKUP SYSTEM
# Cameroon Defense Force OSINT Analysis System
# Automated backup and disaster recovery

param(
    [string]$BackupType = "full",
    [string]$OutputDir = "database/backups",
    [switch]$Compress = $true,
    [switch]$Encrypt = $false
)

Write-Host "=================================" -ForegroundColor Green
Write-Host "PROJECT SENTINEL - Database Backup" -ForegroundColor Green
Write-Host "Cameroon Defense Intelligence System" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Configuration
$DatabaseName = "sentinel_defense"
$Username = "sentinel_admin"
$ContainerName = "sentinel-postgresql"
$Timestamp = (Get-Date).ToString("yyyyMMdd_HHmmss")

# Create backup directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Host "Created backup directory: $OutputDir" -ForegroundColor Green
}

# Function to check if container is running
function Test-ContainerRunning {
    param([string]$ContainerName)
    
    $status = docker ps --filter "name=$ContainerName" --format "{{.Status}}" 2>$null
    return -not [string]::IsNullOrEmpty($status)
}

# Function to perform full backup
function Backup-Full {
    $BackupFile = "$OutputDir/sentinel_full_backup_$Timestamp.sql"
    
    Write-Host "Performing full database backup..." -ForegroundColor Cyan
    Write-Host "Output: $BackupFile" -ForegroundColor Gray
    
    $backupCommand = "pg_dump -U $Username -h localhost -p 5432 --verbose --clean --no-acl --no-owner $DatabaseName"
    
    docker exec $ContainerName bash -c $backupCommand | Out-File -FilePath $BackupFile -Encoding UTF8
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Full backup completed successfully!" -ForegroundColor Green
        $fileSize = (Get-Item $BackupFile).Length / 1MB
        Write-Host "Backup size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Gray
        return $BackupFile
    }
    else {
        Write-Host "Full backup failed!" -ForegroundColor Red
        return $null
    }
}

# Function to perform data-only backup
function Backup-DataOnly {
    $BackupFile = "$OutputDir/sentinel_data_backup_$Timestamp.sql"
    
    Write-Host "Performing data-only backup..." -ForegroundColor Cyan
    Write-Host "Output: $BackupFile" -ForegroundColor Gray
    
    $backupCommand = "pg_dump -U $Username -h localhost -p 5432 --verbose --data-only --no-acl --no-owner $DatabaseName"
    
    docker exec $ContainerName bash -c $backupCommand | Out-File -FilePath $BackupFile -Encoding UTF8
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Data backup completed successfully!" -ForegroundColor Green
        return $BackupFile
    }
    else {
        Write-Host "Data backup failed!" -ForegroundColor Red
        return $null
    }
}

# Function to perform schema-only backup
function Backup-SchemaOnly {
    $BackupFile = "$OutputDir/sentinel_schema_backup_$Timestamp.sql"
    
    Write-Host "Performing schema-only backup..." -ForegroundColor Cyan
    Write-Host "Output: $BackupFile" -ForegroundColor Gray
    
    $backupCommand = "pg_dump -U $Username -h localhost -p 5432 --verbose --schema-only --no-acl --no-owner $DatabaseName"
    
    docker exec $ContainerName bash -c $backupCommand | Out-File -FilePath $BackupFile -Encoding UTF8
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Schema backup completed successfully!" -ForegroundColor Green
        return $BackupFile
    }
    else {
        Write-Host "Schema backup failed!" -ForegroundColor Red
        return $null
    }
}

# Function to compress backup
function Compress-Backup {
    param([string]$FilePath)
    
    if (Test-Path $FilePath) {
        Write-Host "Compressing backup..." -ForegroundColor Yellow
        
        $CompressedFile = "$FilePath.gz"
        
        # Use 7-Zip if available, otherwise use PowerShell compression
        if (Get-Command "7z" -ErrorAction SilentlyContinue) {
            7z a -tgzip $CompressedFile $FilePath | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Remove-Item $FilePath
                Write-Host "Backup compressed: $CompressedFile" -ForegroundColor Green
                return $CompressedFile
            }
        }
        else {
            # PowerShell compression (requires .NET 4.5+)
            try {
                Compress-Archive -Path $FilePath -DestinationPath "$FilePath.zip" -CompressionLevel Optimal
                Remove-Item $FilePath
                Write-Host "Backup compressed: $FilePath.zip" -ForegroundColor Green
                return "$FilePath.zip"
            }
            catch {
                Write-Host "Compression failed: $($_.Exception.Message)" -ForegroundColor Red
                return $FilePath
            }
        }
    }
    
    return $FilePath
}

# Function to get database statistics
function Get-DatabaseStats {
    Write-Host "Gathering database statistics..." -ForegroundColor Cyan
    
    $statsQuery = @"
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;
"@
    
    $statsFile = "$OutputDir/sentinel_stats_$Timestamp.txt"
    
    docker exec $ContainerName psql -U $Username -d $DatabaseName -c $statsQuery | Out-File -FilePath $statsFile -Encoding UTF8
    
    Write-Host "Database statistics saved: $statsFile" -ForegroundColor Gray
}

# Function to cleanup old backups
function Cleanup-OldBackups {
    param([int]$RetentionDays = 7)
    
    Write-Host "Cleaning up backups older than $RetentionDays days..." -ForegroundColor Yellow
    
    $cutoffDate = (Get-Date).AddDays(-$RetentionDays)
    $oldBackups = Get-ChildItem -Path $OutputDir -Filter "sentinel_*backup*" | Where-Object { $_.CreationTime -lt $cutoffDate }
    
    foreach ($backup in $oldBackups) {
        Remove-Item $backup.FullName -Force
        Write-Host "Deleted old backup: $($backup.Name)" -ForegroundColor Gray
    }
    
    if ($oldBackups.Count -eq 0) {
        Write-Host "No old backups to clean up" -ForegroundColor Gray
    }
    else {
        Write-Host "Cleaned up $($oldBackups.Count) old backup(s)" -ForegroundColor Green
    }
}

# Main backup process
Write-Host "Starting PROJECT SENTINEL database backup..." -ForegroundColor Cyan
Write-Host "Backup Type: $BackupType" -ForegroundColor Gray
Write-Host "Timestamp: $Timestamp" -ForegroundColor Gray

# Check if PostgreSQL container is running
if (-not (Test-ContainerRunning -ContainerName $ContainerName)) {
    Write-Host "ERROR: PostgreSQL container '$ContainerName' is not running" -ForegroundColor Red
    Write-Host "Start PostgreSQL with: .\start-postgresql.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "PostgreSQL container is running" -ForegroundColor Green

# Perform backup based on type
$BackupFile = $null

switch ($BackupType.ToLower()) {
    "full" { $BackupFile = Backup-Full }
    "data" { $BackupFile = Backup-DataOnly }
    "schema" { $BackupFile = Backup-SchemaOnly }
    "all" {
        $BackupFile = Backup-Full
        Backup-DataOnly | Out-Null
        Backup-SchemaOnly | Out-Null
    }
    default {
        Write-Host "Invalid backup type: $BackupType" -ForegroundColor Red
        Write-Host "Valid types: full, data, schema, all" -ForegroundColor Yellow
        exit 1
    }
}

if ($BackupFile) {
    # Compress if requested
    if ($Compress) {
        $BackupFile = Compress-Backup -FilePath $BackupFile
    }
    
    # Get database statistics
    Get-DatabaseStats
    
    # Cleanup old backups
    Cleanup-OldBackups -RetentionDays 7
    
    # Show backup summary
    Write-Host ""
    Write-Host "=================================" -ForegroundColor Green
    Write-Host "Backup Completed Successfully!" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    Write-Host "Backup File: $BackupFile" -ForegroundColor White
    Write-Host "Database: $DatabaseName" -ForegroundColor White
    Write-Host "Timestamp: $Timestamp" -ForegroundColor White
    
    if (Test-Path $BackupFile) {
        $fileSize = (Get-Item $BackupFile).Length / 1MB
        Write-Host "File Size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "Restore Command:" -ForegroundColor Yellow
    if ($BackupFile.EndsWith('.gz') -or $BackupFile.EndsWith('.zip')) {
        Write-Host "  1. Extract: gunzip $BackupFile (or unzip)" -ForegroundColor Gray
        Write-Host "  2. Restore: docker exec -i $ContainerName psql -U $Username -d $DatabaseName < extracted_file.sql" -ForegroundColor Gray
    }
    else {
        Write-Host "  docker exec -i $ContainerName psql -U $Username -d $DatabaseName < $BackupFile" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "PROJECT SENTINEL backup complete!" -ForegroundColor Green
}
else {
    Write-Host "Backup failed!" -ForegroundColor Red
    exit 1
}
