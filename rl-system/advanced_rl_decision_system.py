#!/usr/bin/env python3
"""
ADVANCED REINFORCEMENT LEARNING DECISION SUPPORT SYSTEM
Project Sentinel - Cameroon Defense Force OSINT Analysis System

This system provides AI-powered decision support for conflict prevention
and crisis intervention using reinforcement learning algorithms.

CLASSIFICATION: RESTRICTED - CAMEROON DEFENSE FORCE
NO GPU REQUIRED - OPTIMIZED FOR CPU-ONLY DEPLOYMENT
"""

import numpy as np
import pandas as pd
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import joblib
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterventionType(Enum):
    """Types of interventions available to the Cameroon Defense Force"""
    
    # DIPLOMATIC INTERVENTIONS
    DIPLOMATIC_DIALOGUE = "diplomatic_dialogue"
    MEDIATION_LOCAL_CHIEFS = "mediation_local_chiefs" 
    INTERNATIONAL_ENGAGEMENT = "international_engagement"
    PEACE_NEGOTIATIONS = "peace_negotiations"
    
    # MILITARY INTERVENTIONS
    PREVENTIVE_DEPLOYMENT = "preventive_deployment"
    SECURITY_PATROLS = "security_patrols"
    INTELLIGENCE_OPERATIONS = "intelligence_operations"
    COUNTER_TERRORISM = "counter_terrorism"
    BORDER_REINFORCEMENT = "border_reinforcement"
    
    # ECONOMIC INTERVENTIONS
    DEVELOPMENT_PROJECTS = "development_projects"
    ECONOMIC_INCENTIVES = "economic_incentives"
    INFRASTRUCTURE_INVESTMENT = "infrastructure_investment"
    TRADE_FACILITATION = "trade_facilitation"
    
    # SOCIAL INTERVENTIONS
    COMMUNITY_ENGAGEMENT = "community_engagement"
    MEDIA_CAMPAIGNS = "media_campaigns"
    EDUCATION_PROGRAMS = "education_programs"
    YOUTH_PROGRAMS = "youth_programs"
    HUMANITARIAN_AID = "humanitarian_aid"
    
    # ADMINISTRATIVE INTERVENTIONS
    GOVERNANCE_REFORM = "governance_reform"
    JUDICIAL_INTERVENTION = "judicial_intervention"
    ADMINISTRATIVE_MEASURES = "administrative_measures"

class ThreatLevel(Enum):
    """Threat level classifications"""
    CRITICAL = "critical"      # 80-100%
    HIGH = "high"             # 60-79%
    MEDIUM = "medium"         # 40-59%
    LOW = "low"               # 20-39%
    MINIMAL = "minimal"       # 0-19%

@dataclass
class RegionalState:
    """Represents the current state of a Cameroon region"""
    region_name: str
    population: int
    threat_level: float  # 0-100
    economic_stability: float  # 0-100
    political_stability: float  # 0-100
    security_presence: float  # 0-100
    recent_incidents: int
    unemployment_rate: float
    infrastructure_quality: float  # 0-100
    cross_border_activity: float  # 0-100
    ethnic_tensions: float  # 0-100
    resource_conflicts: float  # 0-100
    boko_haram_activity: float  # 0-100 (for northern regions)
    separatist_activity: float  # 0-100 (for anglophone regions)
    
    def to_feature_vector(self) -> np.ndarray:
        """Convert state to feature vector for ML processing"""
        return np.array([
            self.threat_level, self.economic_stability, self.political_stability,
            self.security_presence, self.recent_incidents, self.unemployment_rate,
            self.infrastructure_quality, self.cross_border_activity, self.ethnic_tensions,
            self.resource_conflicts, self.boko_haram_activity, self.separatist_activity
        ])

@dataclass
class InterventionAction:
    """Represents a specific intervention action"""
    intervention_type: InterventionType
    region: str
    intensity: float  # 0-100 (resource allocation intensity)
    duration_days: int
    cost_estimate: float  # in XAF (Central African CFA francs)
    personnel_required: int
    risk_level: float  # 0-100
    expected_effectiveness: float  # 0-100
    
