# 🎬 DOWNLOAD PIXABAY MILITARY VIDEO FOR AUTHENTICATION BACKGROUND
# This script downloads the military/spy video from Pixabay

Write-Host "🎬 DOWNLOADING MILITARY BACKGROUND VIDEO..." -ForegroundColor Cyan
Write-Host "📹 Source: Pixabay Video ID 142363 (Spy/CIA/FBI/MI6/Military)" -ForegroundColor Yellow

# Create videos directory if it doesn't exist
$videosDir = "public/videos"
if (-not (Test-Path $videosDir)) {
    New-Item -ItemType Directory -Path $videosDir -Force
    Write-Host "📁 Created videos directory: $videosDir" -ForegroundColor Green
}

# Pixabay video download URLs (try multiple sources)
$videoUrls = @(
    "https://cdn.pixabay.com/vimeo/142363/spy-cia-fbi-mi6-military-travel-142363.mp4",
    "https://player.vimeo.com/external/142363.hd.mp4?s=c8f8c8f8c8f8c8f8c8f8c8f8c8f8c8f8c8f8c8f8&profile_id=174"
)

$outputFile = "$videosDir/spy-military-pixabay.mp4"

Write-Host "🔄 Attempting to download military video..." -ForegroundColor Yellow

foreach ($url in $videoUrls) {
    try {
        Write-Host "📥 Trying URL: $url" -ForegroundColor Gray
        
        # Use Invoke-WebRequest to download
        Invoke-WebRequest -Uri $url -OutFile $outputFile -UserAgent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        if (Test-Path $outputFile) {
            $fileSize = (Get-Item $outputFile).Length / 1MB
            Write-Host "✅ SUCCESS! Downloaded military video: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
            Write-Host "📍 Saved to: $outputFile" -ForegroundColor Green
            break
        }
    }
    catch {
        Write-Host "❌ Failed to download from: $url" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        continue
    }
}

# If download failed, provide instructions
if (-not (Test-Path $outputFile)) {
    Write-Host "" -ForegroundColor Yellow
    Write-Host "⚠️  MANUAL DOWNLOAD REQUIRED" -ForegroundColor Yellow
    Write-Host "🌐 Please manually download the video from:" -ForegroundColor White
    Write-Host "   https://pixabay.com/videos/spy-cia-fbi-mi6-military-travel-142363/" -ForegroundColor Cyan
    Write-Host "" -ForegroundColor White
    Write-Host "📋 INSTRUCTIONS:" -ForegroundColor White
    Write-Host "   1. Visit the Pixabay link above" -ForegroundColor Gray
    Write-Host "   2. Click 'Free Download'" -ForegroundColor Gray
    Write-Host "   3. Select 'Large MP4' or 'Medium MP4'" -ForegroundColor Gray
    Write-Host "   4. Save the file as: $outputFile" -ForegroundColor Gray
    Write-Host "" -ForegroundColor White
    Write-Host "🎯 Alternative: Use any military/defense themed MP4 video" -ForegroundColor White
    Write-Host "   - Resolution: 1920x1080 or 1280x720" -ForegroundColor Gray
    Write-Host "   - Duration: 30-60 seconds (will loop)" -ForegroundColor Gray
    Write-Host "   - Size: Under 50MB recommended" -ForegroundColor Gray
} else {
    Write-Host "" -ForegroundColor Green
    Write-Host "🎉 READY TO USE!" -ForegroundColor Green
    Write-Host "🚀 Start your Project Sentinel system and enjoy the cinematic login!" -ForegroundColor Cyan
}

Write-Host "" -ForegroundColor White
Write-Host "🛡️ PROJECT SENTINEL - DEFENSE AUTHENTICATION SYSTEM" -ForegroundColor Green
