/**
 * 🛡️ DEFENSE INTEGRATION SERVICE - MASTER SYSTEM ORCHESTRATOR
 * Integrates all defense systems: Notifications, Escalation, Human-in-Loop, Communications, Twilio
 * CAMEROON DEFENSE FORCE - PROJECT SENTINEL
 */

import { escalationService, EscalationState } from './escalationService';
import { twilioService, EmergencyAlert, TwilioConfig } from './twilioService';
import { IntelligenceNotification } from './notificationService';
import { alertMessagingService } from './alertMessagingService';

export interface DefenseSystemStatus {
  notifications: 'active' | 'inactive';
  escalation: 'monitoring' | 'idle';
  humanInLoop: 'available' | 'busy' | 'offline';
  communications: 'ready' | 'offline';
  twilio: 'configured' | 'pending' | 'disabled';
  lastHealthCheck: Date;
}

export interface SystemAlert {
  id: string;
  type: 'threat' | 'system' | 'escalation' | 'communication';
  severity: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  message: string;
  source: string;
  timestamp: Date;
  requiresAction: boolean;
  autoEscalate: boolean;
}

class DefenseIntegrationService {
  private systemStatus: DefenseSystemStatus = {
    notifications: 'active',
    escalation: 'monitoring',
    humanInLoop: 'available',
    communications: 'ready',
    twilio: 'pending',
    lastHealthCheck: new Date()
  };

  private systemAlerts: SystemAlert[] = [];
  private navigationHandlers: Map<string, (data: any) => void> = new Map();

  constructor() {
    this.initializeSystemIntegration();
    this.startSystemMonitoring();
  }

  /**
   * 🔧 INITIALIZE SYSTEM INTEGRATION
   */
  private initializeSystemIntegration(): void {
    console.log('🛡️ Initializing Defense Integration Service...');
    
    // Set up navigation handlers
    this.setupNavigationHandlers();
    
    // Set up cross-system event listeners
    this.setupSystemEventHandlers();
    
    // Health check all systems
    this.performSystemHealthCheck();
    
    console.log('✅ Defense Integration Service initialized');
  }

  /**
   * 🧭 SETUP NAVIGATION HANDLERS
   */
  private setupNavigationHandlers(): void {
    // Human-in-Loop navigation
    this.navigationHandlers.set('human-in-loop', (data) => {
      console.log('🔄 Navigating to Human-in-Loop verification:', data);
      
      // Store context for human-in-loop
      sessionStorage.setItem('sentinel-human-loop-context', JSON.stringify(data));
      
      // Navigate based on your routing system
      if (window.location.hash.includes('#/')) {
        window.location.hash = '#/human-in-loop-verification';
      } else {
        // For React Router or other systems
        window.dispatchEvent(new CustomEvent('sentinel:navigate', {
          detail: { route: '/human-in-loop-verification', context: data }
        }));
      }
    });

    // Communications Hub navigation
    this.navigationHandlers.set('communications-hub', (data) => {
      console.log('📡 Navigating to Communications Hub:', data);
      
      // Store context for communications hub
      sessionStorage.setItem('sentinel-comms-context', JSON.stringify(data));
      
      // Navigate based on your routing system
      if (window.location.hash.includes('#/')) {
        window.location.hash = '#/communications-hub';
      } else {
        // For React Router or other systems
        window.dispatchEvent(new CustomEvent('sentinel:navigate', {
          detail: { route: '/communications-hub', context: data }
        }));
      }
      
      // Pre-fill communications hub if auto-escalated
      if (data.autoFill) {
        setTimeout(() => {
          window.dispatchEvent(new CustomEvent('sentinel:comms-prefill', {
            detail: {
              threatData: {
                title: data.title,
                region: data.region,
                threatLevel: data.threatLevel,
                description: `Auto-escalated threat: ${data.title}`,
                urgent: true
              }
            }
          }));
        }, 1000);
      }
    });

    console.log('🧭 Navigation handlers configured');
  }