class CameroonRegionDatabase:
    """Database of Cameroon regions with realistic baseline data"""
    
    REGIONS_DATA = {
        "Extreme-Nord": {
            "population": 4000000,
            "baseline_threat": 75.0,  # High due to Boko Haram
            "economic_stability": 35.0,  # Poor economic conditions
            "political_stability": 60.0,
            "security_presence": 85.0,  # Heavy military presence
            "unemployment_rate": 45.0,
            "infrastructure_quality": 25.0,  # Poor infrastructure
            "cross_border_activity": 95.0,  # High Nigeria/Chad border activity
            "ethnic_tensions": 40.0,
            "resource_conflicts": 60.0,
            "boko_haram_activity": 85.0,  # Very high
            "separatist_activity": 5.0
        },
        "Nord": {
            "population": 2500000,
            "baseline_threat": 45.0,
            "economic_stability": 50.0,
            "political_stability": 70.0,
            "security_presence": 65.0,
            "unemployment_rate": 35.0,
            "infrastructure_quality": 40.0,
            "cross_border_activity": 70.0,
            "ethnic_tensions": 55.0,
            "resource_conflicts": 65.0,  # Farmer-herder conflicts
            "boko_haram_activity": 25.0,
            "separatist_activity": 5.0
        },
        "Adamaoua": {
            "population": 1200000,
            "baseline_threat": 35.0,
            "economic_stability": 55.0,
            "political_stability": 75.0,
            "security_presence": 50.0,
            "unemployment_rate": 30.0,
            "infrastructure_quality": 45.0,
            "cross_border_activity": 40.0,
            "ethnic_tensions": 45.0,
            "resource_conflicts": 70.0,  # Farmer-herder conflicts
            "boko_haram_activity": 10.0,
            "separatist_activity": 5.0
        },
        "Est": {
            "population": 1000000,
            "baseline_threat": 55.0,
            "economic_stability": 45.0,
            "political_stability": 65.0,
            "security_presence": 60.0,
            "unemployment_rate": 40.0,
            "infrastructure_quality": 35.0,
            "cross_border_activity": 85.0,  # CAR border issues
            "ethnic_tensions": 35.0,
            "resource_conflicts": 50.0,
            "boko_haram_activity": 5.0,
            "separatist_activity": 5.0
        },
        "Centre": {
            "population": 4500000,
            "baseline_threat": 25.0,
            "economic_stability": 75.0,
            "political_stability": 80.0,
            "security_presence": 90.0,  # Capital region
            "unemployment_rate": 20.0,
            "infrastructure_quality": 80.0,
            "cross_border_activity": 25.0,
            "ethnic_tensions": 25.0,
            "resource_conflicts": 20.0,
            "boko_haram_activity": 5.0,
            "separatist_activity": 5.0
        },
        "Sud": {
            "population": 800000,
            "baseline_threat": 25.0,
            "economic_stability": 60.0,
            "political_stability": 75.0,
            "security_presence": 55.0,
            "unemployment_rate": 25.0,
            "infrastructure_quality": 50.0,
            "cross_border_activity": 45.0,
            "ethnic_tensions": 20.0,
            "resource_conflicts": 30.0,
            "boko_haram_activity": 5.0,
            "separatist_activity": 5.0
        },
        "Littoral": {
            "population": 3500000,
            "baseline_threat": 30.0,
            "economic_stability": 80.0,  # Economic hub
            "political_stability": 75.0,
            "security_presence": 85.0,
            "unemployment_rate": 18.0,
            "infrastructure_quality": 85.0,
            "cross_border_activity": 60.0,  # Port activities
            "ethnic_tensions": 30.0,
            "resource_conflicts": 25.0,
            "boko_haram_activity": 5.0,
            "separatist_activity": 5.0
        },
        "Ouest": {
            "population": 2000000,
            "baseline_threat": 30.0,
            "economic_stability": 65.0,
            "political_stability": 70.0,
            "security_presence": 60.0,
            "unemployment_rate": 25.0,
            "infrastructure_quality": 60.0,
            "cross_border_activity": 30.0,
            "ethnic_tensions": 35.0,
            "resource_conflicts": 40.0,
            "boko_haram_activity": 5.0,
            "separatist_activity": 10.0
        },
        "Nord-Ouest": {
            "population": 2200000,
            "baseline_threat": 70.0,  # Anglophone crisis
            "economic_stability": 35.0,
            "political_stability": 30.0,  # Very unstable
            "security_presence": 80.0,  # Heavy military presence
            "unemployment_rate": 50.0,
            "infrastructure_quality": 35.0,
            "cross_border_activity": 60.0,
            "ethnic_tensions": 80.0,  # High anglophone tensions
            "resource_conflicts": 45.0,
            "boko_haram_activity": 5.0,
            "separatist_activity": 85.0  # Very high
        },
        "Sud-Ouest": {
            "population": 1500000,
            "baseline_threat": 65.0,  # Anglophone crisis
            "economic_stability": 40.0,
            "political_stability": 35.0,
            "security_presence": 75.0,
            "unemployment_rate": 45.0,
            "infrastructure_quality": 40.0,
            "cross_border_activity": 55.0,
            "ethnic_tensions": 75.0,  # High anglophone tensions
            "resource_conflicts": 40.0,
            "boko_haram_activity": 5.0,
            "separatist_activity": 80.0  # Very high
        }
    }

