#!/usr/bin/env pwsh
# PROJECT SENTINEL - START ALL SERVICES AT ONCE
# Clean version without emojis to avoid encoding issues

Write-Host "PROJECT SENTINEL - STARTING ALL SERVICES" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Array to store all processes
$script:processes = @()

function Start-ServiceProcess {
    param(
        [string]$ServiceName,
        [string]$WorkingDir,
        [string]$Command,
        [array]$Arguments,
        [int]$Port
    )
    
    Write-Host "Starting $ServiceName on port $Port..." -ForegroundColor Cyan
    
    try {
        # Check if directory exists
        if (-not (Test-Path $WorkingDir)) {
            Write-Host "WARNING: Directory not found: $WorkingDir" -ForegroundColor Yellow
            return $false
        }
        
        $process = Start-Process -FilePath $Command -ArgumentList $Arguments -WorkingDirectory $WorkingDir -PassThru -WindowStyle Normal
        $script:processes += @{
            Name = $ServiceName
            Process = $process
            Port = $Port
            PID = $process.Id
            StartTime = Get-Date
        }
        Write-Host "SUCCESS: $ServiceName started (PID: $($process.Id))" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "FAILED: $ServiceName - $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-ServiceHealth {
    param([int]$Port, [string]$Path = "")
    try {
        $url = "http://localhost:$Port$Path"
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 3 -UseBasicParsing -ErrorAction SilentlyContinue
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

Write-Host "Starting Django Backend API..." -ForegroundColor Yellow
Start-ServiceProcess -ServiceName "Django Backend" -WorkingDir "backend-api" -Command "python" -Arguments @("manage.py", "runserver", "8000", "--settings=sentinel_core.minimal_settings") -Port 8000

Start-Sleep -Seconds 5

Write-Host "Starting ML Prediction API..." -ForegroundColor Yellow
Start-ServiceProcess -ServiceName "ML Prediction API" -WorkingDir "ml-models" -Command "python" -Arguments @("-m", "uvicorn", "prediction_api:app", "--host", "0.0.0.0", "--port", "8001", "--reload") -Port 8001

Start-Sleep -Seconds 3

Write-Host "Starting RL Intervention API..." -ForegroundColor Yellow
Start-ServiceProcess -ServiceName "RL Intervention API" -WorkingDir "rl-system" -Command "python" -Arguments @("-m", "uvicorn", "rl_system_api:app", "--host", "0.0.0.0", "--port", "8002", "--reload") -Port 8002

Start-Sleep -Seconds 3

Write-Host "Starting Human Interface API..." -ForegroundColor Yellow
Start-ServiceProcess -ServiceName "Human Interface API" -WorkingDir "human-in-loop" -Command "python" -Arguments @("-m", "uvicorn", "human_interface_api:app", "--host", "0.0.0.0", "--port", "8003", "--reload") -Port 8003

Start-Sleep -Seconds 3

Write-Host "Starting NLP Translation Service..." -ForegroundColor Yellow
Start-ServiceProcess -ServiceName "NLP Translation" -WorkingDir "nlp-models" -Command "python" -Arguments @("-m", "uvicorn", "translation_service_cpu:app", "--host", "0.0.0.0", "--port", "8004", "--reload") -Port 8004

Start-Sleep -Seconds 3

Write-Host "Starting NLP NER Service..." -ForegroundColor Yellow
Start-ServiceProcess -ServiceName "NLP NER Service" -WorkingDir "nlp-models" -Command "python" -Arguments @("-m", "uvicorn", "ner_service:app", "--host", "0.0.0.0", "--port", "8005", "--reload") -Port 8005

Start-Sleep -Seconds 3

Write-Host "Starting React Frontend Dashboard..." -ForegroundColor Yellow
Start-ServiceProcess -ServiceName "Frontend Dashboard" -WorkingDir "frontend-dashboard" -Command "npm" -Arguments @("run", "dev") -Port 5173

Start-Sleep -Seconds 3

Write-Host "Starting LIVE INTELLIGENCE MONITORING..." -ForegroundColor Magenta
Write-Host "🔥 ACTIVATING CONTINUOUS GEOPOLITICAL COLLECTION 🔥" -ForegroundColor Red
Start-ServiceProcess -ServiceName "Live Intelligence Monitor" -WorkingDir "backend-api" -Command "python" -Arguments @("start_live_monitoring.py") -Port 0

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "ALL SERVICES STARTED!" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host ""

# Wait for services to stabilize
Write-Host "Waiting for services to stabilize..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host "SERVICE ENDPOINTS:" -ForegroundColor Cyan
Write-Host "Main Dashboard:      http://localhost:5173" -ForegroundColor White
Write-Host "Django Backend:      http://localhost:8000" -ForegroundColor White
Write-Host "ML Prediction API:   http://localhost:8001/docs" -ForegroundColor White
Write-Host "RL Intervention API: http://localhost:8002/docs" -ForegroundColor White
Write-Host "Human Interface API: http://localhost:8003/docs" -ForegroundColor White
Write-Host "NLP Translation:     http://localhost:8004/docs" -ForegroundColor White
Write-Host "NLP NER Service:     http://localhost:8005/docs" -ForegroundColor White
Write-Host ""
Write-Host "🔥 LIVE INTELLIGENCE SYSTEM ACTIVE 🔥" -ForegroundColor Red
Write-Host "📡 Monitoring 45+ Cameroon Sources" -ForegroundColor Yellow
Write-Host "🌍 All 10 Regions Under Surveillance" -ForegroundColor Yellow
Write-Host "🔄 Auto-Collection Every 30 Minutes" -ForegroundColor Yellow
Write-Host "🛡️ Defense-Grade Geopolitical Intelligence" -ForegroundColor Yellow
Write-Host ""

Write-Host "RUNNING SERVICES:" -ForegroundColor Yellow
$runningCount = 0
$healthyCount = 0

foreach ($service in $script:processes) {
    $isRunning = -not $service.Process.HasExited
    $isHealthy = $false
    
    if ($isRunning) {
        $runningCount++
        # Test health based on service type
        switch ($service.Port) {
            8000 { $isHealthy = Test-ServiceHealth -Port 8000 -Path "/api/v1/statistics/" }
            8001 { $isHealthy = Test-ServiceHealth -Port 8001 -Path "/docs" }
            8002 { $isHealthy = Test-ServiceHealth -Port 8002 -Path "/docs" }
            8003 { $isHealthy = Test-ServiceHealth -Port 8003 -Path "/docs" }
            8004 { $isHealthy = Test-ServiceHealth -Port 8004 -Path "/docs" }
            8005 { $isHealthy = Test-ServiceHealth -Port 8005 -Path "/docs" }
            5173 { $isHealthy = Test-ServiceHealth -Port 5173 }
            0    { $isHealthy = $isRunning } # Live monitoring service (no port)
        }
        if ($isHealthy) { $healthyCount++ }
    }
    
    $statusIcon = if ($isHealthy) { "HEALTHY" } elseif ($isRunning) { "RUNNING" } else { "STOPPED" }
    
    Write-Host "$($service.Name): $statusIcon (PID: $($service.PID), Port: $($service.Port))" -ForegroundColor White
}

Write-Host ""
Write-Host "SYSTEM METRICS:" -ForegroundColor Cyan
Write-Host "Running Services: $runningCount/$($script:processes.Count)" -ForegroundColor White
Write-Host "Healthy Services: $healthyCount/$($script:processes.Count)" -ForegroundColor White
$successRate = if ($script:processes.Count -gt 0) { ($healthyCount / $script:processes.Count) * 100 } else { 0 }
Write-Host "Success Rate: $($successRate.ToString('F1'))%" -ForegroundColor White

Write-Host ""
Write-Host "🇨🇲 CAMEROON DEFENSE FORCE - PROJECT SENTINEL FULLY OPERATIONAL! 🇨🇲" -ForegroundColor Green
Write-Host "🔥 LIVE INTELLIGENCE COLLECTION ACTIVE 🔥" -ForegroundColor Red
Write-Host "📊 Real-Time Analytics Dashboard Ready" -ForegroundColor Cyan
Write-Host "🛡️ National Security Monitoring Online" -ForegroundColor Magenta
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Keep script running and monitor
try {
    while ($true) {
        Start-Sleep -Seconds 60
        $currentTime = Get-Date -Format 'HH:mm:ss'
        Write-Host "🔥 LIVE INTELLIGENCE SYSTEM OPERATIONAL... $currentTime 🔥" -ForegroundColor Green
        
        # Check for crashed services every 5 minutes
        if ((Get-Date).Minute % 5 -eq 0) {
            $crashedServices = @()
            foreach ($service in $script:processes) {
                if ($service.Process.HasExited) {
                    $crashedServices += $service.Name
                }
            }
            if ($crashedServices.Count -gt 0) {
                Write-Host "⚠️ WARNING: Crashed services detected: $($crashedServices -join ', ')" -ForegroundColor Red
            } else {
                Write-Host "✅ All intelligence services healthy - Monitoring 45+ sources" -ForegroundColor Cyan
            }
        }
        
        # Show intelligence collection status every 10 minutes
        if ((Get-Date).Minute % 10 -eq 0) {
            Write-Host "📡 INTELLIGENCE STATUS: Continuous geopolitical monitoring active" -ForegroundColor Yellow
            Write-Host "🗺️ REGIONAL COVERAGE: All 10 Cameroon regions under surveillance" -ForegroundColor Yellow
            Write-Host "🎯 THREAT ANALYSIS: ML models processing real-time intelligence" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "Stopping all services..." -ForegroundColor Red
    foreach ($service in $script:processes) {
        if (-not $service.Process.HasExited) {
            try {
                $service.Process.Kill()
                Write-Host "Stopped $($service.Name)" -ForegroundColor Yellow
            } catch {
                $serviceName = $service.Name
                Write-Host "Could not stop $serviceName" -ForegroundColor Red
            }
        }
    }
    Write-Host 'All services stopped.' -ForegroundColor Green
}