  /**
   * 📡 SETUP SYSTEM EVENT HANDLERS
   */
  private setupSystemEventHandlers(): void {
    // Escalation events
    window.addEventListener('sentinel:navigate-human-loop', (event: any) => {
      const handler = this.navigationHandlers.get('human-in-loop');
      if (handler) handler(event.detail);
    });

    window.addEventListener('sentinel:navigate-comms-hub', (event: any) => {
      const handler = this.navigationHandlers.get('communications-hub');
      if (handler) handler(event.detail);
    });

    // Emergency popup handler
    window.addEventListener('sentinel:emergency-popup', (event: any) => {
      this.handleEmergencyPopup(event.detail);
    });

    console.log('📡 System event handlers configured');
  }

  /**
   * 🚨 HANDLE EMERGENCY POPUP
   */
  private handleEmergencyPopup(data: any): void {
    console.log('🚨 Handling emergency popup:', data);
    
    // Create system alert
    const systemAlert: SystemAlert = {
      id: `emergency-${Date.now()}`,
      type: 'escalation',
      severity: 'critical',
      title: `AUTO-ESCALATED: ${data.escalation?.title || 'Unknown Threat'}`,
      message: 'No response received for 15 minutes. Emergency protocols activated.',
      source: 'Escalation Service',
      timestamp: new Date(),
      requiresAction: true,
      autoEscalate: true
    };

    this.systemAlerts.push(systemAlert);
    
    // Trigger auto-escalation to Communications Hub
    setTimeout(() => {
      this.triggerAutoEscalationFlow(data.escalation);
    }, 5000); // 5 second delay for user to see popup
  }

  /**
   * ⚡ TRIGGER AUTO-ESCALATION FLOW
   */
  private async triggerAutoEscalationFlow(escalation: EscalationState): Promise<void> {
    console.log('⚡ Triggering auto-escalation flow for:', escalation.title);
    
    try {
      // Step 1: Navigate to Communications Hub
      const handler = this.navigationHandlers.get('communications-hub');
      if (handler) {
        handler({
          notificationId: escalation.notificationId,
          title: escalation.title,
          region: escalation.region,
          threatLevel: escalation.threatLevel,
          autoFill: true,
          autoEscalated: true
        });
      }
      
      // Step 2: Send Twilio alerts (if configured)
      if (twilioService.isReady()) {
        const emergencyAlert: EmergencyAlert = {
          id: `auto-${escalation.notificationId}`,
          title: escalation.title,
          message: `CAMEROON DEFENSE AUTO-ESCALATION\n\nThreat: ${escalation.title}\nRegion: ${escalation.region}\nLevel: ${escalation.threatLevel}%\n\nNo response received for 15 minutes. Immediate action required.`,
          threatLevel: escalation.threatLevel,
          region: escalation.region,
          urgency: 'critical',
          recipients: ['gen-ondoa', 'emergency-ops'], // Emergency contacts
          channels: ['sms', 'whatsapp'],
          autoEscalated: true,
          timestamp: new Date()
        };

        await twilioService.sendEmergencyAlert(emergencyAlert);
        console.log('📱 Twilio emergency alerts sent');
      }
      
      // Step 3: Update system status
      this.systemStatus.escalation = 'monitoring';
      this.systemStatus.communications = 'ready';
      
    } catch (error) {
      console.error('❌ Auto-escalation flow failed:', error);
      
      // Fallback: At least trigger alert messaging service
      try {
        await alertMessagingService.sendCriticalAlert({
          id: `fallback-${escalation.notificationId}`,
          title: `🚨 SYSTEM AUTO-ESCALATION: ${escalation.title}`,
          message: `CRITICAL FAILURE: Auto-escalation failed for threat in ${escalation.region}.\n\nManual intervention required immediately.\n\nThreat Level: ${escalation.threatLevel}%`,
          urgency: 'critical',
          category: 'emergency',
          timestamp: new Date(),
          region: escalation.region,
          coordinates: { lat: 0, lng: 0 }
        });
      } catch (fallbackError) {
        console.error('❌ Fallback alert also failed:', fallbackError);
      }
    }
  }

  /**
   * 🏥 PERFORM SYSTEM HEALTH CHECK
   */
  private performSystemHealthCheck(): void {
    console.log('🏥 Performing system health check...');
    
    try {
      // Check Twilio
      this.systemStatus.twilio = twilioService.isReady() ? 'configured' : 'pending';
      
      // Check escalation service
      const activeEscalations = escalationService.getActiveEscalations();
      this.systemStatus.escalation = activeEscalations.size > 0 ? 'monitoring' : 'idle';
      
      // Update health check timestamp
      this.systemStatus.lastHealthCheck = new Date();
      
      console.log('✅ System health check complete:', this.systemStatus);
      
    } catch (error) {
      console.error('❌ System health check failed:', error);
    }
  }