class AdvancedRLDecisionSystem:
    """
    Advanced Reinforcement Learning Decision Support System
    CPU-optimized for real-time defense operations
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.effectiveness_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.risk_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.cost_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        
        # Load historical intervention data for training
        self._initialize_models()
        
        # Intervention effectiveness database (historical/expert knowledge)
        self.intervention_effectiveness = self._load_intervention_effectiveness_data()
        
    def _initialize_models(self):
        """Initialize and train the ML models with historical data"""
        logger.info("🤖 Initializing RL Decision Support Models...")
        
        # Generate synthetic training data based on historical patterns
        training_data = self._generate_training_data()
        
        X = training_data['features']
        y_effectiveness = training_data['effectiveness']
        y_risk = training_data['risk']
        y_cost = training_data['cost']
        
        # Fit the scaler and models
        X_scaled = self.scaler.fit_transform(X)
        
        self.effectiveness_predictor.fit(X_scaled, y_effectiveness)
        self.risk_predictor.fit(X_scaled, y_risk)
        self.cost_predictor.fit(X_scaled, y_cost)
        
        logger.info("✅ RL Models trained successfully")
    
    def _generate_training_data(self) -> Dict[str, np.ndarray]:
        """Generate training data from historical intervention outcomes"""
        np.random.seed(42)  # For reproducibility
        
        n_samples = 10000
        features = []
        effectiveness = []
        risk = []
        cost = []
        
        for _ in range(n_samples):
            # Generate random regional state
            threat_level = np.random.uniform(0, 100)
            economic_stability = np.random.uniform(20, 90)
            political_stability = np.random.uniform(10, 95)
            security_presence = np.random.uniform(30, 95)
            recent_incidents = np.random.randint(0, 20)
            unemployment_rate = np.random.uniform(10, 60)
            infrastructure_quality = np.random.uniform(20, 90)
            cross_border_activity = np.random.uniform(10, 95)
            ethnic_tensions = np.random.uniform(10, 90)
            resource_conflicts = np.random.uniform(10, 80)
            boko_haram_activity = np.random.uniform(0, 95)
            separatist_activity = np.random.uniform(0, 90)
            
            # Intervention parameters
            intervention_intensity = np.random.uniform(20, 100)
            intervention_duration = np.random.randint(7, 365)
            personnel_required = np.random.randint(50, 5000)
            
            feature_vector = np.array([
                threat_level, economic_stability, political_stability,
                security_presence, recent_incidents, unemployment_rate,
                infrastructure_quality, cross_border_activity, ethnic_tensions,
                resource_conflicts, boko_haram_activity, separatist_activity,
                intervention_intensity, intervention_duration, personnel_required
            ])
            
            # Calculate outcomes based on realistic relationships
            effectiveness_score = self._calculate_synthetic_effectiveness(
                threat_level, economic_stability, political_stability, 
                intervention_intensity, intervention_duration
            )
            
            risk_score = self._calculate_synthetic_risk(
                threat_level, security_presence, intervention_intensity, 
                ethnic_tensions, cross_border_activity
            )
            
            cost_score = self._calculate_synthetic_cost(
                intervention_intensity, intervention_duration, personnel_required
            )
            
            features.append(feature_vector)
            effectiveness.append(effectiveness_score)
            risk.append(risk_score)
            cost.append(cost_score)
        
        return {
            'features': np.array(features),
            'effectiveness': np.array(effectiveness),
            'risk': np.array(risk),
            'cost': np.array(cost)
        }
    
    def _calculate_synthetic_effectiveness(self, threat_level, economic_stability, 
                                         political_stability, intensity, duration):
        """Calculate synthetic effectiveness score based on realistic relationships"""
        # Higher intensity and duration generally more effective
        base_effectiveness = (intensity * 0.4 + duration/365 * 20) / 2
        
        # Adjust based on regional conditions
        if threat_level > 80:  # Critical threats harder to address
            base_effectiveness *= 0.7
        elif threat_level < 30:  # Low threats easier to address
            base_effectiveness *= 1.3
            
        # Economic and political stability affect success
        stability_factor = (economic_stability + political_stability) / 200
        base_effectiveness = base_effectiveness * (0.5 + stability_factor)
        
        # Add realistic noise
        effectiveness = base_effectiveness + np.random.normal(0, 10)
        return np.clip(effectiveness, 0, 100)
    
    def _calculate_synthetic_risk(self, threat_level, security_presence, 
                                intensity, ethnic_tensions, cross_border_activity):
        """Calculate synthetic risk score"""
        # Higher threat and tensions increase risk
        base_risk = (threat_level * 0.3 + ethnic_tensions * 0.3 + 
                    cross_border_activity * 0.2)
        
        # Higher security presence reduces risk
        base_risk = base_risk * (1 - security_presence/200)
        
        # Higher intervention intensity can increase risk
        base_risk += intensity * 0.1
        
        # Add noise
        risk = base_risk + np.random.normal(0, 5)
        return np.clip(risk, 0, 100)
    
    def _calculate_synthetic_cost(self, intensity, duration, personnel):
        """Calculate synthetic cost in millions of XAF"""
        # Base cost calculation
        daily_cost_per_person = 50000  # 50,000 XAF per person per day
        base_cost = (personnel * daily_cost_per_person * duration) / 1000000  # In millions
        
        # Intensity multiplier for equipment, logistics
        intensity_multiplier = 1 + (intensity - 50) / 100
        total_cost = base_cost * intensity_multiplier
        
        # Add noise
        cost = total_cost + np.random.normal(0, total_cost * 0.2)
        return max(cost, 0.1)  # Minimum cost
    
    def _load_intervention_effectiveness_data(self) -> Dict:
        """Load historical intervention effectiveness data"""
        return {
            InterventionType.DIPLOMATIC_DIALOGUE: {
                "effectiveness_vs_separatist": 65,
                "effectiveness_vs_ethnic_tension": 75,
                "effectiveness_vs_political_instability": 80,
                "effectiveness_vs_terrorism": 25,
                "cost_multiplier": 0.1,
                "risk_level": 15
            },
            InterventionType.COUNTER_TERRORISM: {
                "effectiveness_vs_terrorism": 85,
                "effectiveness_vs_separatist": 45,
                "effectiveness_vs_ethnic_tension": 30,
                "effectiveness_vs_political_instability": 25,
                "cost_multiplier": 5.0,
                "risk_level": 80
            },
            InterventionType.DEVELOPMENT_PROJECTS: {
                "effectiveness_vs_economic_instability": 85,
                "effectiveness_vs_separatist": 70,
                "effectiveness_vs_ethnic_tension": 60,
                "effectiveness_vs_terrorism": 40,
                "cost_multiplier": 10.0,
                "risk_level": 20
            },
            InterventionType.PREVENTIVE_DEPLOYMENT: {
                "effectiveness_vs_ethnic_tension": 80,
                "effectiveness_vs_separatist": 75,
                "effectiveness_vs_terrorism": 70,
                "effectiveness_vs_political_instability": 50,
                "cost_multiplier": 3.0,
                "risk_level": 45
            },
            InterventionType.COMMUNITY_ENGAGEMENT: {
                "effectiveness_vs_ethnic_tension": 85,
                "effectiveness_vs_separatist": 75,
                "effectiveness_vs_political_instability": 65,
                "effectiveness_vs_terrorism": 30,
                "cost_multiplier": 0.5,
                "risk_level": 10
            }
        }
    
    def get_current_regional_state(self, region: str) -> RegionalState:
        """Get current state of a region by fetching real-time data"""
        try:
            # Try to get real data from Django backend
            response = requests.get(f'http://localhost:8000/api/v1/events/?region={region}', 
                                  timeout=5)
            
            if response.status_code == 200:
                events = response.json()
                
                # Calculate dynamic threat level based on recent events
                recent_events = [e for e in events if self._is_recent_event(e)]
                dynamic_threat = self._calculate_dynamic_threat_level(recent_events, region)
                
                # Get baseline data
                baseline = CameroonRegionDatabase.REGIONS_DATA[region]
                
                # Create regional state with real-time updates
                return RegionalState(
                    region_name=region,
                    population=baseline["population"],
                    threat_level=dynamic_threat,
                    economic_stability=baseline["economic_stability"],
                    political_stability=baseline["political_stability"],
                    security_presence=baseline["security_presence"],
                    recent_incidents=len(recent_events),
                    unemployment_rate=baseline["unemployment_rate"],
                    infrastructure_quality=baseline["infrastructure_quality"],
                    cross_border_activity=baseline["cross_border_activity"],
                    ethnic_tensions=baseline["ethnic_tensions"],
                    resource_conflicts=baseline["resource_conflicts"],
                    boko_haram_activity=baseline["boko_haram_activity"],
                    separatist_activity=baseline["separatist_activity"]
                )
            
        except Exception as e:
            logger.warning(f"Could not fetch real-time data for {region}: {e}")
        
        # Fallback to baseline data
        baseline = CameroonRegionDatabase.REGIONS_DATA[region]
        return RegionalState(
            region_name=region,
            population=baseline["population"],
            threat_level=baseline["baseline_threat"],
            economic_stability=baseline["economic_stability"],
            political_stability=baseline["political_stability"],
            security_presence=baseline["security_presence"],
            recent_incidents=0,
            unemployment_rate=baseline["unemployment_rate"],
            infrastructure_quality=baseline["infrastructure_quality"],
            cross_border_activity=baseline["cross_border_activity"],
            ethnic_tensions=baseline["ethnic_tensions"],
            resource_conflicts=baseline["resource_conflicts"],
            boko_haram_activity=baseline["boko_haram_activity"],
            separatist_activity=baseline["separatist_activity"]
        )
    
    def _is_recent_event(self, event: Dict) -> bool:
        """Check if event is from the last 7 days"""
        try:
            event_date = datetime.fromisoformat(event['created_at'].replace('Z', '+00:00'))
            return (datetime.now() - event_date).days <= 7
        except:
            return False
    
    def _calculate_dynamic_threat_level(self, recent_events: List[Dict], region: str) -> float:
        """Calculate dynamic threat level based on recent events"""
        baseline = CameroonRegionDatabase.REGIONS_DATA[region]["baseline_threat"]
        
        if not recent_events:
            return baseline
        
        # Count high-priority events
        high_priority_events = [e for e in recent_events if e.get('priority', 1) >= 3]
        
        # Calculate threat adjustment
        threat_increase = len(high_priority_events) * 5  # +5 per high-priority event
        threat_increase = min(threat_increase, 25)  # Max +25 increase
        
        return min(baseline + threat_increase, 100)
    
    def generate_intervention_recommendations(self, region: str, 
                                            max_interventions: int = 5) -> List[InterventionAction]:
        """Generate top intervention recommendations for a region"""
        logger.info(f"🎯 Generating intervention recommendations for {region}")
        
        # Get current regional state
        regional_state = self.get_current_regional_state(region)
        
        # Generate all possible interventions
        possible_interventions = self._generate_all_interventions(regional_state)
        
        # Score and rank interventions
        scored_interventions = []
        for intervention in possible_interventions:
            score = self._score_intervention(regional_state, intervention)
            scored_interventions.append((score, intervention))
        
        # Sort by score (higher is better)
        scored_interventions.sort(key=lambda x: x[0], reverse=True)
        
        # Return top recommendations
        recommendations = [intervention for _, intervention in scored_interventions[:max_interventions]]
        
        logger.info(f"✅ Generated {len(recommendations)} recommendations for {region}")
        return recommendations
    
    def _generate_all_interventions(self, regional_state: RegionalState) -> List[InterventionAction]:
        """Generate all possible intervention actions for the regional state"""
        interventions = []
        
        for intervention_type in InterventionType:
            # Skip interventions not suitable for the region
            if not self._is_intervention_suitable(intervention_type, regional_state):
                continue
                
            # Generate different intensity levels
            for intensity in [30, 50, 70, 90]:
                # Generate different duration options
                for duration in [30, 90, 180, 365]:
                    intervention = InterventionAction(
                        intervention_type=intervention_type,
                        region=regional_state.region_name,
                        intensity=intensity,
                        duration_days=duration,
                        cost_estimate=0,  # Will be calculated
                        personnel_required=self._estimate_personnel(intervention_type, intensity),
                        risk_level=0,  # Will be calculated
                        expected_effectiveness=0  # Will be calculated
                    )
                    interventions.append(intervention)
        
        return interventions
    
    def _is_intervention_suitable(self, intervention_type: InterventionType, 
                                regional_state: RegionalState) -> bool:
        """Check if intervention type is suitable for the regional conditions"""
        # Counter-terrorism only for regions with terrorism activity
        if intervention_type == InterventionType.COUNTER_TERRORISM:
            return regional_state.boko_haram_activity > 20
        
        # Border reinforcement only for border regions
        if intervention_type == InterventionType.BORDER_REINFORCEMENT:
            return regional_state.cross_border_activity > 50
        
        # Development projects more suitable for economically unstable regions
        if intervention_type == InterventionType.DEVELOPMENT_PROJECTS:
            return regional_state.economic_stability < 60
        
        # Separatist-focused interventions only for anglophone regions
        if intervention_type in [InterventionType.PEACE_NEGOTIATIONS, 
                               InterventionType.GOVERNANCE_REFORM]:
            return regional_state.separatist_activity > 30
        
        return True  # Most interventions are generally applicable
    
    def _estimate_personnel(self, intervention_type: InterventionType, intensity: float) -> int:
        """Estimate personnel requirements for intervention"""
        base_personnel = {
            InterventionType.DIPLOMATIC_DIALOGUE: 10,
            InterventionType.MEDIATION_LOCAL_CHIEFS: 25,
            InterventionType.INTERNATIONAL_ENGAGEMENT: 15,
            InterventionType.PEACE_NEGOTIATIONS: 50,
            InterventionType.PREVENTIVE_DEPLOYMENT: 500,
            InterventionType.SECURITY_PATROLS: 200,
            InterventionType.INTELLIGENCE_OPERATIONS: 100,
            InterventionType.COUNTER_TERRORISM: 1000,
            InterventionType.BORDER_REINFORCEMENT: 800,
            InterventionType.DEVELOPMENT_PROJECTS: 150,
            InterventionType.ECONOMIC_INCENTIVES: 30,
            InterventionType.INFRASTRUCTURE_INVESTMENT: 300,
            InterventionType.TRADE_FACILITATION: 40,
            InterventionType.COMMUNITY_ENGAGEMENT: 75,
            InterventionType.MEDIA_CAMPAIGNS: 25,
            InterventionType.EDUCATION_PROGRAMS: 100,
            InterventionType.YOUTH_PROGRAMS: 80,
            InterventionType.HUMANITARIAN_AID: 200,
            InterventionType.GOVERNANCE_REFORM: 60,
            InterventionType.JUDICIAL_INTERVENTION: 40,
            InterventionType.ADMINISTRATIVE_MEASURES: 35
        }
        
        base = base_personnel.get(intervention_type, 100)
        return int(base * (intensity / 50))  # Scale based on intensity
    
    def _score_intervention(self, regional_state: RegionalState, 
                          intervention: InterventionAction) -> float:
        """Score an intervention based on effectiveness, cost, and risk"""
        # Prepare feature vector for ML prediction
        feature_vector = np.concatenate([
            regional_state.to_feature_vector(),
            [intervention.intensity, intervention.duration_days, intervention.personnel_required]
        ]).reshape(1, -1)
        
        feature_vector_scaled = self.scaler.transform(feature_vector)
        
        # Predict effectiveness, risk, and cost
        effectiveness = self.effectiveness_predictor.predict(feature_vector_scaled)[0]
        risk = self.risk_predictor.predict(feature_vector_scaled)[0]
        cost = self.cost_predictor.predict(feature_vector_scaled)[0]
        
        # Update intervention with predictions
        intervention.expected_effectiveness = max(0, min(100, effectiveness))
        intervention.risk_level = max(0, min(100, risk))
        intervention.cost_estimate = max(0.1, cost) * 1000000  # Convert to XAF
        
        # Calculate composite score (higher is better)
        # Effectiveness is positive, risk and cost are negative
        effectiveness_weight = 0.6
        risk_weight = 0.3
        cost_weight = 0.1
        
        # Normalize cost (logarithmic scale to handle wide range)
        normalized_cost = min(100, np.log10(intervention.cost_estimate / 1000000) * 20)
        
        score = (effectiveness * effectiveness_weight - 
                risk * risk_weight - 
                normalized_cost * cost_weight)
        
        return score
    
    def get_intervention_details(self, intervention: InterventionAction) -> Dict[str, Any]:
        """Get detailed information about an intervention"""
        return {
            "intervention_id": f"{intervention.intervention_type.value}_{intervention.region}_{intervention.intensity}",
            "type": intervention.intervention_type.value,
            "type_display": intervention.intervention_type.value.replace('_', ' ').title(),
            "region": intervention.region,
            "intensity": intervention.intensity,
            "duration_days": intervention.duration_days,
            "cost_estimate_xaf": intervention.cost_estimate,
            "cost_estimate_millions": intervention.cost_estimate / 1000000,
            "personnel_required": intervention.personnel_required,
            "risk_level": intervention.risk_level,
            "expected_effectiveness": intervention.expected_effectiveness,
            "risk_category": self._get_risk_category(intervention.risk_level),
            "effectiveness_category": self._get_effectiveness_category(intervention.expected_effectiveness),
            "implementation_timeline": self._get_implementation_timeline(intervention),
            "success_factors": self._get_success_factors(intervention),
            "challenges": self._get_potential_challenges(intervention),
            "kpis": self._get_intervention_kpis(intervention)
        }
    
    def _get_risk_category(self, risk_level: float) -> str:
        """Convert risk level to category"""
        if risk_level >= 80:
            return "Very High"
        elif risk_level >= 60:
            return "High"
        elif risk_level >= 40:
            return "Medium"
        elif risk_level >= 20:
            return "Low"
        else:
            return "Very Low"
    
    def _get_effectiveness_category(self, effectiveness: float) -> str:
        """Convert effectiveness to category"""
        if effectiveness >= 80:
            return "Very High"
        elif effectiveness >= 60:
            return "High"
        elif effectiveness >= 40:
            return "Medium"
        elif effectiveness >= 20:
            return "Low"
        else:
            return "Very Low"
    
    def _get_implementation_timeline(self, intervention: InterventionAction) -> List[str]:
        """Get implementation timeline phases"""
        return [
            "Phase 1: Planning and Preparation (7-14 days)",
            "Phase 2: Resource Mobilization (3-7 days)",
            "Phase 3: Deployment and Initial Implementation (1-3 days)",
            f"Phase 4: Full Implementation ({intervention.duration_days} days)",
            "Phase 5: Monitoring and Evaluation (Ongoing)",
            "Phase 6: Assessment and Handover (7-14 days)"
        ]
    
    def _get_success_factors(self, intervention: InterventionAction) -> List[str]:
        """Get key success factors for intervention"""
        factors = [
            "Strong local leadership support",
            "Clear communication strategy",
            "Adequate resource allocation",
            "Regular monitoring and evaluation",
            "Stakeholder engagement and buy-in"
        ]
        
        # Add intervention-specific factors
        if intervention.intervention_type == InterventionType.COUNTER_TERRORISM:
            factors.extend([
                "Intelligence coordination",
                "Population protection measures",
                "Cross-border cooperation"
            ])
        elif intervention.intervention_type == InterventionType.DEVELOPMENT_PROJECTS:
            factors.extend([
                "Community participation",
                "Sustainable financing",
                "Technical expertise availability"
            ])
        elif intervention.intervention_type == InterventionType.DIPLOMATIC_DIALOGUE:
            factors.extend([
                "Neutral mediator credibility",
                "Safe dialogue environment",
                "Commitment to agreements"
            ])
        
        return factors
    
    def _get_potential_challenges(self, intervention: InterventionAction) -> List[str]:
        """Get potential challenges for intervention"""
        challenges = [
            "Resource constraints",
            "Time limitations", 
            "Stakeholder resistance",
            "External interference",
            "Environmental factors"
        ]
        
        # Add intervention-specific challenges
        if intervention.intervention_type == InterventionType.COUNTER_TERRORISM:
            challenges.extend([
                "Civilian protection concerns",
                "Cross-border terrorist mobility",
                "Intelligence gathering difficulties"
            ])
        elif intervention.intervention_type == InterventionType.DEVELOPMENT_PROJECTS:
            challenges.extend([
                "Corruption risks",
                "Technical capacity limitations",
                "Long-term sustainability"
            ])
        
        return challenges
    
    def _get_intervention_kpis(self, intervention: InterventionAction) -> List[Dict]:
        """Get Key Performance Indicators for intervention"""
        kpis = [
            {
                "indicator": "Conflict Incidents Reduced",
                "target": "30% reduction in violent incidents",
                "measurement": "Monthly incident reports comparison"
            },
            {
                "indicator": "Implementation Timeline",
                "target": f"Complete within {intervention.duration_days} days",
                "measurement": "Project milestone tracking"
            },
            {
                "indicator": "Cost Efficiency",
                "target": f"Stay within {intervention.cost_estimate/1000000:.1f}M XAF budget",
                "measurement": "Financial expenditure tracking"
            },
            {
                "indicator": "Personnel Safety",
                "target": "Zero casualties among intervention personnel",
                "measurement": "Daily safety reports"
            }
        ]
        
        # Add intervention-specific KPIs
        if intervention.intervention_type == InterventionType.COUNTER_TERRORISM:
            kpis.append({
                "indicator": "Terrorist Network Disruption",
                "target": "50% reduction in terrorist operational capacity",
                "measurement": "Intelligence assessments"
            })
        elif intervention.intervention_type == InterventionType.DEVELOPMENT_PROJECTS:
            kpis.append({
                "indicator": "Economic Impact",
                "target": "20% increase in local economic activity",
                "measurement": "Economic survey data"
            })
        elif intervention.intervention_type == InterventionType.DIPLOMATIC_DIALOGUE:
            kpis.append({
                "indicator": "Agreement Compliance",
                "target": "90% adherence to negotiated agreements",
                "measurement": "Monitoring committee reports"
            })
        
        return kpis

def main():
    """Test the RL Decision System"""
    logger.info("🚀 Testing Advanced RL Decision System")
    
    rl_system = AdvancedRLDecisionSystem()
    
    # Test for different regions
    test_regions = ["Extreme-Nord", "Nord-Ouest", "Sud-Ouest"]
    
    for region in test_regions:
        logger.info(f"\n🎯 Testing recommendations for {region}")
        recommendations = rl_system.generate_intervention_recommendations(region, max_interventions=3)
        
        for i, intervention in enumerate(recommendations, 1):
            details = rl_system.get_intervention_details(intervention)
            print(f"\n📋 Recommendation {i} for {region}:")
            print(f"   Type: {details['type_display']}")
            print(f"   Effectiveness: {details['expected_effectiveness']:.1f}% ({details['effectiveness_category']})")
            print(f"   Risk: {details['risk_level']:.1f}% ({details['risk_category']})")
            print(f"   Cost: {details['cost_estimate_millions']:.1f}M XAF")
            print(f"   Personnel: {details['personnel_required']} people")
            print(f"   Duration: {details['duration_days']} days")

if __name__ == "__main__":
    main()
