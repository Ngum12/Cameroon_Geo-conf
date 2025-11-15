"""
PROJECT SENTINEL - HUMAN INTERFACE API
FastAPI service for human operators to interact with AI recommendations.

Provides web interface for verification, decision-making, and monitoring.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn
import json

# Import our verification and tracking systems
from verification_system import (
    HumanInLoopVerificationSystem, AIRecommendation, HumanOperator,
    DecisionStatus, AlertLevel, InterventionRisk, UserRole
)
from decision_tracking_system import DecisionTrackingSystem, DecisionOutcome, PerformanceMetrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Project Sentinel - Human Interface API",
    description="Human-in-the-Loop verification system for AI conflict prevention",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Global systems
verification_system = None
tracking_system = None
active_connections: List[WebSocket] = []

# Pydantic models for API
class LoginRequest(BaseModel):
    user_id: str
    password: str = Field(..., min_length=6)

class RecommendationSubmission(BaseModel):
    intervention_type: str
    target_region: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    expected_outcome: str
    reasoning: str
    risk_level: str
    potential_casualties: int = Field(default=0, ge=0)
    success_probability: float = Field(default=0.5, ge=0.0, le=1.0)
    intelligence_sources: List[str] = []
    historical_precedents: List[str] = []
    alternative_options: List[str] = []

class HumanDecisionRequest(BaseModel):
    recommendation_id: str
    decision: str  # approved, rejected, modified, emergency_override
    reasoning: str = Field(..., min_length=10)
    modifications: Optional[Dict[str, Any]] = None
    urgency_override: bool = False

class OutcomeReport(BaseModel):
    recommendation_id: str
    actual_outcome: str
    effectiveness_score: float = Field(..., ge=0.0, le=1.0)
    unintended_consequences: List[str] = []
    lessons_learned: str = ""
    follow_up_required: bool = False

class AlertSubscription(BaseModel):
    user_id: str
    alert_levels: List[int] = [1, 2, 3]  # Which alert levels to receive
    regions: List[str] = []  # Which regions (empty = all)
    notification_methods: List[str] = ["websocket", "email"]

@app.on_event("startup")
async def startup_event():
    """Initialize the human interface systems."""
    global verification_system, tracking_system
    
    logger.info("🚀 Initializing Project Sentinel Human Interface API...")
    
    try:
        # Initialize verification system
        verification_system = HumanInLoopVerificationSystem()
        
        # Initialize tracking system
        tracking_system = DecisionTrackingSystem("sentinel_production.db")
        
        logger.info("✅ Human Interface API initialized successfully!")
        logger.info(f"🧑‍💼 Operators: {len(verification_system.operators)}")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        verification_system = None
        tracking_system = None

@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "service": "Project Sentinel Human Interface API",
        "status": "operational" if verification_system else "failed",
        "version": "1.0.0",
        "description": "Human-in-the-Loop verification system for AI conflict prevention decisions"
    }

@app.get("/health")
async def health_check():
    """System health check."""
    if not verification_system or not tracking_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    status = verification_system.get_system_status()
    
    return {
        "status": "healthy",
        "verification_system": status,
        "tracking_system": "operational",
        "active_websockets": len(active_connections),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/auth/login")
async def login(login_request: LoginRequest):
    """Authenticate human operator."""
    if not verification_system:
        raise HTTPException(status_code=503, detail="Verification system not available")
    
    # Check if operator exists (simplified auth - in production use proper JWT)
    operator = verification_system.operators.get(login_request.user_id)
    if not operator:
        raise HTTPException(status_code=401, detail="Invalid operator ID")
    
    if not operator.is_active:
        raise HTTPException(status_code=403, detail="Operator account disabled")
    
    # Update last activity
    operator.last_activity = datetime.now()
    
    return {
        "access_token": f"token_{login_request.user_id}_{datetime.now().timestamp()}",
        "token_type": "bearer",
        "operator": {
            "user_id": operator.user_id,
            "name": operator.name,
            "role": operator.role.value,
            "region_authorization": operator.region_authorization,
            "permissions": {
                "can_approve_low": operator.can_approve_low,
                "can_approve_medium": operator.can_approve_medium, 
                "can_approve_high": operator.can_approve_high,
                "can_emergency_override": operator.can_emergency_override
            }
        }
    }

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from token (simplified)."""
    token = credentials.credentials
    if not token.startswith("token_"):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    # Extract user_id from token (simplified - in production use proper JWT validation)
    try:
        user_id = token.split("_")[1]
        return user_id
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/recommendations/submit")
async def submit_ai_recommendation(
    recommendation: RecommendationSubmission,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Submit AI recommendation for human verification."""
    if not verification_system or not tracking_system:
        raise HTTPException(status_code=503, detail="Systems not available")
    
    try:
        # Convert to AIRecommendation object
        ai_recommendation = AIRecommendation(
            intervention_type=recommendation.intervention_type,
            target_region=recommendation.target_region,
            confidence_score=recommendation.confidence_score,
            expected_outcome=recommendation.expected_outcome,
            reasoning=recommendation.reasoning,
            risk_level=InterventionRisk(recommendation.risk_level),
            potential_casualties=recommendation.potential_casualties,
            success_probability=recommendation.success_probability,
            intelligence_sources=recommendation.intelligence_sources,
            historical_precedents=recommendation.historical_precedents,
            alternative_options=recommendation.alternative_options
        )
        
        # Submit to verification system
        recommendation_id = verification_system.submit_ai_recommendation(ai_recommendation)
        
        # Record in tracking system
        tracking_system.record_recommendation(ai_recommendation)
        
        # Send real-time alerts to operators
        background_tasks.add_task(
            send_real_time_alerts, 
            ai_recommendation
        )
        
        return {
            "success": True,
            "recommendation_id": recommendation_id,
            "alert_level": ai_recommendation.alert_level.name,
            "assigned_operator": ai_recommendation.assigned_operator,
            "timeout": ai_recommendation.approval_timeout.total_seconds()
        }
        
    except Exception as e:
        logger.error(f"❌ Error submitting recommendation: {e}")
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")

@app.get("/recommendations/pending")
async def get_pending_recommendations(current_user: str = Depends(get_current_user)):
    """Get pending recommendations for current operator."""
    if not verification_system:
        raise HTTPException(status_code=503, detail="Verification system not available")
    
    try:
        # Get pending decisions for this user
        pending_decisions = verification_system.get_pending_decisions(current_user)
        
        # Convert to API response format
        recommendations = []
        for decision in pending_decisions:
            recommendations.append({
                "recommendation_id": decision.recommendation_id,
                "timestamp": decision.timestamp.isoformat(),
                "intervention_type": decision.intervention_type,
                "target_region": decision.target_region,
                "confidence_score": decision.confidence_score,
                "expected_outcome": decision.expected_outcome,
                "reasoning": decision.reasoning,
                "risk_level": decision.risk_level.value,
                "alert_level": decision.alert_level.name,
                "potential_casualties": decision.potential_casualties,
                "success_probability": decision.success_probability,
                "intelligence_sources": decision.intelligence_sources,
                "historical_precedents": decision.historical_precedents,
                "alternative_options": decision.alternative_options,
                "requires_approval": decision.requires_approval,
                "timeout_remaining": (
                    decision.timestamp + decision.approval_timeout - datetime.now()
                ).total_seconds(),
                "is_expired": datetime.now() > decision.timestamp + decision.approval_timeout
            })
        
        return {
            "pending_recommendations": recommendations,
            "total_count": len(recommendations),
            "high_priority": len([r for r in recommendations if r["alert_level"] == "HIGH"]),
            "medium_priority": len([r for r in recommendations if r["alert_level"] == "MEDIUM"]),
            "low_priority": len([r for r in recommendations if r["alert_level"] == "LOW"])
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting pending recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@app.post("/recommendations/{recommendation_id}/decision")
async def make_human_decision(
    recommendation_id: str,
    decision_request: HumanDecisionRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Make human decision on AI recommendation."""
    if not verification_system or not tracking_system:
        raise HTTPException(status_code=503, detail="Systems not available")
    
    try:
        # Validate decision status
        try:
            decision_status = DecisionStatus(decision_request.decision)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid decision status")
        
        # Make decision in verification system
        success = verification_system.human_decision(
            recommendation_id,
            current_user,
            decision_status,
            decision_request.reasoning,
            decision_request.modifications
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Decision could not be processed")
        
        # Update tracking system
        tracking_system.update_recommendation_decision(
            recommendation_id,
            current_user,
            decision_status,
            decision_request.reasoning
        )
        
        # Send notifications
        background_tasks.add_task(
            notify_decision_stakeholders,
            recommendation_id,
            current_user,
            decision_status,
            decision_request.reasoning
        )
        
        return {
            "success": True,
            "decision": decision_status.value,
            "operator": current_user,
            "timestamp": datetime.now().isoformat(),
            "message": f"Decision '{decision_status.value}' recorded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error making decision: {e}")
        raise HTTPException(status_code=500, detail=f"Decision failed: {str(e)}")

@app.post("/recommendations/{recommendation_id}/outcome")
async def report_outcome(
    recommendation_id: str,
    outcome_report: OutcomeReport,
    current_user: str = Depends(get_current_user)
):
    """Report actual outcome of implemented decision."""
    if not tracking_system:
        raise HTTPException(status_code=503, detail="Tracking system not available")
    
    try:
        # Create outcome record
        outcome = DecisionOutcome(
            decision_id=f"outcome_{recommendation_id}_{datetime.now().timestamp()}",
            recommendation_id=recommendation_id,
            actual_outcome=outcome_report.actual_outcome,
            effectiveness_score=outcome_report.effectiveness_score,
            unintended_consequences=outcome_report.unintended_consequences,
            lessons_learned=outcome_report.lessons_learned,
            follow_up_required=outcome_report.follow_up_required
        )
        
        # Record outcome
        success = tracking_system.record_outcome(outcome)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to record outcome")
        
        return {
            "success": True,
            "outcome_id": outcome.decision_id,
            "effectiveness_score": outcome.effectiveness_score,
            "message": "Outcome recorded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error recording outcome: {e}")
        raise HTTPException(status_code=500, detail=f"Outcome recording failed: {str(e)}")

@app.get("/analytics/performance/{operator_id}")
async def get_operator_performance(
    operator_id: str,
    period_days: int = 30,
    current_user: str = Depends(get_current_user)
):
    """Get performance analytics for an operator."""
    if not tracking_system:
        raise HTTPException(status_code=503, detail="Tracking system not available")
    
    # Check authorization (operators can only view their own performance, commanders can view all)
    if current_user != operator_id:
        operator = verification_system.operators.get(current_user)
        if not operator or operator.role not in [UserRole.OPERATIONS_COMMANDER, UserRole.DEFENSE_MINISTER]:
            raise HTTPException(status_code=403, detail="Not authorized to view this performance data")
    
    try:
        # Calculate performance metrics
        performance = tracking_system.calculate_operator_performance(operator_id, period_days)
        
        return {
            "operator_id": performance.operator_id,
            "period": {
                "start_date": performance.period_start.isoformat(),
                "end_date": performance.period_end.isoformat(),
                "days": period_days
            },
            "decision_metrics": {
                "total_decisions": performance.total_decisions,
                "approved_decisions": performance.approved_decisions,
                "rejected_decisions": performance.rejected_decisions,
                "modified_decisions": performance.modified_decisions,
                "overridden_decisions": performance.overridden_decisions
            },
            "timing_metrics": {
                "average_decision_time_minutes": performance.average_decision_time,
                "timeout_count": performance.timeout_count
            },
            "effectiveness_metrics": {
                "average_effectiveness": performance.average_effectiveness,
                "successful_interventions": performance.successful_interventions,
                "failed_interventions": performance.failed_interventions
            },
            "bias_indicators": performance.bias_indicators,
            "improvement_trend": performance.improvement_trend
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting performance: {e}")
        raise HTTPException(status_code=500, detail=f"Performance analysis failed: {str(e)}")

@app.get("/analytics/system-report")
async def get_system_report(
    period_days: int = 7,
    current_user: str = Depends(get_current_user)
):
    """Generate system-wide analytics report."""
    if not tracking_system:
        raise HTTPException(status_code=503, detail="Tracking system not available")
    
    try:
        report = tracking_system.generate_decision_report(period_days)
        return report
        
    except Exception as e:
        logger.error(f"❌ Error generating report: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time alerts and updates."""
    await websocket.accept()
    active_connections.append(websocket)
    
    logger.info(f"🔗 WebSocket connected: {user_id}")
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection_established",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to Project Sentinel alerts"
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_json()
                
                # Handle different message types
                if data.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
    finally:
        active_connections.remove(websocket)
        logger.info(f"🔌 WebSocket disconnected: {user_id}")

async def send_real_time_alerts(recommendation: AIRecommendation):
    """Send real-time alerts to connected operators."""
    if not active_connections:
        return
    
    alert_data = {
        "type": "new_recommendation",
        "recommendation_id": recommendation.recommendation_id,
        "alert_level": recommendation.alert_level.name,
        "target_region": recommendation.target_region,
        "intervention_type": recommendation.intervention_type,
        "confidence_score": recommendation.confidence_score,
        "assigned_operator": recommendation.assigned_operator,
        "requires_approval": recommendation.requires_approval,
        "timeout_minutes": int(recommendation.approval_timeout.total_seconds() / 60),
        "timestamp": recommendation.timestamp.isoformat()
    }
    
    # Send to all connected clients (in production, would filter by operator assignment)
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(alert_data)
        except:
            disconnected.append(connection)
    
    # Remove disconnected clients
    for connection in disconnected:
        active_connections.remove(connection)

async def notify_decision_stakeholders(recommendation_id: str, operator_id: str,
                                     decision: DecisionStatus, reasoning: str):
    """Notify stakeholders of human decision."""
    notification_data = {
        "type": "decision_made",
        "recommendation_id": recommendation_id,
        "operator_id": operator_id,
        "decision": decision.value,
        "reasoning": reasoning[:100] + "..." if len(reasoning) > 100 else reasoning,
        "timestamp": datetime.now().isoformat()
    }
    
    # Send to connected clients
    for connection in active_connections:
        try:
            await connection.send_json(notification_data)
        except:
            pass

# Utility endpoints
@app.get("/operators")
async def list_operators(current_user: str = Depends(get_current_user)):
    """List all operators (for commanders only)."""
    if not verification_system:
        raise HTTPException(status_code=503, detail="Verification system not available")
    
    # Check authorization
    current_operator = verification_system.operators.get(current_user)
    if not current_operator or current_operator.role not in [
        UserRole.OPERATIONS_COMMANDER, UserRole.DEFENSE_MINISTER
    ]:
        raise HTTPException(status_code=403, detail="Not authorized to view operators")
    
    operators = []
    for op in verification_system.operators.values():
        operators.append({
            "user_id": op.user_id,
            "name": op.name,
            "role": op.role.value,
            "region_authorization": op.region_authorization,
            "is_active": op.is_active,
            "last_activity": op.last_activity.isoformat(),
            "contact_email": op.contact_email,
            "contact_phone": op.contact_phone
        })
    
    return {"operators": operators, "total_count": len(operators)}

@app.post("/admin/timeout-check")
async def check_timeouts(
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Manually check for expired decisions (admin only)."""
    if not verification_system:
        raise HTTPException(status_code=503, detail="Verification system not available")
    
    # Check authorization
    current_operator = verification_system.operators.get(current_user)
    if not current_operator or current_operator.role != UserRole.DEFENSE_MINISTER:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    expired_ids = verification_system.check_timeouts()
    
    return {
        "expired_count": len(expired_ids),
        "expired_ids": expired_ids,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # For development
    uvicorn.run(
        "human_interface_api:app",
        host="127.0.0.1",
        port=8005,
        log_level="info",
        reload=False
    )

