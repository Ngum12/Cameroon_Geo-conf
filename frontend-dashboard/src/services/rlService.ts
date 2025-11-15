/**
 * 🤖 REINFORCEMENT LEARNING SERVICE
 * Integrates with Project Sentinel RL system for intervention recommendations
 */

import { UnifiedThreatPoint } from './threatIntelligence';

export interface InterventionRecommendation {
  id: string;
  threatId: string;
  region: string;
  interventionType: string;
  interventionName: string;
  description: string;
  confidence: number;
  costEstimate: number;
  personnelRequired: number;
  durationDays: number;
  riskLevel: number;
  successProbability: number;
  category: 'diplomatic' | 'military' | 'economic' | 'social' | 'administrative';
  urgency: 'immediate' | 'short_term' | 'medium_term' | 'long_term';
  resources: string[];
  expectedOutcome: string;
  timestamp: Date;
}

export interface RLAnalysisResult {
  threatId: string;
  threatLevel: number;
  region: string;
  recommendations: InterventionRecommendation[];
  optimalStrategy: InterventionRecommendation;
  riskAssessment: {
    noAction: number;
    recommended: number;
    alternative: number;
  };
  timeline: {
    immediate: InterventionRecommendation[];
    shortTerm: InterventionRecommendation[];
    longTerm: InterventionRecommendation[];
  };
}

class ReinforcementLearningService {
  private baseUrl = 'http://localhost:8004'; // RL API endpoint
  private isAvailable = false;

  constructor() {
    this.checkAvailability();
  }

