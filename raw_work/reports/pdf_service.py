#!/usr/bin/env python3
"""
PROJECT SENTINEL - PDF REPORT SERVICE
Cameroon Defense Force OSINT Analysis System
FastAPI service for generating intelligence reports
"""

import os
import sys
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import logging
import asyncio
import json
import requests
import uvicorn

# Import our PDF generator
from pdf_generator import pdf_generator, ReportConfig, ThreatData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="PROJECT SENTINEL - PDF Report Service",
    description="Professional intelligence report generation for Cameroon Defense Forces",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class ReportRequest(BaseModel):
    """Request model for report generation"""
    report_type: str = Field(default="intelligence_assessment", 
                            description="Type of report: intelligence_assessment, executive_summary, detailed_analysis")
    time_period: str = Field(default="24_hours", 
                            description="Time period: 24_hours, 7_days, 30_days")
    regions: Optional[List[str]] = Field(default=None, 
                                       description="Specific regions to include (None for all)")
    include_charts: bool = Field(default=True, description="Include visualizations")
    include_executive_summary: bool = Field(default=True, description="Include executive summary")
    include_maps: bool = Field(default=False, description="Include geographical maps")
    classification: str = Field(default="CONFIDENTIAL", description="Security classification")
    author: str = Field(default="PROJECT SENTINEL", description="Report author")
    custom_title: Optional[str] = Field(default=None, description="Custom report title")

class ReportResponse(BaseModel):
    """Response model for report generation"""
    success: bool
    report_id: str
    filename: str
    file_path: str
    file_size: int
    generation_time: float
    pages: int
    timestamp: str

class ReportStatus(BaseModel):
    """Report generation status"""
    report_id: str
    status: str  # "generating", "completed", "failed"
    progress: int  # 0-100
    message: str
    created_at: str
    completed_at: Optional[str] = None

class SystemMetrics(BaseModel):
    """System metrics for reports"""
    total_reports_generated: int
    reports_today: int
    average_generation_time: float
    most_requested_type: str
    disk_usage_mb: float

# Global state
report_queue = {}
report_history = []

