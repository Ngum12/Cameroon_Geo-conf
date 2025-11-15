"""
PROJECT SENTINEL - VERIFICATION SYSTEM
Cameroon Defense Force Human-in-the-Loop Architecture

Critical human oversight system for life-or-death AI decisions.
Three-tier alert system with mandatory human verification.

⚠️ MISSION CRITICAL: NO AI ACTION WITHOUT APPROPRIATE HUMAN APPROVAL ⚠️
"""

import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum, IntEnum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
import json
import asyncio
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertLevel(IntEnum):
    """Three-tier alert system for human verification."""
    LOW = 1      # Automated with logging
    MEDIUM = 2   # Human review within 1 hour  
    HIGH = 3     # Human approval required before action

class DecisionStatus(Enum):
    """Status of AI recommendations requiring human oversight."""
    PENDING = "pending"              # Awaiting human review
    APPROVED = "approved"            # Human approved the action
    REJECTED = "rejected"            # Human rejected the action
    MODIFIED = "modified"            # Human modified the recommendation
    EXPIRED = "expired"              # Timeout exceeded without decision
    ESCALATED = "escalated"          # Escalated to higher authority
    EMERGENCY_OVERRIDE = "emergency_override"  # Emergency human override

class UserRole(Enum):
    """User roles with different authorization levels."""
    FIELD_OPERATOR = "field_operator"        # Regional commanders
    INTELLIGENCE_ANALYST = "intelligence_analyst"  # Intelligence staff
    OPERATIONS_COMMANDER = "operations_commander"  # Operations command
    DEFENSE_MINISTER = "defense_minister"    # Highest authority
    SYSTEM_ADMIN = "system_admin"           # Technical administration

class InterventionRisk(Enum):
    """Risk classification for interventions."""
    DIPLOMATIC_LOW = "diplomatic_low"        # Dialogue, mediation
    ECONOMIC_MEDIUM = "economic_medium"      # Aid, development projects
    SECURITY_HIGH = "security_high"         # Military deployment
    EMERGENCY_CRITICAL = "emergency_critical"  # Life-threatening situations

@dataclass
class HumanOperator:
    """Human operator with authorization levels."""
    user_id: str
    name: str
    role: UserRole
    region_authorization: List[str] = field(default_factory=list)  # Authorized regions
    contact_email: str = ""
    contact_phone: str = ""
    is_active: bool = True
    last_activity: datetime = field(default_factory=datetime.now)
    
    # Authorization levels
    can_approve_low: bool = True
    can_approve_medium: bool = False
    can_approve_high: bool = False
    can_emergency_override: bool = False
    
    def __post_init__(self):
        """Set authorization levels based on role."""
        if self.role == UserRole.FIELD_OPERATOR:
            self.can_approve_low = True
            self.can_approve_medium = True
        elif self.role == UserRole.INTELLIGENCE_ANALYST:
            self.can_approve_low = True
            self.can_approve_medium = True
        elif self.role == UserRole.OPERATIONS_COMMANDER:
            self.can_approve_low = True
            self.can_approve_medium = True
            self.can_approve_high = True
        elif self.role == UserRole.DEFENSE_MINISTER:
            self.can_approve_low = True
            self.can_approve_medium = True
            self.can_approve_high = True
            self.can_emergency_override = True

@dataclass
class AIRecommendation:
    """AI-generated recommendation requiring human oversight."""
    recommendation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    
    # AI Analysis
    intervention_type: str = ""
    target_region: str = ""
    confidence_score: float = 0.0
    expected_outcome: str = ""
    reasoning: str = ""
    
    # Risk Assessment
    risk_level: InterventionRisk = InterventionRisk.DIPLOMATIC_LOW
    potential_casualties: int = 0
    resource_requirements: Dict[str, float] = field(default_factory=dict)
    success_probability: float = 0.0
    
    # Alert Classification
    alert_level: AlertLevel = AlertLevel.LOW
    requires_approval: bool = True
    approval_timeout: timedelta = timedelta(hours=24)
    
    # Supporting Evidence
    intelligence_sources: List[str] = field(default_factory=list)
    historical_precedents: List[str] = field(default_factory=list)
    alternative_options: List[str] = field(default_factory=list)
    
    # Current Status
    status: DecisionStatus = DecisionStatus.PENDING
    assigned_operator: Optional[str] = None
    human_decision: Optional[str] = None
    human_reasoning: str = ""
    decision_timestamp: Optional[datetime] = None