  private async checkAvailability(): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      this.isAvailable = response.ok;
      console.log(`🤖 RL Service ${this.isAvailable ? 'ONLINE' : 'OFFLINE'}`);
    } catch (error) {
      this.isAvailable = false;
      console.log('🤖 RL Service OFFLINE - Using fallback recommendations');
    }
  }

  public async getInterventionRecommendations(threat: UnifiedThreatPoint): Promise<RLAnalysisResult> {
    if (!this.isAvailable) {
      return this.getFallbackRecommendations(threat);
    }

    try {
      const response = await fetch(`${this.baseUrl}/recommend-intervention`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          region: threat.region,
          threat_level: threat.threatLevel,
          threat_type: threat.category,
          recent_incidents: 5,
          economic_stability: 60,
          political_stability: 65,
          security_presence: 70
        })
      });

      if (!response.ok) throw new Error('RL API request failed');

      const data = await response.json();
      return this.transformApiResponse(data, threat);

    } catch (error) {
      console.error('❌ RL Service error:', error);
      return this.getFallbackRecommendations(threat);
    }
  }

  private transformApiResponse(apiData: any, threat: UnifiedThreatPoint): RLAnalysisResult {
    const recommendations: InterventionRecommendation[] = apiData.recommendations.map((rec: any, index: number) => ({
      id: `rl-${Date.now()}-${index}`,
      threatId: threat.id || `threat-${Date.now()}`,
      region: threat.region,
      interventionType: rec.intervention_type,
      interventionName: rec.intervention_name || this.getInterventionName(rec.intervention_type),
      description: rec.description || this.getInterventionDescription(rec.intervention_type),
      confidence: rec.confidence || 0.85,
      costEstimate: rec.cost_estimate || this.estimateCost(rec.intervention_type),
      personnelRequired: rec.personnel_required || this.estimatePersonnel(rec.intervention_type),
      durationDays: rec.duration_days || this.estimateDuration(rec.intervention_type),
      riskLevel: rec.risk_level || 0.3,
      successProbability: rec.success_probability || 0.75,
      category: this.categorizeIntervention(rec.intervention_type),
      urgency: this.determineUrgency(threat.threatLevel, rec.intervention_type),
      resources: rec.resources || this.getRequiredResources(rec.intervention_type),
      expectedOutcome: rec.expected_outcome || this.getExpectedOutcome(rec.intervention_type),
      timestamp: new Date()
    }));

    // Sort by confidence and success probability
    recommendations.sort((a, b) => (b.confidence * b.successProbability) - (a.confidence * a.successProbability));

    return {
      threatId: threat.id || `threat-${Date.now()}`,
      threatLevel: threat.threatLevel,
      region: threat.region,
      recommendations,
      optimalStrategy: recommendations[0],
      riskAssessment: {
        noAction: Math.min(threat.threatLevel / 100, 0.95),
        recommended: recommendations[0]?.riskLevel || 0.3,
        alternative: recommendations[1]?.riskLevel || 0.4
      },
      timeline: {
        immediate: recommendations.filter(r => r.urgency === 'immediate'),
        shortTerm: recommendations.filter(r => r.urgency === 'short_term'),
        longTerm: recommendations.filter(r => r.urgency === 'medium_term' || r.urgency === 'long_term')
      }
    };
  }

  private getFallbackRecommendations(threat: UnifiedThreatPoint): RLAnalysisResult {
    const recommendations: InterventionRecommendation[] = [];

    // Generate context-appropriate recommendations
    if (threat.region === 'Far North' || threat.region === 'Extreme-Nord') {
      recommendations.push({
        id: `fallback-${Date.now()}-1`,
        threatId: threat.id || `threat-${Date.now()}`,
        region: threat.region,
        interventionType: 'preventive_deployment',
        interventionName: 'Enhanced Border Patrol Operations',
        description: 'Deploy additional security forces along Chad-Nigeria borders to prevent Boko Haram infiltration',
        confidence: 0.89,
        costEstimate: 250000,
        personnelRequired: 150,
        durationDays: 90,
        riskLevel: 0.25,
        successProbability: 0.82,
        category: 'military',
        urgency: 'immediate',
        resources: ['Armored vehicles', 'Communication equipment', 'Intelligence assets'],
        expectedOutcome: '40% reduction in cross-border incidents',
        timestamp: new Date()
      });

      recommendations.push({
        id: `fallback-${Date.now()}-2`,
        threatId: threat.id || `threat-${Date.now()}`,
        region: threat.region,
        interventionType: 'community_engagement',
        interventionName: 'Community Intelligence Network',
        description: 'Establish local informant networks and community liaison programs',
        confidence: 0.76,
        costEstimate: 50000,
        personnelRequired: 25,
        durationDays: 180,
        riskLevel: 0.15,
        successProbability: 0.78,
        category: 'social',
        urgency: 'short_term',
        resources: ['Local chiefs', 'Communication systems', 'Training materials'],
        expectedOutcome: 'Improved early warning capabilities',
        timestamp: new Date()
      });

    } else if (threat.region === 'Southwest' || threat.region === 'Northwest' || threat.region === 'Sud-Ouest' || threat.region === 'Nord-Ouest') {
      recommendations.push({
        id: `fallback-${Date.now()}-3`,
        threatId: threat.id || `threat-${Date.now()}`,
        region: threat.region,
        interventionType: 'diplomatic_dialogue',
        interventionName: 'Regional Peace Dialogue Initiative',
        description: 'Facilitate negotiations between government and separatist groups through traditional rulers',
        confidence: 0.71,
        costEstimate: 100000,
        personnelRequired: 30,
        durationDays: 120,
        riskLevel: 0.35,
        successProbability: 0.65,
        category: 'diplomatic',
        urgency: 'immediate',
        resources: ['Traditional authorities', 'Neutral venues', 'Security guarantees'],
        expectedOutcome: 'Reduced separatist activities',
        timestamp: new Date()
      });

    } else {
      // General recommendations for other regions
      recommendations.push({
        id: `fallback-${Date.now()}-4`,
        threatId: threat.id || `threat-${Date.now()}`,
        region: threat.region,
        interventionType: 'intelligence_operations',
        interventionName: 'Enhanced Surveillance Operations',
        description: 'Increase intelligence gathering and monitoring in the affected region',
        confidence: 0.83,
        costEstimate: 75000,
        personnelRequired: 40,
        durationDays: 60,
        riskLevel: 0.20,
        successProbability: 0.80,
        category: 'military',
        urgency: threat.threatLevel >= 80 ? 'immediate' : 'short_term',
        resources: ['Surveillance equipment', 'Intelligence analysts', 'Communication systems'],
        expectedOutcome: 'Improved threat assessment and response',
        timestamp: new Date()
      });
    }

    recommendations.sort((a, b) => (b.confidence * b.successProbability) - (a.confidence * a.successProbability));

    return {
      threatId: threat.id || `threat-${Date.now()}`,
      threatLevel: threat.threatLevel,
      region: threat.region,
      recommendations,
      optimalStrategy: recommendations[0],
      riskAssessment: {
        noAction: Math.min(threat.threatLevel / 100, 0.95),
        recommended: recommendations[0]?.riskLevel || 0.25,
        alternative: recommendations[1]?.riskLevel || 0.35
      },
      timeline: {
        immediate: recommendations.filter(r => r.urgency === 'immediate'),
        shortTerm: recommendations.filter(r => r.urgency === 'short_term'),
        longTerm: recommendations.filter(r => r.urgency === 'medium_term' || r.urgency === 'long_term')
      }
    };
  }

  // Helper methods
  private getInterventionName(type: string): string {
    const names: { [key: string]: string } = {
      'preventive_deployment': 'Preventive Security Deployment',
      'security_patrols': 'Enhanced Security Patrols',
      'intelligence_operations': 'Intelligence Operations',
      'counter_terrorism': 'Counter-Terrorism Operations',
      'border_reinforcement': 'Border Security Enhancement',
      'diplomatic_dialogue': 'Diplomatic Engagement',
      'community_engagement': 'Community Outreach Program',
      'development_projects': 'Development Initiative',
      'economic_incentives': 'Economic Incentive Program',
      'media_campaigns': 'Strategic Communication Campaign',
      'education_programs': 'Educational Intervention',
      'humanitarian_aid': 'Humanitarian Assistance'
    };
    return names[type] || 'Strategic Intervention';
  }

  private getInterventionDescription(type: string): string {
    const descriptions: { [key: string]: string } = {
      'preventive_deployment': 'Deploy security forces to prevent escalation and maintain stability',
      'security_patrols': 'Increase security presence through regular patrol operations',
      'intelligence_operations': 'Gather actionable intelligence to inform strategic decisions',
      'counter_terrorism': 'Targeted operations against terrorist organizations',
      'border_reinforcement': 'Strengthen border security to prevent infiltration',
      'diplomatic_dialogue': 'Engage stakeholders through diplomatic channels',
      'community_engagement': 'Build relationships with local communities for sustainable peace',
      'development_projects': 'Implement infrastructure and economic development projects',
      'economic_incentives': 'Provide economic opportunities to reduce conflict drivers',
      'media_campaigns': 'Use strategic communication to counter extremist narratives',
      'education_programs': 'Educational initiatives to promote peace and stability',
      'humanitarian_aid': 'Provide humanitarian assistance to affected populations'
    };
    return descriptions[type] || 'Implement strategic measures to address the threat';
  }

  private categorizeIntervention(type: string): 'diplomatic' | 'military' | 'economic' | 'social' | 'administrative' {
    const diplomatic = ['diplomatic_dialogue', 'mediation_local_chiefs', 'international_engagement', 'peace_negotiations'];
    const military = ['preventive_deployment', 'security_patrols', 'intelligence_operations', 'counter_terrorism', 'border_reinforcement'];
    const economic = ['development_projects', 'economic_incentives', 'infrastructure_investment', 'trade_facilitation'];
    const social = ['community_engagement', 'media_campaigns', 'education_programs', 'youth_programs', 'humanitarian_aid'];
    const administrative = ['governance_reform', 'judicial_intervention', 'administrative_measures'];

    if (diplomatic.includes(type)) return 'diplomatic';
    if (military.includes(type)) return 'military';
    if (economic.includes(type)) return 'economic';
    if (social.includes(type)) return 'social';
    if (administrative.includes(type)) return 'administrative';
    return 'military';
  }

  private determineUrgency(threatLevel: number, type: string): 'immediate' | 'short_term' | 'medium_term' | 'long_term' {
    if (threatLevel >= 80) return 'immediate';
    if (threatLevel >= 60) return 'short_term';
    if (threatLevel >= 40) return 'medium_term';
    return 'long_term';
  }

  private estimateCost(type: string): number {
    const costs: { [key: string]: number } = {
      'diplomatic_dialogue': 25000,
      'preventive_deployment': 200000,
      'security_patrols': 150000,
      'intelligence_operations': 75000,
      'counter_terrorism': 300000,
      'border_reinforcement': 400000,
      'community_engagement': 50000,
      'development_projects': 500000,
      'economic_incentives': 250000,
      'media_campaigns': 30000,
      'education_programs': 80000,
      'humanitarian_aid': 100000
    };
    return costs[type] || 100000;
  }

  private estimatePersonnel(type: string): number {
    const personnel: { [key: string]: number } = {
      'diplomatic_dialogue': 15,
      'preventive_deployment': 200,
      'security_patrols': 100,
      'intelligence_operations': 50,
      'counter_terrorism': 150,
      'border_reinforcement': 300,
      'community_engagement': 25,
      'development_projects': 75,
      'economic_incentives': 30,
      'media_campaigns': 20,
      'education_programs': 40,
      'humanitarian_aid': 60
    };
    return personnel[type] || 50;
  }

  private estimateDuration(type: string): number {
    const durations: { [key: string]: number } = {
      'diplomatic_dialogue': 90,
      'preventive_deployment': 120,
      'security_patrols': 180,
      'intelligence_operations': 60,
      'counter_terrorism': 90,
      'border_reinforcement': 365,
      'community_engagement': 270,
      'development_projects': 540,
      'economic_incentives': 365,
      'media_campaigns': 180,
      'education_programs': 270,
      'humanitarian_aid': 120
    };
    return durations[type] || 90;
  }

  private getRequiredResources(type: string): string[] {
    const resources: { [key: string]: string[] } = {
      'diplomatic_dialogue': ['Meeting venues', 'Security detail', 'Translation services'],
      'preventive_deployment': ['Military units', 'Armored vehicles', 'Communication equipment'],
      'security_patrols': ['Patrol vehicles', 'Communication systems', 'Protective equipment'],
      'intelligence_operations': ['Intelligence analysts', 'Surveillance equipment', 'Secure communications'],
      'counter_terrorism': ['Special forces', 'Advanced equipment', 'Intelligence assets'],
      'border_reinforcement': ['Border guards', 'Surveillance systems', 'Detection equipment'],
      'community_engagement': ['Community liaisons', 'Meeting venues', 'Transportation'],
      'development_projects': ['Construction teams', 'Materials', 'Project managers'],
      'economic_incentives': ['Economic advisors', 'Funding mechanisms', 'Monitoring systems'],
      'media_campaigns': ['Media specialists', 'Production equipment', 'Distribution channels'],
      'education_programs': ['Educators', 'Learning materials', 'Facilities'],
      'humanitarian_aid': ['Relief supplies', 'Distribution network', 'Medical support']
    };
    return resources[type] || ['Personnel', 'Equipment', 'Logistics support'];
  }

  private getExpectedOutcome(type: string): string {
    const outcomes: { [key: string]: string } = {
      'diplomatic_dialogue': 'Peaceful resolution through negotiated agreement',
      'preventive_deployment': 'Deterrence and stability maintenance',
      'security_patrols': 'Reduced criminal activity and improved security',
      'intelligence_operations': 'Enhanced situational awareness and threat detection',
      'counter_terrorism': 'Disruption of terrorist networks and operations',
      'border_reinforcement': 'Improved border security and reduced infiltration',
      'community_engagement': 'Improved community cooperation and trust',
      'development_projects': 'Economic growth and improved living conditions',
      'economic_incentives': 'Reduced conflict drivers through economic opportunity',
      'media_campaigns': 'Counter-narratives and improved public perception',
      'education_programs': 'Long-term attitude change and conflict prevention',
      'humanitarian_aid': 'Immediate relief and stabilization of affected populations'
    };
    return outcomes[type] || 'Improved security situation and stability';
  }

  public isServiceAvailable(): boolean {
    return this.isAvailable;
  }
}

export const rlService = new ReinforcementLearningService();
export default rlService;