@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint with service information"""
    return {
        "service": "PROJECT SENTINEL - PDF Report Service",
        "status": "operational",
        "version": "1.0.0",
        "organization": "Cameroon Defense Forces",
        "endpoints": {
            "generate_report": "/api/generate-report",
            "download_report": "/api/download/{report_id}",
            "report_status": "/api/status/{report_id}",
            "list_reports": "/api/reports",
            "sample_report": "/api/sample-report"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "PROJECT SENTINEL - PDF Report Service",
        "timestamp": datetime.now().isoformat(),
        "pdf_generator": "operational",
        "reports_directory": str(pdf_generator.reports_dir),
        "disk_space_mb": get_disk_usage()
    }

def get_disk_usage() -> float:
    """Get disk usage for reports directory"""
    try:
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(pdf_generator.reports_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return round(total_size / (1024 * 1024), 2)  # MB
    except Exception:
        return 0.0

async def fetch_threat_data(regions: Optional[List[str]] = None, 
                           time_period: str = "24_hours") -> List[ThreatData]:
    """Fetch threat intelligence data from the main system"""
    try:
        # Try to get real data from the backend API
        response = requests.get("http://localhost:8000/api/statistics/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Convert API data to ThreatData format
            threat_data = []
            
            # Sample conversion - would be adapted based on actual API structure
            default_regions = ["Extreme-Nord", "Nord-Ouest", "Sud-Ouest", "Centre", "Littoral", 
                             "Est", "Adamaoua", "Nord", "Ouest", "Sud"]
            
            selected_regions = regions if regions else default_regions
            
            for region in selected_regions:
                # This would be replaced with actual data parsing
                threat_data.append(ThreatData(
                    region=region,
                    threat_level=determine_threat_level(region),
                    risk_score=calculate_risk_score(region),
                    article_count=get_article_count(region, data),
                    key_actors=get_key_actors(region),
                    incident_types=get_incident_types(region),
                    sentiment_score=get_sentiment_score(region),
                    escalation_probability=get_escalation_probability(region)
                ))
            
            return threat_data
            
    except Exception as e:
        logger.warning(f"Could not fetch real data, using sample data: {e}")
    
    # Fallback to sample data if API is not available
    return generate_sample_threat_data(regions)

def determine_threat_level(region: str) -> str:
    """Determine threat level based on region"""
    high_risk = ["Extreme-Nord", "Nord-Ouest", "Sud-Ouest"]
    if region in high_risk:
        return "HIGH"
    elif region in ["Nord", "Est"]:
        return "MEDIUM"
    else:
        return "LOW"

def calculate_risk_score(region: str) -> float:
    """Calculate risk score for region"""
    risk_map = {
        "Extreme-Nord": 85.3,
        "Nord-Ouest": 72.4,
        "Sud-Ouest": 68.1,
        "Nord": 55.2,
        "Est": 48.7,
        "Centre": 32.4,
        "Littoral": 28.9,
        "Ouest": 35.6,
        "Adamaoua": 41.2,
        "Sud": 25.8
    }
    return risk_map.get(region, 40.0)

def get_article_count(region: str, api_data: Dict) -> int:
    """Get article count for region"""
    # Would parse from real API data
    import random
    return random.randint(3, 25)

def get_key_actors(region: str) -> List[str]:
    """Get key actors for region"""
    actors_map = {
        "Extreme-Nord": ["Boko Haram", "BIR Forces", "ISWAP", "Local Militias"],
        "Nord-Ouest": ["Ambazonia Defense Forces", "Government Forces", "Civil Society"],
        "Sud-Ouest": ["Separatist Groups", "Military Units", "Civilian Leadership"],
        "Centre": ["Political Parties", "Government Officials", "Civil Society"],
        "Littoral": ["Business Community", "Port Authorities", "Trade Unions"]
    }
    return actors_map.get(region, ["Local Authorities", "Civil Society"])

def get_incident_types(region: str) -> List[str]:
    """Get incident types for region"""
    incidents_map = {
        "Extreme-Nord": ["Terrorism", "Cross-border Activity", "Military Operations"],
        "Nord-Ouest": ["Separatist Activity", "Armed Conflict", "Political Violence"],
        "Sud-Ouest": ["Armed Conflict", "Civilian Displacement", "Security Operations"],
        "Centre": ["Political Activity", "Economic Issues", "Social Movements"],
        "Littoral": ["Economic Activity", "Maritime Security", "Trade Issues"]
    }
    return incidents_map.get(region, ["General Security", "Economic Activity"])

def get_sentiment_score(region: str) -> float:
    """Get sentiment score for region"""
    sentiment_map = {
        "Extreme-Nord": -0.65,
        "Nord-Ouest": -0.42,
        "Sud-Ouest": -0.38,
        "Centre": 0.15,
        "Littoral": 0.25
    }
    return sentiment_map.get(region, 0.0)

def get_escalation_probability(region: str) -> float:
    """Get escalation probability for region"""
    escalation_map = {
        "Extreme-Nord": 0.78,
        "Nord-Ouest": 0.55,
        "Sud-Ouest": 0.48,
        "Centre": 0.22,
        "Littoral": 0.18
    }
    return escalation_map.get(region, 0.3)

def generate_sample_threat_data(regions: Optional[List[str]] = None) -> List[ThreatData]:
    """Generate sample threat data for demonstration"""
    default_regions = ["Extreme-Nord", "Nord-Ouest", "Sud-Ouest", "Centre", "Littoral"]
    selected_regions = regions if regions else default_regions
    
    threat_data = []
    for region in selected_regions:
        threat_data.append(ThreatData(
            region=region,
            threat_level=determine_threat_level(region),
            risk_score=calculate_risk_score(region),
            article_count=get_article_count(region, {}),
            key_actors=get_key_actors(region),
            incident_types=get_incident_types(region),
            sentiment_score=get_sentiment_score(region),
            escalation_probability=get_escalation_probability(region)
        ))
    
    return threat_data

async def generate_report_background(report_request: ReportRequest, report_id: str):
    """Background task to generate report"""
    try:
        # Update status
        report_queue[report_id].status = "generating"
        report_queue[report_id].progress = 10
        report_queue[report_id].message = "Fetching threat intelligence data..."
        
        # Fetch threat data
        threat_data = await fetch_threat_data(report_request.regions, report_request.time_period)
        
        report_queue[report_id].progress = 30
        report_queue[report_id].message = "Processing regional assessments..."
        
        # Create report configuration
        config = ReportConfig(
            title=report_request.custom_title or "PROJECT SENTINEL Intelligence Assessment",
            classification=report_request.classification,
            report_type=report_request.report_type.upper(),
            author=report_request.author,
            organization="Cameroon Defense Forces - Intelligence Division",
            time_period=report_request.time_period.replace("_", " ").title(),
            include_charts=report_request.include_charts,
            include_maps=report_request.include_maps,
            include_executive_summary=report_request.include_executive_summary
        )
        
        report_queue[report_id].progress = 50
        report_queue[report_id].message = "Generating charts and visualizations..."
        
        # Give time for chart generation
        await asyncio.sleep(2)
        
        report_queue[report_id].progress = 70
        report_queue[report_id].message = "Compiling PDF document..."
        
        # Generate report
        start_time = datetime.now()
        output_path = pdf_generator.generate_intelligence_report(threat_data, config)
        end_time = datetime.now()
        
        # Get file info
        file_path = Path(output_path)
        file_size = file_path.stat().st_size if file_path.exists() else 0
        generation_time = (end_time - start_time).total_seconds()
        
        # Update status
        report_queue[report_id].status = "completed"
        report_queue[report_id].progress = 100
        report_queue[report_id].message = "Report generated successfully"
        report_queue[report_id].completed_at = datetime.now().isoformat()
        
        # Add to history
        report_history.append({
            "report_id": report_id,
            "filename": file_path.name,
            "file_path": str(file_path),
            "file_size": file_size,
            "generation_time": generation_time,
            "timestamp": datetime.now().isoformat(),
            "request": report_request.dict()
        })
        
        logger.info(f"Report {report_id} generated successfully: {output_path}")
        
    except Exception as e:
        logger.error(f"Error generating report {report_id}: {e}")
        report_queue[report_id].status = "failed"
        report_queue[report_id].message = f"Generation failed: {str(e)}"
        import traceback
        logger.error(traceback.format_exc())

@app.post("/api/generate-report", response_model=Dict[str, Any])
async def generate_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """Generate intelligence report"""
    
    # Create report ID
    report_id = f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(report_history)+1:03d}"
    
    # Initialize status tracking
    report_queue[report_id] = ReportStatus(
        report_id=report_id,
        status="queued",
        progress=0,
        message="Report queued for generation",
        created_at=datetime.now().isoformat()
    )
    
    # Start background generation
    background_tasks.add_task(generate_report_background, request, report_id)
    
    return {
        "success": True,
        "report_id": report_id,
        "status": "queued",
        "message": "Report generation started",
        "estimated_time": "2-5 minutes",
        "status_endpoint": f"/api/status/{report_id}",
        "download_endpoint": f"/api/download/{report_id}"
    }

@app.get("/api/status/{report_id}")
async def get_report_status(report_id: str):
    """Get report generation status"""
    
    if report_id not in report_queue:
        raise HTTPException(status_code=404, detail="Report not found")
    
    status = report_queue[report_id]
    return status.dict()

@app.get("/api/download/{report_id}")
async def download_report(report_id: str):
    """Download generated report"""
    
    # Check if report exists in history
    report_info = None
    for report in report_history:
        if report["report_id"] == report_id:
            report_info = report
            break
    
    if not report_info:
        raise HTTPException(status_code=404, detail="Report not found")
    
    file_path = Path(report_info["file_path"])
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(
        path=str(file_path),
        media_type='application/pdf',
        filename=report_info["filename"]
    )

@app.get("/api/reports")
async def list_reports(limit: int = Query(20, ge=1, le=100)):
    """List generated reports"""
    
    recent_reports = sorted(
        report_history, 
        key=lambda x: x["timestamp"], 
        reverse=True
    )[:limit]
    
    return {
        "reports": recent_reports,
        "total_count": len(report_history),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/sample-report")
async def generate_sample_report():
    """Generate sample intelligence report"""
    
    try:
        output_path = pdf_generator.generate_sample_report()
        file_path = Path(output_path)
        
        return FileResponse(
            path=str(file_path),
            media_type='application/pdf',
            filename=file_path.name
        )
        
    except Exception as e:
        logger.error(f"Error generating sample report: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.get("/api/metrics", response_model=SystemMetrics)
async def get_system_metrics():
    """Get system metrics"""
    
    today = datetime.now().date()
    reports_today = len([
        r for r in report_history 
        if datetime.fromisoformat(r["timestamp"]).date() == today
    ])
    
    if report_history:
        avg_time = sum(r["generation_time"] for r in report_history) / len(report_history)
        
        # Find most requested report type
        type_counts = {}
        for report in report_history:
            report_type = report["request"]["report_type"]
            type_counts[report_type] = type_counts.get(report_type, 0) + 1
        most_requested = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else "intelligence_assessment"
    else:
        avg_time = 0.0
        most_requested = "intelligence_assessment"
    
    return SystemMetrics(
        total_reports_generated=len(report_history),
        reports_today=reports_today,
        average_generation_time=round(avg_time, 2),
        most_requested_type=most_requested,
        disk_usage_mb=get_disk_usage()
    )

@app.delete("/api/cleanup")
async def cleanup_old_reports(days_old: int = Query(30, ge=1, le=365)):
    """Clean up old report files"""
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    deleted_count = 0
    
    try:
        for report in report_history[:]:  # Copy list to avoid modification during iteration
            report_date = datetime.fromisoformat(report["timestamp"])
            
            if report_date < cutoff_date:
                file_path = Path(report["file_path"])
                if file_path.exists():
                    file_path.unlink()
                    deleted_count += 1
                
                report_history.remove(report)
        
        return {
            "success": True,
            "deleted_files": deleted_count,
            "cutoff_date": cutoff_date.isoformat(),
            "remaining_reports": len(report_history)
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting PROJECT SENTINEL PDF Report Service...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8007,
        log_level="info"
    )