  /**
   * ⏰ START SYSTEM MONITORING
   */
  private startSystemMonitoring(): void {
    // Health check every 2 minutes
    setInterval(() => {
      this.performSystemHealthCheck();
    }, 120000);
    
    // Clean old alerts every 10 minutes
    setInterval(() => {
      this.cleanOldAlerts();
    }, 600000);
    
    console.log('⏰ System monitoring started');
  }

  /**
   * 🧹 CLEAN OLD ALERTS
   */
  private cleanOldAlerts(): void {
    const cutoffTime = Date.now() - (24 * 60 * 60 * 1000); // 24 hours
    const initialCount = this.systemAlerts.length;
    
    this.systemAlerts = this.systemAlerts.filter(alert => 
      alert.timestamp.getTime() > cutoffTime
    );
    
    const removedCount = initialCount - this.systemAlerts.length;
    if (removedCount > 0) {
      console.log(`🧹 Cleaned ${removedCount} old system alerts`);
    }
  }

  /**
   * 🔧 CONFIGURE TWILIO API
   */
  public configureTwilio(config: TwilioConfig): void {
    console.log('🔧 Configuring Twilio integration...');
    
    try {
      twilioService.initialize(config);
      this.systemStatus.twilio = 'configured';
      
      // Enable escalation service to use Twilio
      escalationService.enableTwilio(true);
      
      console.log('✅ Twilio configured successfully');
      
      // Test connection
      this.testTwilioConnection();
      
    } catch (error) {
      console.error('❌ Twilio configuration failed:', error);
      this.systemStatus.twilio = 'disabled';
    }
  }

  /**
   * 🧪 TEST TWILIO CONNECTION
   */
  private async testTwilioConnection(): Promise<void> {
    try {
      const isConnected = await twilioService.testConnection();
      if (isConnected) {
        console.log('🧪 Twilio connection test passed');
        
        // Create success alert
        this.systemAlerts.push({
          id: `twilio-test-${Date.now()}`,
          type: 'system',
          severity: 'low',
          title: 'Twilio Integration Active',
          message: 'SMS and WhatsApp emergency alerts are now available',
          source: 'Defense Integration Service',
          timestamp: new Date(),
          requiresAction: false,
          autoEscalate: false
        });
      }
    } catch (error) {
      console.error('🧪 Twilio connection test failed:', error);
    }
  }

  // Public API
  public getSystemStatus(): DefenseSystemStatus {
    return { ...this.systemStatus };
  }

  public getSystemAlerts(): SystemAlert[] {
    return [...this.systemAlerts];
  }

  public getCriticalSystemAlerts(): SystemAlert[] {
    return this.systemAlerts.filter(alert => alert.severity === 'critical');
  }

  public getActiveEscalations(): Map<string, EscalationState> {
    return escalationService.getActiveEscalations();
  }

  public isTwilioReady(): boolean {
    return this.systemStatus.twilio === 'configured';
  }

  // Emergency manual override
  public triggerEmergencyProtocol(reason: string): void {
    console.log(`🚨 EMERGENCY PROTOCOL TRIGGERED: ${reason}`);
    
    const emergencyAlert: SystemAlert = {
      id: `emergency-${Date.now()}`,
      type: 'system',
      severity: 'critical',
      title: 'EMERGENCY PROTOCOL ACTIVATED',
      message: `Manual emergency protocol triggered: ${reason}`,
      source: 'Manual Override',
      timestamp: new Date(),
      requiresAction: true,
      autoEscalate: true
    };

    this.systemAlerts.push(emergencyAlert);
    
    // Trigger all emergency systems
    window.dispatchEvent(new CustomEvent('sentinel:emergency-protocol', {
      detail: { reason, alert: emergencyAlert }
    }));
  }
}

// Export singleton instance
export const defenseIntegrationService = new DefenseIntegrationService();
export default defenseIntegrationService;
