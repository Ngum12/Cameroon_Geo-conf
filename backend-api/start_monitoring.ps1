#!/usr/bin/env pwsh
Write-Host "🚀 HARMONY FLOW PLATFORM - CONTINUOUS NEWS MONITORING" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Gray
Write-Host "📡 Monitoring Cameroon news sources every 30 minutes" -ForegroundColor Green
Write-Host "📰 Sources: Cameroon Tribune, Journal du Cameroun, Business in Cameroon" -ForegroundColor Yellow
Write-Host "🔄 Numbers will update automatically as new articles are published" -ForegroundColor Magenta
Write-Host "🛑 Press Ctrl+C to stop monitoring" -ForegroundColor Red
Write-Host "====================================================" -ForegroundColor Gray
Write-Host ""

try {
    python continuous_news_monitor.py
} catch {
    Write-Host "❌ Error starting monitor: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
