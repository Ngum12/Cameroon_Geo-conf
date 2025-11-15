"""
PROJECT SENTINEL - DECISION SUPPORT FRAMEWORK
Cameroon Defense Force RL System for Optimal Conflict Intervention

This module implements the core decision support framework including:
- State space definition (regional conditions, resources, history)  
- Action space design (20+ intervention types)
- Reward function design (conflict prevention success)
- Environment simulation for training
- Historical outcome analysis
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Union
from enum import Enum, IntEnum
import json
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RegionCode(IntEnum):
    """Cameroon regions mapped to integer codes."""
    CENTRE = 0
    LITTORAL = 1
    SUD_OUEST = 2
    NORD_OUEST = 3
    EXTREME_NORD = 4
    NORD = 5
    ADAMAOUA = 6
    EST = 7
    SUD = 8
    OUEST = 9

class InterventionType(Enum):
    """Types of interventions available to the system."""
    # DIPLOMATIC INTERVENTIONS
    DIALOGUE_INITIATION = "diplomatic_dialogue"
    MEDIATION_DEPLOYMENT = "diplomatic_mediation"
    INTERNATIONAL_ENGAGEMENT = "diplomatic_international"
    TRADITIONAL_LEADER_OUTREACH = "diplomatic_traditional"
    
    # MILITARY INTERVENTIONS
    SECURITY_DEPLOYMENT = "military_deployment"
    PATROL_INCREASE = "military_patrol"
    INTELLIGENCE_OPERATION = "military_intelligence"
    BORDER_REINFORCEMENT = "military_border"
    PEACEKEEPING_MISSION = "military_peacekeeping"
    
    # ECONOMIC INTERVENTIONS
    DEVELOPMENT_AID = "economic_aid"
    INFRASTRUCTURE_PROJECT = "economic_infrastructure"
    EMPLOYMENT_PROGRAM = "economic_employment"
    SANCTIONS_TARGETED = "economic_sanctions"
    TRADE_INCENTIVES = "economic_trade"
    
    # SOCIAL INTERVENTIONS
    MEDIA_CAMPAIGN = "social_media"
    COMMUNITY_ENGAGEMENT = "social_community"
    EDUCATION_PROGRAM = "social_education"
    CULTURAL_EVENTS = "social_cultural"
    YOUTH_PROGRAMS = "social_youth"
    
    # EMERGENCY INTERVENTIONS
    HUMANITARIAN_AID = "emergency_humanitarian"
    EVACUATION_SUPPORT = "emergency_evacuation"
    CRISIS_COMMUNICATION = "emergency_communication"
    
    # NO ACTION
    MONITOR_ONLY = "no_action"

class ThreatLevel(IntEnum):
    """Threat levels for different regions."""
    PEACEFUL = 0      # No current threats
    LOW_RISK = 1      # Minor tensions
    MEDIUM_RISK = 2   # Escalating situation
    HIGH_RISK = 3     # Active conflict likely
    CRITICAL = 4      # Imminent violent conflict

@dataclass
class RegionalState:
    """Represents the current state of a specific region."""
    region_id: int
    region_name: str
    
    # HISTORICAL CONTEXT
    historical_conflict_count: int = 0
    days_since_last_incident: int = 365
    total_historical_fatalities: int = 0
    avg_incident_severity: float = 0.0
    
    # CURRENT THREAT INDICATORS
    threat_level: int = ThreatLevel.PEACEFUL
    conflict_probability_7d: float = 0.0
    conflict_probability_30d: float = 0.0
    conflict_probability_90d: float = 0.0
    
    # ACTOR PRESENCE
    government_presence: float = 1.0  # 0-1 scale
    boko_haram_activity: float = 0.0
    separatist_activity: float = 0.0
    foreign_actor_presence: float = 0.0
    
    # SOCIOECONOMIC CONDITIONS
    economic_stability: float = 0.5  # 0-1 scale
    education_level: float = 0.5
    unemployment_rate: float = 0.3
    infrastructure_quality: float = 0.5
    
    # GEOGRAPHIC FACTORS
    is_border_region: bool = False
    distance_to_capital: float = 0.0
    population_density: float = 0.0
    
    # SEASONAL FACTORS
    is_dry_season: bool = False
    is_election_period: bool = False
    
    # RESOURCE AVAILABILITY
    military_resources: float = 1.0  # Available military capacity (0-1)
    diplomatic_resources: float = 1.0  # Available diplomatic capacity
    economic_resources: float = 1.0   # Available economic resources
    
    # RECENT INTERVENTIONS (last 30 days)
    recent_military_actions: int = 0
    recent_diplomatic_actions: int = 0
    recent_economic_actions: int = 0
    recent_social_actions: int = 0
    
    def to_array(self) -> np.ndarray:
        """Convert state to numpy array for ML models."""
        return np.array([
            self.region_id,
            self.historical_conflict_count,
            self.days_since_last_incident,
            self.total_historical_fatalities,
            self.avg_incident_severity,
            self.threat_level,
            self.conflict_probability_7d,
            self.conflict_probability_30d,
            self.conflict_probability_90d,
            self.government_presence,
            self.boko_haram_activity,
            self.separatist_activity,
            self.foreign_actor_presence,
            self.economic_stability,
            self.education_level,
            self.unemployment_rate,
            self.infrastructure_quality,
            int(self.is_border_region),
            self.distance_to_capital,
            self.population_density,
            int(self.is_dry_season),
            int(self.is_election_period),
            self.military_resources,
            self.diplomatic_resources,
            self.economic_resources,
            self.recent_military_actions,
            self.recent_diplomatic_actions,
            self.recent_economic_actions,
            self.recent_social_actions
        ], dtype=np.float32)
    
    @classmethod
    def get_state_size(cls) -> int:
        """Get the size of the state vector."""
        return 29

@dataclass
class InterventionAction:
    """Represents a specific intervention action."""
    intervention_type: InterventionType
    target_region: int
    intensity: float = 1.0  # 0.0-1.0 scale
    duration: int = 7  # days
    resources_required: float = 1.0  # 0.0-1.0 scale of total capacity
    
    # Intervention-specific parameters
    diplomatic_level: str = "local"  # local, national, international
    military_scale: str = "small"    # small, medium, large
    economic_amount: float = 0.0     # in millions USD equivalent
    social_reach: int = 1000         # estimated people reached
    
    def to_array(self) -> np.ndarray:
        """Convert action to numpy array."""
        # Map intervention type to integer
        intervention_id = list(InterventionType).index(self.intervention_type)
        
        # Map categorical variables to integers
        diplomatic_levels = {"local": 0, "national": 1, "international": 2}
        military_scales = {"small": 0, "medium": 1, "large": 2}
        
        return np.array([
            intervention_id,
            self.target_region,
            self.intensity,
            self.duration,
            self.resources_required,
            diplomatic_levels.get(self.diplomatic_level, 0),
            military_scales.get(self.military_scale, 0),
            self.economic_amount,
            self.social_reach
        ], dtype=np.float32)
    
    @classmethod
    def get_action_size(cls) -> int:
        """Get the size of the action vector."""
        return 9

class ConflictEnvironment:
    """Simulation environment for conflict prevention RL."""
    
    def __init__(self, historical_data_path: str = "../ml-models/cameroon_events_ml_ready.json"):
        self.historical_data_path = historical_data_path
        self.regions = {}
        self.current_step = 0
        self.max_steps = 365  # One year simulation
        self.start_date = datetime(2024, 1, 1)
        
        # Load historical data for initialization
        self.historical_events = self._load_historical_data()
        
        # Initialize regional states
        self._initialize_regions()
        
        # Action space: 24 intervention types × 10 regions = 240 possible actions
        self.action_space_size = len(InterventionType) * len(RegionCode)
        self.state_space_size = RegionalState.get_state_size() * len(RegionCode)  # All regions combined
        
        logger.info(f"🌍 Environment initialized:")
        logger.info(f"   • Regions: {len(self.regions)}")
        logger.info(f"   • Historical events: {len(self.historical_events)}")
        logger.info(f"   • Action space size: {self.action_space_size}")
        logger.info(f"   • State space size: {self.state_space_size}")
    
    def _load_historical_data(self) -> List[Dict[str, Any]]:
        """Load historical conflict events."""
        try:
            with open(self.historical_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            events = data.get('events', [])
            logger.info(f"📊 Loaded {len(events)} historical events")
            return events
        except Exception as e:
            logger.warning(f"⚠️ Could not load historical data: {e}")
            return []
    
    def _initialize_regions(self):
        """Initialize all regional states based on historical data."""
        region_names = {
            0: "Centre", 1: "Littoral", 2: "Sud-Ouest", 3: "Nord-Ouest",
            4: "Extreme-Nord", 5: "Nord", 6: "Adamaoua", 7: "Est",
            8: "Sud", 9: "Ouest"
        }
        
        # Calculate historical statistics per region
        region_stats = self._calculate_regional_statistics()
        
        for region_id, name in region_names.items():
            stats = region_stats.get(name, {})
            
            self.regions[region_id] = RegionalState(
                region_id=region_id,
                region_name=name,
                historical_conflict_count=stats.get('event_count', 0),
                total_historical_fatalities=stats.get('total_fatalities', 0),
                avg_incident_severity=stats.get('avg_severity', 0.0),
                threat_level=self._calculate_initial_threat_level(stats),
                is_border_region=region_id in [4, 5, 2, 3, 7],  # Border regions
                distance_to_capital=self._calculate_distance_to_capital(region_id),
                government_presence=0.9 if region_id == 0 else 0.7,  # Higher in Centre
                boko_haram_activity=0.8 if region_id == 4 else 0.1,  # Higher in Extreme-Nord
                separatist_activity=0.6 if region_id in [2, 3] else 0.1,  # Higher in anglophone regions
            )
    
    def _calculate_regional_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Calculate historical statistics for each region."""
        region_stats = {}
        
        if not self.historical_events:
            return region_stats
        
        # Group events by region
        for event in self.historical_events:
            region = event.get('admin1', 'Unknown')
            if region not in region_stats:
                region_stats[region] = {
                    'event_count': 0,
                    'total_fatalities': 0,
                    'severities': []
                }
            
            region_stats[region]['event_count'] += 1
            region_stats[region]['total_fatalities'] += event.get('fatalities', 0)
            region_stats[region]['severities'].append(event.get('severity_score', 0))
        
        # Calculate averages
        for region, stats in region_stats.items():
            if stats['severities']:
                stats['avg_severity'] = np.mean(stats['severities'])
            else:
                stats['avg_severity'] = 0.0
        
        return region_stats
    
    def _calculate_initial_threat_level(self, stats: Dict[str, Any]) -> int:
        """Calculate initial threat level based on historical data."""
        event_count = stats.get('event_count', 0)
        avg_severity = stats.get('avg_severity', 0.0)
        
        # Threat level based on historical activity
        if event_count > 100 and avg_severity > 70:
            return ThreatLevel.HIGH_RISK
        elif event_count > 50 and avg_severity > 50:
            return ThreatLevel.MEDIUM_RISK
        elif event_count > 20:
            return ThreatLevel.LOW_RISK
        else:
            return ThreatLevel.PEACEFUL
    
    def _calculate_distance_to_capital(self, region_id: int) -> float:
        """Calculate approximate distance to Yaoundé (Centre region)."""
        # Simplified distance calculation (could use actual coordinates)
        distances = {0: 0.0, 1: 1.0, 2: 3.0, 3: 2.5, 4: 7.0, 5: 5.0, 6: 3.5, 7: 4.0, 8: 2.0, 9: 1.5}
        return distances.get(region_id, 3.0)
    
    def get_state(self) -> np.ndarray:
        """Get current state of all regions."""
        state_vectors = []
        for region_id in sorted(self.regions.keys()):
            state_vectors.append(self.regions[region_id].to_array())
        return np.concatenate(state_vectors)
    
    def step(self, action_id: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """Take an action in the environment and return new state, reward, done, info."""
        # Decode action
        intervention_type_id = action_id // len(RegionCode)
        target_region = action_id % len(RegionCode)
        
        intervention_type = list(InterventionType)[intervention_type_id]
        
        # Create action object
        action = InterventionAction(
            intervention_type=intervention_type,
            target_region=target_region,
            intensity=np.random.uniform(0.5, 1.0),  # Random intensity for now
            duration=7  # One week intervention
        )
        
        # Apply intervention effects
        reward = self._apply_intervention(action)
        
        # Update environment state
        self._update_environment()
        
        # Check if episode is done
        self.current_step += 1
        done = self.current_step >= self.max_steps
        
        # Collect info
        info = {
            'step': self.current_step,
            'intervention': intervention_type.value,
            'target_region': target_region,
            'reward': reward,
            'total_conflicts': sum(1 for r in self.regions.values() if r.threat_level >= ThreatLevel.HIGH_RISK)
        }
        
        return self.get_state(), reward, done, info
    
    def _apply_intervention(self, action: InterventionAction) -> float:
        """Apply intervention and calculate reward."""
        target_region = self.regions[action.target_region]
        initial_threat = target_region.threat_level
        
        # Apply intervention effects based on type
        if action.intervention_type in [InterventionType.DIALOGUE_INITIATION, 
                                       InterventionType.MEDIATION_DEPLOYMENT,
                                       InterventionType.TRADITIONAL_LEADER_OUTREACH]:
            # Diplomatic interventions reduce tensions
            target_region.threat_level = max(0, target_region.threat_level - 1)
            target_region.recent_diplomatic_actions += 1
            effectiveness = 0.7  # Diplomatic interventions are moderately effective
            
        elif action.intervention_type in [InterventionType.SECURITY_DEPLOYMENT,
                                         InterventionType.PATROL_INCREASE,
                                         InterventionType.BORDER_REINFORCEMENT]:
            # Military interventions provide immediate security but may increase tensions
            if target_region.threat_level >= ThreatLevel.HIGH_RISK:
                target_region.threat_level = max(1, target_region.threat_level - 2)  # Effective against high threats
                effectiveness = 0.8
            else:
                target_region.threat_level = min(4, target_region.threat_level + 1)  # May increase tensions in peaceful areas
                effectiveness = 0.3
            target_region.recent_military_actions += 1
            
        elif action.intervention_type in [InterventionType.DEVELOPMENT_AID,
                                         InterventionType.INFRASTRUCTURE_PROJECT,
                                         InterventionType.EMPLOYMENT_PROGRAM]:
            # Economic interventions improve long-term stability
            target_region.economic_stability = min(1.0, target_region.economic_stability + 0.1)
            target_region.threat_level = max(0, target_region.threat_level - 1)
            target_region.recent_economic_actions += 1
            effectiveness = 0.6  # Long-term effectiveness
            
        elif action.intervention_type in [InterventionType.COMMUNITY_ENGAGEMENT,
                                         InterventionType.EDUCATION_PROGRAM,
                                         InterventionType.YOUTH_PROGRAMS]:
            # Social interventions build community resilience
            target_region.education_level = min(1.0, target_region.education_level + 0.05)
            target_region.threat_level = max(0, target_region.threat_level - 1)
            target_region.recent_social_actions += 1
            effectiveness = 0.5  # Gradual effectiveness
            
        else:
            # Monitor only or other actions
            effectiveness = 0.1
        
        # Calculate reward based on threat reduction and intervention cost
        threat_reduction = initial_threat - target_region.threat_level
        intervention_cost = action.resources_required * action.intensity
        
        # Reward formula: threat reduction benefit - intervention cost + stability bonus
        reward = (threat_reduction * 10.0) - (intervention_cost * 2.0)
        
        # Bonus for maintaining peaceful regions
        if target_region.threat_level == ThreatLevel.PEACEFUL:
            reward += 5.0
        
        # Penalty for conflicts in critical regions (border areas, major cities)
        if target_region.is_border_region and target_region.threat_level >= ThreatLevel.HIGH_RISK:
            reward -= 10.0
        
        return reward * effectiveness
    
    def _update_environment(self):
        """Update the environment state (simulate natural progression)."""
        current_date = self.start_date + timedelta(days=self.current_step)
        
        for region in self.regions.values():
            # Natural decay of intervention effects
            region.recent_military_actions = max(0, region.recent_military_actions - 1)
            region.recent_diplomatic_actions = max(0, region.recent_diplomatic_actions - 1)
            region.recent_economic_actions = max(0, region.recent_economic_actions - 1)
            region.recent_social_actions = max(0, region.recent_social_actions - 1)
            
            # Random events (simplified)
            if np.random.random() < 0.01:  # 1% chance of random incident
                region.threat_level = min(4, region.threat_level + 1)
                region.days_since_last_incident = 0
            else:
                region.days_since_last_incident += 1
            
            # Seasonal effects
            region.is_dry_season = current_date.month in [11, 12, 1, 2, 3, 4]
            
            # Gradual threat level changes based on regional factors
            threat_change_prob = 0.05  # 5% daily chance of change
            if np.random.random() < threat_change_prob:
                # Higher instability in regions with active non-state actors
                if region.boko_haram_activity > 0.5 or region.separatist_activity > 0.5:
                    region.threat_level = min(4, region.threat_level + 1)
                elif region.government_presence > 0.8 and region.economic_stability > 0.6:
                    region.threat_level = max(0, region.threat_level - 1)
    
    def reset(self) -> np.ndarray:
        """Reset environment to initial state."""
        self.current_step = 0
        self._initialize_regions()
        return self.get_state()
    
    def render(self) -> str:
        """Render current environment state."""
        output = f"🌍 CAMEROON CONFLICT ENVIRONMENT - Day {self.current_step}\n"
        output += "=" * 60 + "\n"
        
        for region_id, region in self.regions.items():
            threat_emoji = ["🟢", "🟡", "🟠", "🔴", "💀"][region.threat_level]
            output += f"{threat_emoji} {region.region_name:12} | Threat: {region.threat_level} | "
            output += f"Conflicts: {region.historical_conflict_count:3d} | "
            output += f"Gov: {region.government_presence:.1f} | "
            output += f"Econ: {region.economic_stability:.1f}\n"
        
        total_high_risk = sum(1 for r in self.regions.values() if r.threat_level >= ThreatLevel.HIGH_RISK)
        output += f"\n🚨 High-risk regions: {total_high_risk}/10\n"
        
        return output

def create_reward_function() -> callable:
    """Create reward function for conflict prevention RL."""
    
    def reward_function(initial_state: np.ndarray, 
                       action: InterventionAction, 
                       final_state: np.ndarray, 
                       intervention_success: bool) -> float:
        """
        Calculate reward for a conflict prevention intervention.
        
        Reward components:
        1. Conflict prevention success: +50 to +100
        2. Resource efficiency: -1 to -10 (cost of intervention)
        3. Stability maintenance: +5 per peaceful region
        4. Critical region protection: +20 for protecting border/major regions
        5. Timing bonus: +10 for early intervention (before escalation)
        """
        
        reward = 0.0
        
        # 1. Conflict prevention success
        if intervention_success:
            reward += 75.0  # Major reward for preventing conflict
        
        # 2. Resource efficiency penalty
        cost_penalty = action.resources_required * action.intensity * 5.0
        reward -= cost_penalty
        
        # 3. Stability maintenance bonus
        # This would be calculated based on state analysis
        stability_bonus = 5.0  # Simplified
        reward += stability_bonus
        
        # 4. Critical region protection
        if action.target_region in [4, 2, 3]:  # Extreme-Nord, Sud-Ouest, Nord-Ouest
            reward += 20.0
        
        # 5. Timing bonus (early intervention)
        if action.intervention_type in [InterventionType.DIALOGUE_INITIATION, 
                                       InterventionType.MEDIATION_DEPLOYMENT]:
            reward += 10.0  # Bonus for diplomatic solutions
        
        return reward
    
    return reward_function

# Main demonstration
if __name__ == "__main__":
    logger.info("🚀 PROJECT SENTINEL - DECISION SUPPORT FRAMEWORK DEMO")
    logger.info("=" * 60)
    
    # Create environment
    env = ConflictEnvironment()
    
    # Display initial state
    print(env.render())
    
    # Demonstrate some interventions
    logger.info("\n🎯 TESTING INTERVENTIONS:")
    
    test_actions = [
        0,   # Diplomatic dialogue in Centre
        25,  # Security deployment in Sud-Ouest  
        50,  # Development aid in Extreme-Nord
        100  # Community engagement in Nord
    ]
    
    for i, action_id in enumerate(test_actions):
        logger.info(f"\n--- Intervention {i+1} ---")
        state, reward, done, info = env.step(action_id)
        logger.info(f"Action: {info['intervention']} in region {info['target_region']}")
        logger.info(f"Reward: {reward:.2f}")
        logger.info(f"High-risk regions: {info['total_conflicts']}")
    
    print("\n" + env.render())
    
    logger.info("✅ Decision Support Framework initialized successfully!")
    logger.info(f"📊 State space: {env.state_space_size} dimensions")
    logger.info(f"🎯 Action space: {env.action_space_size} possible actions")
    logger.info(f"🏆 Reward function: Multi-objective optimization ready")