class VerificationRules:
    """Rules engine for determining alert levels and approval requirements."""
    
    @staticmethod
    def classify_alert_level(recommendation: AIRecommendation) -> AlertLevel:
        """Determine alert level based on recommendation characteristics."""
        
        # LEVEL 3 (HIGH) - Human approval required before action
        high_risk_conditions = [
            recommendation.risk_level == InterventionRisk.SECURITY_HIGH,
            recommendation.risk_level == InterventionRisk.EMERGENCY_CRITICAL,
            recommendation.potential_casualties > 5,
            recommendation.confidence_score < 0.6,  # Low confidence requires human check
            "military" in recommendation.intervention_type.lower(),
            "security" in recommendation.intervention_type.lower(),
            recommendation.target_region in ["Extreme-Nord", "Sud-Ouest", "Nord-Ouest"],  # High-risk regions
        ]
        
        if any(high_risk_conditions):
            return AlertLevel.HIGH
        
        # LEVEL 2 (MEDIUM) - Human review within 1 hour
        medium_risk_conditions = [
            recommendation.risk_level == InterventionRisk.ECONOMIC_MEDIUM,
            recommendation.potential_casualties > 0,
            recommendation.success_probability < 0.7,
            "economic" in recommendation.intervention_type.lower(),
            recommendation.resource_requirements.get("total", 0) > 0.5,  # High resource usage
        ]
        
        if any(medium_risk_conditions):
            return AlertLevel.MEDIUM
        
        # LEVEL 1 (LOW) - Automated with logging
        return AlertLevel.LOW
    
    @staticmethod
    def determine_required_role(alert_level: AlertLevel, 
                              intervention_risk: InterventionRisk) -> UserRole:
        """Determine minimum user role required for approval."""
        
        if alert_level == AlertLevel.HIGH:
            if intervention_risk == InterventionRisk.EMERGENCY_CRITICAL:
                return UserRole.DEFENSE_MINISTER
            elif intervention_risk == InterventionRisk.SECURITY_HIGH:
                return UserRole.OPERATIONS_COMMANDER
            else:
                return UserRole.OPERATIONS_COMMANDER
        
        elif alert_level == AlertLevel.MEDIUM:
            return UserRole.INTELLIGENCE_ANALYST
        
        else:  # LOW
            return UserRole.FIELD_OPERATOR
    
    @staticmethod
    def calculate_timeout(alert_level: AlertLevel, 
                         intervention_risk: InterventionRisk) -> timedelta:
        """Calculate approval timeout based on urgency."""
        
        if intervention_risk == InterventionRisk.EMERGENCY_CRITICAL:
            return timedelta(minutes=30)  # 30 minutes for emergencies
        elif alert_level == AlertLevel.HIGH:
            return timedelta(hours=2)     # 2 hours for high-risk
        elif alert_level == AlertLevel.MEDIUM:
            return timedelta(hours=1)     # 1 hour for medium-risk
        else:
            return timedelta(hours=24)    # 24 hours for low-risk

