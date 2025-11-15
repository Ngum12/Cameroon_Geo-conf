"""
PROJECT SENTINEL - DECISION TRACKING SYSTEM
Complete audit trail and decision reasoning capture system.

Tracks all AI-human interactions with full accountability.
"""

import logging
import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import pandas as pd
from pathlib import Path

from verification_system import (
    AIRecommendation, HumanOperator, DecisionStatus, AlertLevel, 
    InterventionRisk, UserRole
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DecisionOutcome:
    """Track the outcome of human decisions."""
    decision_id: str
    recommendation_id: str
    actual_outcome: str = ""
    effectiveness_score: float = 0.0  # 0.0-1.0
    unintended_consequences: List[str] = None
    lessons_learned: str = ""
    follow_up_required: bool = False
    outcome_timestamp: datetime = None
    
    def __post_init__(self):
        if self.unintended_consequences is None:
            self.unintended_consequences = []
        if self.outcome_timestamp is None:
            self.outcome_timestamp = datetime.now()

@dataclass
class PerformanceMetrics:
    """Performance metrics for human operators."""
    operator_id: str
    period_start: datetime
    period_end: datetime
    
    # Decision metrics
    total_decisions: int = 0
    approved_decisions: int = 0
    rejected_decisions: int = 0
    modified_decisions: int = 0
    overridden_decisions: int = 0
    
    # Timing metrics  
    average_decision_time: float = 0.0  # minutes
    timeout_count: int = 0
    
    # Effectiveness metrics
    average_effectiveness: float = 0.0
    successful_interventions: int = 0
    failed_interventions: int = 0
    
    # Learning metrics
    bias_indicators: Dict[str, float] = None
    improvement_trend: float = 0.0
    
    def __post_init__(self):
        if self.bias_indicators is None:
            self.bias_indicators = {}

class DecisionTrackingSystem:
    """Complete decision tracking and audit system."""
    
    def __init__(self, db_path: str = "sentinel_decisions.db"):
        self.db_path = db_path
        self.init_database()
        
        # In-memory caches
        self.decision_cache: Dict[str, AIRecommendation] = {}
        self.outcome_cache: Dict[str, DecisionOutcome] = {}
        self.performance_cache: Dict[str, PerformanceMetrics] = {}
    
    def init_database(self):
        """Initialize SQLite database for decision tracking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Recommendations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                intervention_type TEXT NOT NULL,
                target_region TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                expected_outcome TEXT,
                reasoning TEXT,
                risk_level TEXT NOT NULL,
                potential_casualties INTEGER DEFAULT 0,
                success_probability REAL DEFAULT 0.0,
                alert_level INTEGER NOT NULL,
                requires_approval BOOLEAN DEFAULT TRUE,
                approval_timeout_minutes INTEGER,
                intelligence_sources TEXT,
                historical_precedents TEXT,
                alternative_options TEXT,
                status TEXT NOT NULL,
                assigned_operator TEXT,
                human_decision TEXT,
                human_reasoning TEXT,
                decision_timestamp TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Decision outcomes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decision_outcomes (
                id TEXT PRIMARY KEY,
                recommendation_id TEXT NOT NULL,
                actual_outcome TEXT,
                effectiveness_score REAL DEFAULT 0.0,
                unintended_consequences TEXT,
                lessons_learned TEXT,
                follow_up_required BOOLEAN DEFAULT FALSE,
                outcome_timestamp TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recommendation_id) REFERENCES recommendations (id)
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operator_id TEXT NOT NULL,
                period_start TEXT NOT NULL,
                period_end TEXT NOT NULL,
                total_decisions INTEGER DEFAULT 0,
                approved_decisions INTEGER DEFAULT 0,
                rejected_decisions INTEGER DEFAULT 0,
                modified_decisions INTEGER DEFAULT 0,
                overridden_decisions INTEGER DEFAULT 0,
                average_decision_time REAL DEFAULT 0.0,
                timeout_count INTEGER DEFAULT 0,
                average_effectiveness REAL DEFAULT 0.0,
                successful_interventions INTEGER DEFAULT 0,
                failed_interventions INTEGER DEFAULT 0,
                bias_indicators TEXT,
                improvement_trend REAL DEFAULT 0.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Audit log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                operator_id TEXT,
                recommendation_id TEXT,
                data TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Decision tracking database initialized: {self.db_path}")
    
    def record_recommendation(self, recommendation: AIRecommendation) -> bool:
        """Record AI recommendation in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert complex fields to JSON
            intelligence_sources = json.dumps(recommendation.intelligence_sources)
            historical_precedents = json.dumps(recommendation.historical_precedents)
            alternative_options = json.dumps(recommendation.alternative_options)
            
            cursor.execute('''
                INSERT INTO recommendations (
                    id, timestamp, intervention_type, target_region, confidence_score,
                    expected_outcome, reasoning, risk_level, potential_casualties,
                    success_probability, alert_level, requires_approval,
                    approval_timeout_minutes, intelligence_sources, historical_precedents,
                    alternative_options, status, assigned_operator, human_decision,
                    human_reasoning, decision_timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                recommendation.recommendation_id,
                recommendation.timestamp.isoformat(),
                recommendation.intervention_type,
                recommendation.target_region,
                recommendation.confidence_score,
                recommendation.expected_outcome,
                recommendation.reasoning,
                recommendation.risk_level.value,
                recommendation.potential_casualties,
                recommendation.success_probability,
                int(recommendation.alert_level),
                recommendation.requires_approval,
                int(recommendation.approval_timeout.total_seconds() / 60),
                intelligence_sources,
                historical_precedents,
                alternative_options,
                recommendation.status.value,
                recommendation.assigned_operator,
                recommendation.human_decision,
                recommendation.human_reasoning,
                recommendation.decision_timestamp.isoformat() if recommendation.decision_timestamp else None
            ))
            
            conn.commit()
            conn.close()
            
            # Cache the recommendation
            self.decision_cache[recommendation.recommendation_id] = recommendation
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error recording recommendation: {e}")
            return False
    
    def update_recommendation_decision(self, recommendation_id: str, 
                                     operator_id: str, decision: DecisionStatus,
                                     reasoning: str) -> bool:
        """Update recommendation with human decision."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            decision_time = datetime.now()
            
            cursor.execute('''
                UPDATE recommendations 
                SET status = ?, human_decision = ?, human_reasoning = ?, decision_timestamp = ?
                WHERE id = ?
            ''', (decision.value, operator_id, reasoning, decision_time.isoformat(), recommendation_id))
            
            conn.commit()
            conn.close()
            
            # Update cache
            if recommendation_id in self.decision_cache:
                rec = self.decision_cache[recommendation_id]
                rec.status = decision
                rec.human_decision = operator_id
                rec.human_reasoning = reasoning
                rec.decision_timestamp = decision_time
            
            # Log audit event
            self.log_audit_event(
                "decision_updated",
                operator_id, 
                recommendation_id,
                {
                    "decision": decision.value,
                    "reasoning_length": len(reasoning),
                    "decision_time": decision_time.isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating decision: {e}")
            return False
    
    def record_outcome(self, outcome: DecisionOutcome) -> bool:
        """Record the actual outcome of a decision."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO decision_outcomes (
                    id, recommendation_id, actual_outcome, effectiveness_score,
                    unintended_consequences, lessons_learned, follow_up_required,
                    outcome_timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                outcome.decision_id,
                outcome.recommendation_id,
                outcome.actual_outcome,
                outcome.effectiveness_score,
                json.dumps(outcome.unintended_consequences),
                outcome.lessons_learned,
                outcome.follow_up_required,
                outcome.outcome_timestamp.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            # Cache the outcome
            self.outcome_cache[outcome.decision_id] = outcome
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error recording outcome: {e}")
            return False
    
    def log_audit_event(self, event_type: str, operator_id: str, 
                       recommendation_id: str, data: Dict[str, Any],
                       ip_address: str = "", user_agent: str = "") -> bool:
        """Log audit event for compliance."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO audit_log (
                    timestamp, event_type, operator_id, recommendation_id,
                    data, ip_address, user_agent
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                event_type,
                operator_id,
                recommendation_id,
                json.dumps(data),
                ip_address,
                user_agent
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error logging audit event: {e}")
            return False
    
    def calculate_operator_performance(self, operator_id: str, 
                                     period_days: int = 30) -> PerformanceMetrics:
        """Calculate performance metrics for an operator."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get decisions in period
            decisions_df = pd.read_sql_query('''
                SELECT * FROM recommendations 
                WHERE human_decision = ? 
                AND decision_timestamp >= ? 
                AND decision_timestamp <= ?
            ''', conn, params=(operator_id, start_date.isoformat(), end_date.isoformat()))
            
            # Get outcomes for these decisions
            outcomes_df = pd.read_sql_query('''
                SELECT o.* FROM decision_outcomes o
                JOIN recommendations r ON o.recommendation_id = r.id
                WHERE r.human_decision = ?
                AND r.decision_timestamp >= ?
                AND r.decision_timestamp <= ?
            ''', conn, params=(operator_id, start_date.isoformat(), end_date.isoformat()))
            
            conn.close()
            
            # Calculate metrics
            metrics = PerformanceMetrics(
                operator_id=operator_id,
                period_start=start_date,
                period_end=end_date
            )
            
            if len(decisions_df) > 0:
                metrics.total_decisions = len(decisions_df)
                
                # Count decision types
                status_counts = decisions_df['status'].value_counts()
                metrics.approved_decisions = status_counts.get('approved', 0)
                metrics.rejected_decisions = status_counts.get('rejected', 0)
                metrics.modified_decisions = status_counts.get('modified', 0)
                metrics.overridden_decisions = status_counts.get('emergency_override', 0)
                
                # Calculate timing metrics
                decisions_df['timestamp'] = pd.to_datetime(decisions_df['timestamp'])
                decisions_df['decision_timestamp'] = pd.to_datetime(decisions_df['decision_timestamp'])
                
                # Decision times in minutes
                decision_times = (decisions_df['decision_timestamp'] - decisions_df['timestamp']).dt.total_seconds() / 60
                metrics.average_decision_time = float(decision_times.mean())
                
                # Timeout count
                approval_times = decisions_df['approval_timeout_minutes']
                metrics.timeout_count = int((decision_times > approval_times).sum())
                
                # Effectiveness metrics
                if len(outcomes_df) > 0:
                    metrics.average_effectiveness = float(outcomes_df['effectiveness_score'].mean())
                    metrics.successful_interventions = int((outcomes_df['effectiveness_score'] >= 0.7).sum())
                    metrics.failed_interventions = int((outcomes_df['effectiveness_score'] < 0.3).sum())
                
                # Bias detection (simplified)
                region_bias = self._detect_regional_bias(decisions_df)
                risk_bias = self._detect_risk_bias(decisions_df)
                
                metrics.bias_indicators = {
                    'regional_bias': region_bias,
                    'risk_bias': risk_bias
                }
                
                # Improvement trend (compare to previous period)
                previous_metrics = self._get_previous_performance(operator_id, period_days)
                if previous_metrics:
                    metrics.improvement_trend = metrics.average_effectiveness - previous_metrics.average_effectiveness
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error calculating performance: {e}")
            return PerformanceMetrics(operator_id=operator_id, period_start=start_date, period_end=end_date)
    
    def _detect_regional_bias(self, decisions_df: pd.DataFrame) -> float:
        """Detect potential regional bias in decisions."""
        if len(decisions_df) < 5:
            return 0.0
        
        # Calculate approval rates by region
        region_stats = decisions_df.groupby('target_region')['status'].apply(
            lambda x: (x == 'approved').mean()
        )
        
        if len(region_stats) < 2:
            return 0.0
        
        # Bias score: standard deviation of approval rates
        return float(region_stats.std())
    
    def _detect_risk_bias(self, decisions_df: pd.DataFrame) -> float:
        """Detect potential risk level bias in decisions."""
        if len(decisions_df) < 5:
            return 0.0
        
        # Calculate approval rates by risk level
        risk_stats = decisions_df.groupby('risk_level')['status'].apply(
            lambda x: (x == 'approved').mean()
        )
        
        if len(risk_stats) < 2:
            return 0.0
        
        # Expected: higher risk should have lower approval rates
        # Bias: if high-risk has higher approval rate than low-risk
        return float(risk_stats.std())
    
    def _get_previous_performance(self, operator_id: str, period_days: int) -> Optional[PerformanceMetrics]:
        """Get previous period performance for comparison."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get most recent performance record
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM performance_metrics 
                WHERE operator_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (operator_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return PerformanceMetrics(
                    operator_id=row[1],
                    period_start=datetime.fromisoformat(row[2]),
                    period_end=datetime.fromisoformat(row[3]),
                    average_effectiveness=row[12]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting previous performance: {e}")
            return None
    
    def generate_decision_report(self, period_days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive decision tracking report."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get all decisions in period
            decisions_df = pd.read_sql_query('''
                SELECT * FROM recommendations 
                WHERE timestamp >= ? 
                ORDER BY timestamp DESC
            ''', conn, params=(start_date.isoformat(),))
            
            # Get outcomes
            outcomes_df = pd.read_sql_query('''
                SELECT * FROM decision_outcomes 
                WHERE outcome_timestamp >= ?
            ''', conn, params=(start_date.isoformat(),))
            
            # Get audit events
            audit_df = pd.read_sql_query('''
                SELECT * FROM audit_log 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', conn, params=(start_date.isoformat(),))
            
            conn.close()
            
            # Generate report
            report = {
                'report_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'period_days': period_days
                },
                'summary_statistics': {
                    'total_recommendations': len(decisions_df),
                    'pending_decisions': len(decisions_df[decisions_df['status'] == 'pending']),
                    'approved_decisions': len(decisions_df[decisions_df['status'] == 'approved']),
                    'rejected_decisions': len(decisions_df[decisions_df['status'] == 'rejected']),
                    'modified_decisions': len(decisions_df[decisions_df['status'] == 'modified']),
                    'expired_decisions': len(decisions_df[decisions_df['status'] == 'expired'])
                },
                'alert_level_breakdown': {},
                'regional_analysis': {},
                'operator_performance': {},
                'effectiveness_metrics': {},
                'audit_trail': {
                    'total_events': len(audit_df),
                    'event_types': audit_df['event_type'].value_counts().to_dict() if len(audit_df) > 0 else {}
                }
            }
            
            if len(decisions_df) > 0:
                # Alert level breakdown
                alert_counts = decisions_df['alert_level'].value_counts()
                report['alert_level_breakdown'] = {
                    'high_priority': int(alert_counts.get(3, 0)),
                    'medium_priority': int(alert_counts.get(2, 0)),
                    'low_priority': int(alert_counts.get(1, 0))
                }
                
                # Regional analysis
                region_stats = decisions_df.groupby('target_region').agg({
                    'id': 'count',
                    'status': lambda x: (x == 'approved').mean(),
                    'confidence_score': 'mean'
                }).round(3)
                
                report['regional_analysis'] = region_stats.to_dict('index')
            
            if len(outcomes_df) > 0:
                # Effectiveness metrics
                report['effectiveness_metrics'] = {
                    'average_effectiveness': float(outcomes_df['effectiveness_score'].mean()),
                    'successful_rate': float((outcomes_df['effectiveness_score'] >= 0.7).mean()),
                    'failure_rate': float((outcomes_df['effectiveness_score'] < 0.3).mean()),
                    'total_outcomes_tracked': len(outcomes_df)
                }
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating decision report: {e}")
            return {"error": str(e)}
    
    def export_audit_trail(self, output_path: str = "audit_trail_export.json") -> bool:
        """Export complete audit trail for compliance."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get all tables
            recommendations_df = pd.read_sql_query('SELECT * FROM recommendations ORDER BY timestamp', conn)
            outcomes_df = pd.read_sql_query('SELECT * FROM decision_outcomes ORDER BY outcome_timestamp', conn)
            audit_df = pd.read_sql_query('SELECT * FROM audit_log ORDER BY timestamp', conn)
            
            conn.close()
            
            # Create export data
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'total_recommendations': len(recommendations_df),
                'total_outcomes': len(outcomes_df),
                'total_audit_events': len(audit_df),
                'recommendations': recommendations_df.to_dict('records'),
                'outcomes': outcomes_df.to_dict('records'),
                'audit_log': audit_df.to_dict('records')
            }
            
            # Write to file
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"✅ Audit trail exported to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exporting audit trail: {e}")
            return False

# Main demonstration
if __name__ == "__main__":
    logger.info("📊 PROJECT SENTINEL - DECISION TRACKING SYSTEM")
    logger.info("=" * 60)
    
    # Initialize tracking system
    tracker = DecisionTrackingSystem("test_decisions.db")
    
    # Create sample data
    from verification_system import AIRecommendation, InterventionRisk
    
    sample_recommendation = AIRecommendation(
        intervention_type="diplomatic_mediation",
        target_region="Nord-Ouest",
        confidence_score=0.78,
        expected_outcome="Resolve land disputes between farmers and herders",
        reasoning="Recent escalation in land conflicts requires immediate mediation.",
        risk_level=InterventionRisk.DIPLOMATIC_LOW,
        potential_casualties=0,
        success_probability=0.75
    )
    
    # Record recommendation
    success = tracker.record_recommendation(sample_recommendation)
    logger.info(f"📋 Recommendation recorded: {success}")
    
    # Update with human decision
    success = tracker.update_recommendation_decision(
        sample_recommendation.recommendation_id,
        "cmd_002",
        DecisionStatus.APPROVED,
        "Mediation appropriate for land conflicts. Local traditional leaders should be involved."
    )
    logger.info(f"✅ Decision updated: {success}")
    
    # Record outcome
    outcome = DecisionOutcome(
        decision_id=str(uuid.uuid4()),
        recommendation_id=sample_recommendation.recommendation_id,
        actual_outcome="Successful mediation resulted in peaceful resolution of land disputes",
        effectiveness_score=0.85,
        lessons_learned="Traditional leader involvement critical for success in rural conflicts"
    )
    
    success = tracker.record_outcome(outcome)
    logger.info(f"📈 Outcome recorded: {success}")
    
    # Generate performance metrics
    performance = tracker.calculate_operator_performance("cmd_002", 30)
    logger.info(f"👤 Performance metrics calculated for operator cmd_002")
    logger.info(f"   Total decisions: {performance.total_decisions}")
    logger.info(f"   Average effectiveness: {performance.average_effectiveness:.3f}")
    
    # Generate decision report
    report = tracker.generate_decision_report(7)
    logger.info(f"📊 Decision report generated:")
    logger.info(f"   Total recommendations: {report['summary_statistics']['total_recommendations']}")
    logger.info(f"   Audit events: {report['audit_trail']['total_events']}")
    
    # Export audit trail
    success = tracker.export_audit_trail("test_audit_export.json")
    logger.info(f"💾 Audit trail exported: {success}")
    
    logger.info("✅ DECISION TRACKING SYSTEM OPERATIONAL!")
    logger.info("🔒 COMPLETE ACCOUNTABILITY AND AUDIT TRAIL READY")
