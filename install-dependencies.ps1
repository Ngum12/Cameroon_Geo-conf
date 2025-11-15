#!/usr/bin/env pwsh
<#
PROJECT SENTINEL - DEPENDENCY INSTALLER
Installs all required Python packages for all services
#>

Write-Host "📦 PROJECT SENTINEL - INSTALLING ALL DEPENDENCIES" -ForegroundColor Green
Write-Host "═════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

function Install-PythonDependencies {
    param(
        [string]$ServiceName,
        [string]$Directory,
        [string]$RequirementsFile = "requirements.txt"
    )
    
    Write-Host "🔧 Installing $ServiceName dependencies..." -ForegroundColor Cyan
    Write-Host "   📁 Directory: $Directory" -ForegroundColor White
    
    if (Test-Path "$Directory\$RequirementsFile") {
        try {
            Push-Location $Directory
            pip install -r $RequirementsFile
            Write-Host "   ✅ $ServiceName dependencies installed!" -ForegroundColor Green
            Pop-Location
        } catch {
            Write-Host "   ❌ Failed to install $ServiceName dependencies: $($_.Exception.Message)" -ForegroundColor Red
            Pop-Location
        }
    } else {
        Write-Host "   ⚠️ No $RequirementsFile found for $ServiceName" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Install core Django dependencies (minimal)
Write-Host "1️⃣ DJANGO CORE DEPENDENCIES" -ForegroundColor Magenta
pip install Django djangorestframework django-cors-headers python-decouple uvicorn fastapi
Write-Host ""

# Install service-specific dependencies
Install-PythonDependencies -ServiceName "ML Prediction Models" -Directory "ml-models"
Install-PythonDependencies -ServiceName "RL Intervention System" -Directory "rl-system"
Install-PythonDependencies -ServiceName "Human Interface API" -Directory "human-in-loop"
Install-PythonDependencies -ServiceName "NLP Services" -Directory "nlp-models"

# Install Node.js dependencies for frontend
Write-Host "7️⃣ FRONTEND DEPENDENCIES" -ForegroundColor Magenta
if (Test-Path "frontend-dashboard\package.json") {
    try {
        Push-Location "frontend-dashboard"
        npm install
        Write-Host "   ✅ Frontend dependencies installed!" -ForegroundColor Green
        Pop-Location
    } catch {
        Write-Host "   ❌ Failed to install frontend dependencies: $($_.Exception.Message)" -ForegroundColor Red
        Pop-Location
    }
} else {
    Write-Host "   ⚠️ No package.json found for frontend" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 ALL DEPENDENCIES INSTALLED!" -ForegroundColor Green
Write-Host "🚀 Ready to run: .\start-all-services.ps1" -ForegroundColor Yellow