class HumanInLoopVerificationSystem:
    """Core human verification system for AI recommendations."""
    
    def __init__(self):
        self.operators: Dict[str, HumanOperator] = {}
        self.pending_decisions: Dict[str, AIRecommendation] = {}
        self.decision_history: List[AIRecommendation] = []
        self.audit_log: List[Dict[str, Any]] = []
        
        # Initialize default operators (would be loaded from database in production)
        self._initialize_default_operators()
    
    def _initialize_default_operators(self):
        """Initialize default human operators."""
        default_operators = [
            HumanOperator(
                user_id="cmd_001",
                name="Colonel Nkomo",
                role=UserRole.OPERATIONS_COMMANDER,
                region_authorization=["Centre", "Littoral", "Sud", "Ouest"],
                contact_email="nkomo@defense.cm",
                contact_phone="+237-600-000-001"
            ),
            HumanOperator(
                user_id="cmd_002", 
                name="Major Fotso",
                role=UserRole.OPERATIONS_COMMANDER,
                region_authorization=["Nord", "Adamaoua", "Est"],
                contact_email="fotso@defense.cm",
                contact_phone="+237-600-000-002"
            ),
            HumanOperator(
                user_id="cmd_003",
                name="Lieutenant Colonel Mbarga",
                role=UserRole.OPERATIONS_COMMANDER,
                region_authorization=["Extreme-Nord", "Sud-Ouest", "Nord-Ouest"],
                contact_email="mbarga@defense.cm", 
                contact_phone="+237-600-000-003"
            ),
            HumanOperator(
                user_id="minister_001",
                name="Minister Atangana",
                role=UserRole.DEFENSE_MINISTER,
                region_authorization=["ALL"],
                contact_email="minister@defense.cm",
                contact_phone="+237-600-000-000"
            )
        ]
        
        for operator in default_operators:
            self.operators[operator.user_id] = operator
        
        logger.info(f"✅ Initialized {len(self.operators)} human operators")
    
    def submit_ai_recommendation(self, recommendation: AIRecommendation) -> str:
        """Submit AI recommendation for human verification."""
        
        # Classify alert level
        recommendation.alert_level = VerificationRules.classify_alert_level(recommendation)
        
        # Determine required role and timeout
        required_role = VerificationRules.determine_required_role(
            recommendation.alert_level, recommendation.risk_level
        )
        recommendation.approval_timeout = VerificationRules.calculate_timeout(
            recommendation.alert_level, recommendation.risk_level
        )
        
        # Assign to appropriate operator
        assigned_operator = self._assign_operator(recommendation.target_region, required_role)
        if assigned_operator:
            recommendation.assigned_operator = assigned_operator.user_id
        
        # Store pending decision
        self.pending_decisions[recommendation.recommendation_id] = recommendation
        
        # Log submission
        self._log_audit_event(
            "recommendation_submitted",
            recommendation.recommendation_id,
            {
                "alert_level": recommendation.alert_level.name,
                "assigned_to": recommendation.assigned_operator,
                "requires_approval": recommendation.requires_approval,
                "timeout_hours": recommendation.approval_timeout.total_seconds() / 3600
            }
        )
        
        # Send alerts based on level
        self._send_alert(recommendation)
        
        logger.info(f"📋 AI Recommendation submitted: {recommendation.recommendation_id}")
        logger.info(f"   Alert Level: {recommendation.alert_level.name}")
        logger.info(f"   Assigned to: {assigned_operator.name if assigned_operator else 'UNASSIGNED'}")
        logger.info(f"   Timeout: {recommendation.approval_timeout}")
        
        return recommendation.recommendation_id
    
    def _assign_operator(self, target_region: str, 
                        required_role: UserRole) -> Optional[HumanOperator]:
        """Assign appropriate operator based on region and role."""
        
        # Find operators with appropriate role and region authorization
        eligible_operators = []
        
        for operator in self.operators.values():
            if not operator.is_active:
                continue
            
            # Check role authorization
            role_authorized = False
            if required_role == UserRole.FIELD_OPERATOR and operator.role in [
                UserRole.FIELD_OPERATOR, UserRole.INTELLIGENCE_ANALYST, 
                UserRole.OPERATIONS_COMMANDER, UserRole.DEFENSE_MINISTER
            ]:
                role_authorized = True
            elif required_role == UserRole.INTELLIGENCE_ANALYST and operator.role in [
                UserRole.INTELLIGENCE_ANALYST, UserRole.OPERATIONS_COMMANDER, UserRole.DEFENSE_MINISTER
            ]:
                role_authorized = True
            elif required_role == UserRole.OPERATIONS_COMMANDER and operator.role in [
                UserRole.OPERATIONS_COMMANDER, UserRole.DEFENSE_MINISTER
            ]:
                role_authorized = True
            elif required_role == UserRole.DEFENSE_MINISTER and operator.role == UserRole.DEFENSE_MINISTER:
                role_authorized = True
            
            # Check region authorization
            region_authorized = (
                "ALL" in operator.region_authorization or 
                target_region in operator.region_authorization
            )
            
            if role_authorized and region_authorized:
                eligible_operators.append(operator)
        
        # Return most recent active operator or first available
        if eligible_operators:
            return max(eligible_operators, key=lambda op: op.last_activity)
        
        logger.warning(f"⚠️ No eligible operator found for {target_region}, role {required_role}")
        return None
    
    def _send_alert(self, recommendation: AIRecommendation):
        """Send alerts to assigned operator based on alert level."""
        
        if not recommendation.assigned_operator:
            logger.error(f"❌ Cannot send alert: No operator assigned to {recommendation.recommendation_id}")
            return
        
        operator = self.operators[recommendation.assigned_operator]
        
        # Compose alert message
        urgency = "🔴 CRITICAL" if recommendation.alert_level == AlertLevel.HIGH else \
                 "🟡 URGENT" if recommendation.alert_level == AlertLevel.MEDIUM else \
                 "🟢 ROUTINE"
        
        alert_message = f"""
{urgency} - PROJECT SENTINEL ALERT

Recommendation ID: {recommendation.recommendation_id}
Region: {recommendation.target_region}
Intervention: {recommendation.intervention_type}
Confidence: {recommendation.confidence_score:.1%}
Risk Level: {recommendation.risk_level.value}

Reasoning: {recommendation.reasoning[:200]}...

Action Required: {'IMMEDIATE APPROVAL' if recommendation.alert_level == AlertLevel.HIGH else 'REVIEW WITHIN 1 HOUR' if recommendation.alert_level == AlertLevel.MEDIUM else 'ROUTINE REVIEW'}
Timeout: {recommendation.approval_timeout}

Operator: {operator.name}
Contact: {operator.contact_phone}
        """
        
        # Log alert (in production, would send actual notifications)
        logger.info(f"📢 ALERT SENT to {operator.name}:")
        logger.info(alert_message)
        
        # In production, would integrate with:
        # - SMS/WhatsApp alerts
        # - Email notifications  
        # - Push notifications to mobile app
        # - Dashboard alerts
        # - Radio communications for emergencies
    
    def human_decision(self, recommendation_id: str, user_id: str, 
                      decision: DecisionStatus, reasoning: str = "",
                      modifications: Optional[Dict[str, Any]] = None) -> bool:
        """Process human decision on AI recommendation."""
        
        if recommendation_id not in self.pending_decisions:
            logger.error(f"❌ Recommendation {recommendation_id} not found in pending decisions")
            return False
        
        recommendation = self.pending_decisions[recommendation_id]
        operator = self.operators.get(user_id)
        
        if not operator:
            logger.error(f"❌ Operator {user_id} not found")
            return False
        
        # Verify operator authorization
        if not self._verify_authorization(operator, recommendation):
            logger.error(f"❌ Operator {operator.name} not authorized for this decision")
            return False
        
        # Process decision
        recommendation.status = decision
        recommendation.human_decision = user_id
        recommendation.human_reasoning = reasoning
        recommendation.decision_timestamp = datetime.now()
        
        # Apply modifications if provided
        if modifications and decision == DecisionStatus.MODIFIED:
            for key, value in modifications.items():
                if hasattr(recommendation, key):
                    setattr(recommendation, key, value)
        
        # Move from pending to history
        self.decision_history.append(recommendation)
        del self.pending_decisions[recommendation_id]
        
        # Log decision
        self._log_audit_event(
            "human_decision",
            recommendation_id,
            {
                "operator": operator.name,
                "decision": decision.value,
                "reasoning": reasoning,
                "modifications": modifications
            }
        )
        
        logger.info(f"✅ Human Decision Recorded:")
        logger.info(f"   Recommendation: {recommendation_id}")
        logger.info(f"   Operator: {operator.name}")
        logger.info(f"   Decision: {decision.value}")
        logger.info(f"   Reasoning: {reasoning[:100]}...")
        
        return True
    
    def _verify_authorization(self, operator: HumanOperator, 
                            recommendation: AIRecommendation) -> bool:
        """Verify operator is authorized to make this decision."""
        
        # Check alert level authorization
        if recommendation.alert_level == AlertLevel.HIGH and not operator.can_approve_high:
            return False
        elif recommendation.alert_level == AlertLevel.MEDIUM and not operator.can_approve_medium:
            return False
        elif recommendation.alert_level == AlertLevel.LOW and not operator.can_approve_low:
            return False
        
        # Check regional authorization
        if ("ALL" not in operator.region_authorization and 
            recommendation.target_region not in operator.region_authorization):
            return False
        
        return True
    
    def _log_audit_event(self, event_type: str, recommendation_id: str, data: Dict[str, Any]):
        """Log audit event for compliance and tracking."""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "recommendation_id": recommendation_id,
            "data": data
        }
        self.audit_log.append(audit_entry)
    
    def get_pending_decisions(self, user_id: str) -> List[AIRecommendation]:
        """Get pending decisions for a specific operator."""
        operator = self.operators.get(user_id)
        if not operator:
            return []
        
        # Return decisions assigned to this operator
        user_decisions = []
        for rec in self.pending_decisions.values():
            if rec.assigned_operator == user_id:
                user_decisions.append(rec)
        
        return sorted(user_decisions, key=lambda r: r.timestamp, reverse=True)
    
    def check_timeouts(self) -> List[str]:
        """Check for expired decisions and handle timeouts."""
        expired_ids = []
        current_time = datetime.now()
        
        for rec_id, recommendation in self.pending_decisions.items():
            if current_time > recommendation.timestamp + recommendation.approval_timeout:
                recommendation.status = DecisionStatus.EXPIRED
                expired_ids.append(rec_id)
                
                # Log timeout
                self._log_audit_event(
                    "decision_timeout",
                    rec_id,
                    {"timeout_duration": recommendation.approval_timeout.total_seconds()}
                )
        
        # Move expired decisions to history
        for rec_id in expired_ids:
            self.decision_history.append(self.pending_decisions[rec_id])
            del self.pending_decisions[rec_id]
        
        if expired_ids:
            logger.warning(f"⚠️ {len(expired_ids)} decisions expired due to timeout")
        
        return expired_ids
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "active_operators": len([op for op in self.operators.values() if op.is_active]),
            "pending_decisions": len(self.pending_decisions),
            "pending_high_priority": len([r for r in self.pending_decisions.values() 
                                        if r.alert_level == AlertLevel.HIGH]),
            "pending_medium_priority": len([r for r in self.pending_decisions.values() 
                                          if r.alert_level == AlertLevel.MEDIUM]),
            "pending_low_priority": len([r for r in self.pending_decisions.values() 
                                       if r.alert_level == AlertLevel.LOW]),
            "decisions_today": len([r for r in self.decision_history 
                                  if r.decision_timestamp and 
                                  r.decision_timestamp.date() == datetime.now().date()]),
            "audit_entries": len(self.audit_log),
            "system_operational": True
        }

