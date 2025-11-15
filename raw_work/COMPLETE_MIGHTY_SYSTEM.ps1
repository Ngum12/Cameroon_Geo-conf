#!/usr/bin/env pwsh
# PROJECT SENTINEL - COMPLETE MIGHTY SYSTEM LAUNCHER
# Restored from your original start-all-clean.ps1 with enhancements

Write-Host "🛡️ PROJECT SENTINEL - COMPLETE MIGHTY SYSTEM" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host "🎯 CAMEROON DEFENSE FORCE - HARMONY FLOW PLATFORM" -ForegroundColor Cyan
Write-Host "📡 ALL 7 ORIGINAL SERVICES + ENHANCEMENTS" -ForegroundColor Yellow
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
    
    Write-Host "🔧 Starting $ServiceName on port $Port..." -ForegroundColor Cyan
    
    try {
        if (-not (Test-Path $WorkingDir)) {
            Write-Host "❌ Directory not found: $WorkingDir" -ForegroundColor Red
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
        Write-Host "✅ SUCCESS: $ServiceName started (PID: $($process.Id))" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ FAILED: $ServiceName - $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-ServiceHealth {
    param([int]$Port, [string]$Path = "")
    
    try {
        $url = "http://localhost:$Port$Path"
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 3 -UseBasicParsing
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Show-SystemStatus {
    $runningCount = 0
    $healthyCount = 0
    
    Write-Host ""
    Write-Host "📊 COMPLETE SYSTEM STATUS:" -ForegroundColor Yellow
    Write-Host "=========================" -ForegroundColor Yellow
    
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
            }
            if ($isHealthy) { $healthyCount++ }
        }
        
        $statusIcon = if ($isHealthy) { "🟢" } elseif ($isRunning) { "🟡" } else { "🔴" }
        $statusText = if ($isHealthy) { "HEALTHY" } elseif ($isRunning) { "RUNNING" } else { "STOPPED" }
        
        Write-Host "   $statusIcon $($service.Name): $statusText (PID: $($service.PID), Port: $($service.Port))" -ForegroundColor White
    }
    
    $successRate = if ($script:processes.Count -gt 0) { ($healthyCount / $script:processes.Count) * 100 } else { 0 }
    
    Write-Host ""
    Write-Host "📈 SYSTEM METRICS:" -ForegroundColor Cyan
    Write-Host "   🔧 Running Services: $runningCount/$($script:processes.Count)" -ForegroundColor White
    Write-Host "   💚 Healthy Services: $healthyCount/$($script:processes.Count)" -ForegroundColor White
    Write-Host "   📊 Success Rate: $($successRate.ToString('F1'))%" -ForegroundColor White
    
    if ($successRate -ge 80) {
        Write-Host "🚀 SYSTEM STATUS: FULLY OPERATIONAL" -ForegroundColor Green
    } elseif ($successRate -ge 60) {
        Write-Host "⚠️ SYSTEM STATUS: PARTIALLY OPERATIONAL" -ForegroundColor Yellow
    } else {
        Write-Host "🔴 SYSTEM STATUS: DEGRADED" -ForegroundColor Red
    }
}

# Start all services in order
Write-Host "🚀 STARTING ALL 7 SERVICES..." -ForegroundColor Yellow
Write-Host ""

Write-Host "1️⃣ Starting Django Backend API..." -ForegroundColor Yellow
Start-ServiceProcess -ServiceName "Django Backend" -WorkingDir "backend-api" -Command "python" -Arguments @("manage.py", "runserver", "8000", "--settings=sentinel_core.minimal_settings") -Port 8000
Start-Sleep -Seconds 5

Write-Host "2️⃣ Starting ML Prediction API..." -ForegroundColor Yellow
Start-ServiceProcess -ServiceName "ML Prediction API" -WorkingDir "ml-models" -Command "python" -Arguments @("-m", "uvicorn", "prediction_api:app", "--host", "0.0.0.0", "--port", "8001", "--reload") -Port 8001
Start-Sleep -Seconds 3

Write-Host "3️⃣ Starting RL Intervention API..." -ForegroundColor Yellow
Start-ServiceProcess -ServiceName "RL Intervention API" -WorkingDir "rl-system" -Command "python" -Arguments @("-m", "uvicorn", "rl_system_api:app", "--host", "0.0.0.0", "--port", "8002", "--reload") -Port 8002
Start-Sleep -Seconds 3

Write-Host "4️⃣ Starting Human Interface API..." -ForegroundColor Yellow
Start-ServiceProcess -ServiceName "Human Interface API" -WorkingDir "human-in-loop" -Command "python" -Arguments @("-m", "uvicorn", "human_interface_api:app", "--host", "0.0.0.0", "--port", "8003", "--reload") -Port 8003
Start-Sleep -Seconds 3

Write-Host "5️⃣ Starting NLP Translation Service..." -ForegroundColor Yellow
Start-ServiceProcess -ServiceName "NLP Translation" -WorkingDir "nlp-models" -Command "python" -Arguments @("-m", "uvicorn", "translation_service_cpu:app", "--host", "0.0.0.0", "--port", "8004", "--reload") -Port 8004
Start-Sleep -Seconds 3

Write-Host "6️⃣ Starting NLP NER Service..." -ForegroundColor Yellow
Start-ServiceProcess -ServiceName "NLP NER Service" -WorkingDir "nlp-models" -Command "python" -Arguments @("-m", "uvicorn", "ner_service:app", "--host", "0.0.0.0", "--port", "8005", "--reload") -Port 8005
Start-Sleep -Seconds 3

Write-Host "7️⃣ Starting React Frontend Dashboard..." -ForegroundColor Yellow
Start-ServiceProcess -ServiceName "Frontend Dashboard" -WorkingDir "frontend-dashboard" -Command "npm" -Arguments @("run", "dev") -Port 5173

Write-Host ""
Write-Host "🎯 ALL SERVICES STARTUP COMPLETE!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Wait for services to stabilize
Write-Host "⏳ Allowing services to stabilize..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Show initial status
Show-SystemStatus

Write-Host ""
Write-Host "🌐 SERVICE ENDPOINTS:" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host "🎯 Main Dashboard:      http://localhost:5173" -ForegroundColor White
Write-Host "🔧 Django Backend:      http://localhost:8000" -ForegroundColor White
Write-Host "🤖 ML Prediction API:   http://localhost:8001/docs" -ForegroundColor White
Write-Host "🧠 RL Intervention API: http://localhost:8002/docs" -ForegroundColor White
Write-Host "👤 Human Interface API: http://localhost:8003/docs" -ForegroundColor White
Write-Host "🌍 NLP Translation:     http://localhost:8004/docs" -ForegroundColor White
Write-Host "🏷️ NLP NER Service:     http://localhost:8005/docs" -ForegroundColor White
Write-Host ""

Write-Host "🛡️ CAMEROON DEFENSE FORCE - PROJECT SENTINEL OPERATIONAL!" -ForegroundColor Green
Write-Host "🎯 HARMONY FLOW PLATFORM - COMPLETE MIGHTY SYSTEM ACTIVE!" -ForegroundColor Green
Write-Host "📊 Press Ctrl+C to stop all services gracefully" -ForegroundColor Yellow
Write-Host ""

# Enhanced monitoring loop
try {
    $lastStatusTime = Get-Date
    while ($true) {
        Start-Sleep -Seconds 30
        
        # Show periodic status updates
        $currentTime = Get-Date
        if (($currentTime - $lastStatusTime).TotalMinutes -ge 5) {
            Write-Host "🕐 System running... $($currentTime.ToString('HH:mm:ss'))" -ForegroundColor Green
            Show-SystemStatus
            $lastStatusTime = $currentTime
        }
        
        # Check for crashed services
        $crashedServices = @()
        foreach ($service in $script:processes) {
            if ($service.Process.HasExited) {
                $crashedServices += $service.Name
            }
        }
        
        if ($crashedServices.Count -gt 0) {
            Write-Host "⚠️ Detected crashed services: $($crashedServices -join ', ')" -ForegroundColor Red
        }
    }
} catch {
    Write-Host ""
    Write-Host "🛑 Stopping all services..." -ForegroundColor Red
    
    foreach ($service in $script:processes) {
        if (-not $service.Process.HasExited) {
            try {
                $service.Process.Kill()
                Write-Host "✅ Stopped $($service.Name)" -ForegroundColor Yellow
            } catch {
                Write-Host "❌ Could not stop $($service.Name)" -ForegroundColor Red
            }
        }
    }
    
    Write-Host ""
    Write-Host "🛡️ PROJECT SENTINEL - COMPLETE SHUTDOWN" -ForegroundColor Green
    Write-Host "🎯 CAMEROON DEFENSE FORCE - SYSTEM OFFLINE" -ForegroundColor Green
    Write-Host "📊 All services stopped." -ForegroundColor Green
}
