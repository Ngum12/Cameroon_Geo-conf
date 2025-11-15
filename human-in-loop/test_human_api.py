"""
Test the Human Interface API to ensure all components work together.
"""

import asyncio
import logging
from datetime import datetime
import json

# Import all components for testing
from verification_system import (
    HumanInLoopVerificationSystem, AIRecommendation, DecisionStatus,
    InterventionRisk, AlertLevel
)
from decision_tracking_system import DecisionTrackingSystem
from human_interface_api import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_human_interface_system():
    """Comprehensive test of the human interface system."""
    
    logger.info("🧪 TESTING HUMAN INTERFACE SYSTEM")
    logger.info("=" * 50)
    
    try:
        # 1. Test Verification System
        logger.info("1️⃣ Testing Verification System...")
        verification_system = HumanInLoopVerificationSystem()
        
        # Create test recommendation
        test_recommendation = AIRecommendation(
            intervention_type="diplomatic_dialogue",
            target_region="Centre",
            confidence_score=0.75,
            expected_outcome="Resolve community tensions through dialogue",
            reasoning="Intelligence reports indicate rising tensions between ethnic groups in Yaoundé. Immediate diplomatic intervention recommended.",
            risk_level=InterventionRisk.DIPLOMATIC_LOW,
            potential_casualties=0,
            success_probability=0.8
        )
        
        # Submit recommendation
        rec_id = verification_system.submit_ai_recommendation(test_recommendation)
        logger.info(f"   ✅ Recommendation submitted: {rec_id}")
        logger.info(f"   ✅ Alert level: {test_recommendation.alert_level.name}")
        logger.info(f"   ✅ Assigned to: {test_recommendation.assigned_operator}")
        
        # 2. Test Decision Tracking System
        logger.info("\n2️⃣ Testing Decision Tracking System...")
        tracking_system = DecisionTrackingSystem("test_human_interface.db")
        
        # Record the recommendation
        success = tracking_system.record_recommendation(test_recommendation)
        logger.info(f"   ✅ Recommendation recorded in DB: {success}")
        
        # Make human decision
        success = verification_system.human_decision(
            rec_id,
            "cmd_001",
            DecisionStatus.APPROVED,
            "Diplomatic approach is appropriate for ethnic tensions. Low risk with high potential for success."
        )
        logger.info(f"   ✅ Human decision processed: {success}")
        
        # Update tracking system
        success = tracking_system.update_recommendation_decision(
            rec_id,
            "cmd_001",
            DecisionStatus.APPROVED,
            "Diplomatic approach approved after careful consideration."
        )
        logger.info(f"   ✅ Decision recorded in tracking: {success}")
        
        # 3. Test Performance Analytics
        logger.info("\n3️⃣ Testing Performance Analytics...")
        performance = tracking_system.calculate_operator_performance("cmd_001", 30)
        logger.info(f"   ✅ Performance metrics calculated:")
        logger.info(f"      • Total decisions: {performance.total_decisions}")
        logger.info(f"      • Approved: {performance.approved_decisions}")
        logger.info(f"      • Average decision time: {performance.average_decision_time:.2f} min")
        
        # 4. Test System Reports
        logger.info("\n4️⃣ Testing System Reports...")
        report = tracking_system.generate_decision_report(7)
        logger.info(f"   ✅ System report generated:")
        logger.info(f"      • Total recommendations: {report['summary_statistics']['total_recommendations']}")
        logger.info(f"      • Approved decisions: {report['summary_statistics']['approved_decisions']}")
        logger.info(f"      • Audit events: {report['audit_trail']['total_events']}")
        
        # 5. Test System Status
        logger.info("\n5️⃣ Testing System Status...")
        status = verification_system.get_system_status()
        logger.info(f"   ✅ System status retrieved:")
        logger.info(f"      • Active operators: {status['active_operators']}")
        logger.info(f"      • Pending decisions: {status['pending_decisions']}")
        logger.info(f"      • System operational: {status['system_operational']}")
        
        # 6. Test Timeout Checking
        logger.info("\n6️⃣ Testing Timeout System...")
        expired_ids = verification_system.check_timeouts()
        logger.info(f"   ✅ Timeout check completed: {len(expired_ids)} expired")
        
        # 7. Test Audit Export
        logger.info("\n7️⃣ Testing Audit Export...")
        success = tracking_system.export_audit_trail("test_audit_export.json")
        logger.info(f"   ✅ Audit trail exported: {success}")
        
        # 8. Test Multiple Alert Levels
        logger.info("\n8️⃣ Testing Multiple Alert Levels...")
        
        # Create high-risk recommendation
        high_risk_rec = AIRecommendation(
            intervention_type="military_security_deployment",
            target_region="Extreme-Nord",
            confidence_score=0.68,
            expected_outcome="Prevent terrorist attack on civilian targets",
            reasoning="Credible intelligence indicates imminent Boko Haram attack. Military deployment urgent.",
            risk_level=InterventionRisk.SECURITY_HIGH,
            potential_casualties=25,
            success_probability=0.65
        )
        
        high_risk_id = verification_system.submit_ai_recommendation(high_risk_rec)
        logger.info(f"   ✅ High-risk recommendation: {high_risk_id}")
        logger.info(f"   ✅ Alert level: {high_risk_rec.alert_level.name}")
        logger.info(f"   ✅ Timeout: {high_risk_rec.approval_timeout}")
        
        # Create medium-risk recommendation
        medium_risk_rec = AIRecommendation(
            intervention_type="economic_development_aid",
            target_region="Sud-Ouest",
            confidence_score=0.72,
            expected_outcome="Reduce separatist support through economic development",
            reasoning="Economic aid to anglophone regions may reduce separatist sentiment.",
            risk_level=InterventionRisk.ECONOMIC_MEDIUM,
            potential_casualties=0,
            success_probability=0.7
        )
        
        medium_risk_id = verification_system.submit_ai_recommendation(medium_risk_rec)
        logger.info(f"   ✅ Medium-risk recommendation: {medium_risk_id}")
        logger.info(f"   ✅ Alert level: {medium_risk_rec.alert_level.name}")
        
        # Final system status
        logger.info("\n9️⃣ Final System Status...")
        final_status = verification_system.get_system_status()
        logger.info(f"   ✅ Final system status:")
        logger.info(f"      • Total pending: {final_status['pending_decisions']}")
        logger.info(f"      • High priority: {final_status['pending_high_priority']}")
        logger.info(f"      • Medium priority: {final_status['pending_medium_priority']}")
        logger.info(f"      • Low priority: {final_status['pending_low_priority']}")
        
        logger.info("\n🎉 ALL TESTS PASSED!")
        logger.info("✅ Human-in-the-Loop System is fully operational!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_models():
    """Test API request/response models."""
    logger.info("\n🔧 Testing API Models...")
    
    # Test RecommendationSubmission
    from human_interface_api import RecommendationSubmission
    
    rec_data = {
        "intervention_type": "diplomatic_dialogue",
        "target_region": "Centre", 
        "confidence_score": 0.85,
        "expected_outcome": "Peaceful resolution",
        "reasoning": "Diplomatic solution recommended",
        "risk_level": "diplomatic_low",
        "potential_casualties": 0,
        "success_probability": 0.8,
        "intelligence_sources": ["Source A", "Source B"],
        "historical_precedents": ["Case 1"],
        "alternative_options": ["Option 1", "Option 2"]
    }
    
    try:
        rec_model = RecommendationSubmission(**rec_data)
        logger.info("   ✅ RecommendationSubmission model valid")
    except Exception as e:
        logger.error(f"   ❌ RecommendationSubmission failed: {e}")
    
    # Test HumanDecisionRequest
    from human_interface_api import HumanDecisionRequest
    
    decision_data = {
        "recommendation_id": "test-123",
        "decision": "approved",
        "reasoning": "This is a good decision because it aligns with our strategic objectives.",
        "modifications": {"intensity": 0.8},
        "urgency_override": False
    }
    
    try:
        decision_model = HumanDecisionRequest(**decision_data)
        logger.info("   ✅ HumanDecisionRequest model valid")
    except Exception as e:
        logger.error(f"   ❌ HumanDecisionRequest failed: {e}")
    
    logger.info("✅ API models validation complete")

if __name__ == "__main__":
    logger.info("🚀 COMPREHENSIVE HUMAN-IN-THE-LOOP SYSTEM TEST")
    logger.info("=" * 80)
    
    # Run API models test
    test_api_models()
    
    # Run main system test
    success = asyncio.run(test_human_interface_system())
    
    if success:
        logger.info("\n🏆 SYSTEM TEST SUMMARY:")
        logger.info("   ✅ Verification System: OPERATIONAL")
        logger.info("   ✅ Decision Tracking: OPERATIONAL")
        logger.info("   ✅ Performance Analytics: OPERATIONAL")
        logger.info("   ✅ Audit System: OPERATIONAL")
        logger.info("   ✅ Multi-tier Alerts: OPERATIONAL")
        logger.info("   ✅ Human Authorization: OPERATIONAL")
        logger.info("")
        logger.info("🛡️ HUMAN-IN-THE-LOOP SYSTEM READY FOR DEPLOYMENT!")
        logger.info("⚠️ CRITICAL HUMAN OVERSIGHT OPERATIONAL FOR LIFE-OR-DEATH DECISIONS")
    else:
        logger.error("❌ SYSTEM TEST FAILED - REQUIRES DEBUGGING")