# Main demonstration
if __name__ == "__main__":
    logger.info("🚨 PROJECT SENTINEL - HUMAN-IN-THE-LOOP VERIFICATION SYSTEM")
    logger.info("=" * 80)
    
    # Initialize system
    verification_system = HumanInLoopVerificationSystem()
    
    # Create sample AI recommendations
    recommendations = [
        AIRecommendation(
            intervention_type="diplomatic_dialogue",
            target_region="Centre",
            confidence_score=0.85,
            expected_outcome="Reduce tensions between communities",
            reasoning="Recent intelligence suggests escalating ethnic tensions in Yaoundé suburbs. Diplomatic intervention recommended.",
            risk_level=InterventionRisk.DIPLOMATIC_LOW,
            potential_casualties=0,
            success_probability=0.8
        ),
        AIRecommendation(
            intervention_type="military_security_deployment",
            target_region="Extreme-Nord",
            confidence_score=0.72,
            expected_outcome="Prevent Boko Haram attack on civilian population",
            reasoning="Intercepted communications indicate planned attack on Maroua market. Military deployment recommended.",
            risk_level=InterventionRisk.SECURITY_HIGH,
            potential_casualties=10,
            success_probability=0.65
        ),
        AIRecommendation(
            intervention_type="economic_development_aid",
            target_region="Sud-Ouest",
            confidence_score=0.68,
            expected_outcome="Reduce separatist support through economic development",
            reasoning="High unemployment in anglophone regions contributing to separatist sentiment. Economic aid recommended.",
            risk_level=InterventionRisk.ECONOMIC_MEDIUM,
            potential_casualties=0,
            success_probability=0.7
        )
    ]
    
    # Submit recommendations
    logger.info("\n📋 SUBMITTING AI RECOMMENDATIONS:")
    recommendation_ids = []
    for rec in recommendations:
        rec_id = verification_system.submit_ai_recommendation(rec)
        recommendation_ids.append(rec_id)
    
    # Display system status
    logger.info("\n📊 SYSTEM STATUS:")
    status = verification_system.get_system_status()
    for key, value in status.items():
        logger.info(f"   {key}: {value}")
    
    # Simulate human decisions
    logger.info("\n👤 SIMULATING HUMAN DECISIONS:")
    
    # Approve diplomatic intervention (low-risk)
    verification_system.human_decision(
        recommendation_ids[0],
        "cmd_001",
        DecisionStatus.APPROVED,
        "Diplomatic solution appropriate for ethnic tensions. Minimal risk, high potential for peaceful resolution."
    )
    
    # Modify military intervention (high-risk)
    verification_system.human_decision(
        recommendation_ids[1],
        "cmd_003", 
        DecisionStatus.MODIFIED,
        "Approved with modifications: Reduce deployment size but increase intelligence gathering.",
        modifications={"resource_requirements": {"military": 0.3}}
    )
    
    # Reject economic intervention (medium-risk)
    verification_system.human_decision(
        recommendation_ids[2],
        "cmd_001",
        DecisionStatus.REJECTED,
        "Economic aid inappropriate at this time. Political negotiations should precede economic interventions."
    )
    
    # Final system status
    logger.info("\n📈 FINAL SYSTEM STATUS:")
    final_status = verification_system.get_system_status()
    for key, value in final_status.items():
        logger.info(f"   {key}: {value}")
    
    logger.info("✅ HUMAN-IN-THE-LOOP VERIFICATION SYSTEM READY!")
    logger.info("🛡️ CRITICAL HUMAN OVERSIGHT OPERATIONAL FOR LIFE-OR-DEATH DECISIONS")

