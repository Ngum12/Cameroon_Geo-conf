/**
 * 🧪 ESCALATION SYSTEM TEST TRIGGER
 * Forces critical threat notifications to test the escalation system
 */

import { notificationService } from './notificationService';

export function triggerCriticalThreatForTesting() {
  console.log('🧪 TESTING: Injecting critical threat notification...');

  // Create a critical threat that WILL trigger escalation
  const criticalThreat = {
    title: '🚨 IMMINENT THREAT - BORDER INCURSION DETECTED',
    message: '🔥 IMMINENT THREAT: Large armed group crossing Chad-Cameroon border. Satellite confirms 25+ personnel with vehicles. IMMEDIATE MILITARY RESPONSE REQUIRED. Escalation protocols ACTIVE.',
    priority: 'critical' as const,
    category: 'high_alert' as const,
    source: 'Emergency Intelligence',
    region: 'Far North',
    requiresAction: true,
    audioAlert: true,
    threatLevel: 94,
    metadata: {
      threatLevel: 94,
      confidence: 0.96,
      coordinates: { lat: 12.1, lng: 15.2 },
      urgency: 'immediate',
      operationalCode: 'CRITICAL-9999'
    }
  };

  // Force create the notification (bypass the normal generation)
  (notificationService as any).createDefenseNotification(criticalThreat);
  
  console.log('🚨 CRITICAL THREAT INJECTED! Escalation system should activate...');
  console.log('⏰ Wait 5 minutes for reminder, 10 minutes for emergency, 15 minutes for auto-escalation');
}

export function triggerMultipleCriticalThreats() {
  console.log('🧪 TESTING: Injecting multiple critical threats...');

  const threats = [
    {
      title: '⚡ TERROR CELL ACTIVATION - CRITICAL ALERT',
      message: '💥 CRITICAL: Terror cell activation detected in Northwest region. Communications intercepts confirm coordinated attack planning. DEFENSE FORCES MOBILIZE NOW. Auto-escalation in 15 minutes.',
      priority: 'critical' as const,
      category: 'threat_escalation' as const,
      source: 'Counter-Terrorism Intelligence',
      region: 'Northwest',
      requiresAction: true,
      audioAlert: true,
      threatLevel: 88,
      metadata: {
        threatLevel: 88,
        confidence: 0.92,
        coordinates: { lat: 6.0, lng: 10.3 },
        urgency: 'critical',
        operationalCode: 'ALPHA-8888'
      }
    },
    {
      title: '🔥 MASS CASUALTY THREAT - IMMEDIATE ACTION',
      message: '⚠️ MASS CASUALTY THREAT: Intelligence indicates planned attack on civilian targets. Multiple sources confirm. EVACUATIONS RECOMMENDED. All units on high alert. ESCALATE IMMEDIATELY.',
      priority: 'critical' as const,
      category: 'high_alert' as const,
      source: 'Threat Analysis Unit',
      region: 'Southwest',
      requiresAction: true,
      audioAlert: true,
      threatLevel: 87,
      metadata: {
        threatLevel: 87,
        confidence: 0.89,
        coordinates: { lat: 4.2, lng: 9.3 },
        urgency: 'immediate',
        operationalCode: 'BRAVO-7777'
      }
    },
    {
      title: '💀 BOKO HARAM ATTACK IMMINENT - CRITICAL',
      message: '🚨 BOKO HARAM ATTACK IMMINENT: Multiple intelligence sources confirm coordinated assault planned within 24 hours. Far North region at maximum threat level. ALL DEFENSE UNITS MOBILIZE.',
      priority: 'critical' as const,
      category: 'threat_escalation' as const,
      source: 'Joint Intelligence Command',
      region: 'Far North',
      requiresAction: true,
      audioAlert: true,
      threatLevel: 93,
      metadata: {
        threatLevel: 93,
        confidence: 0.97,
        coordinates: { lat: 12.2, lng: 14.9 },
        urgency: 'immediate',
        operationalCode: 'CHARLIE-9999'
      }
    }
  ];

  // Inject threats with delays
  threats.forEach((threat, index) => {
    setTimeout(() => {
      (notificationService as any).createDefenseNotification(threat);
      console.log(`🚨 Critical threat ${index + 1}/3 injected: ${threat.title}`);
    }, index * 10000); // 10 second delays between threats
  });

  console.log('🚨 MULTIPLE CRITICAL THREATS QUEUED! Each will trigger separate escalation timers...');
}

// Auto-expose for browser console testing
if (typeof window !== 'undefined') {
  (window as any).testEscalation = {
    single: triggerCriticalThreatForTesting,
    multiple: triggerMultipleCriticalThreats
  };
  console.log('🧪 Escalation testing available via: window.testEscalation.single() or window.testEscalation.multiple()');
}
