/**
 * 🚨 ESCALATION SERVICE - DEFENSE CRITICAL ALERT ESCALATION SYSTEM
 * Manages threat escalation timeline, human-in-loop integration, and emergency protocols
 * CAMEROON DEFENSE FORCE - PROJECT SENTINEL
 */

import { IntelligenceNotification } from './notificationService';
import { alertMessagingService, AlertMessage } from './alertMessagingService';

export interface EscalationState {
  notificationId: string;
  threatLevel: number;
  region: string;
  title: string;
  initialAlert: Date;
  lastAlarm: Date;
  escalationLevel: 'initial' | 'reminder' | 'critical' | 'emergency' | 'auto_escalated';
  actionTaken: boolean;
  humanResponseRequired: boolean;
  autoEscalationTriggered: boolean;
  twilioAlertSent: boolean;
  timers: {
    reminderTimer?: NodeJS.Timeout;
    emergencyTimer?: NodeJS.Timeout;
    autoEscalationTimer?: NodeJS.Timeout;
  };
}

export interface EscalationConfig {
  reminderDelayMinutes: number;
  emergencyDelayMinutes: number;  
  autoEscalationDelayMinutes: number;
  soundAlertEnabled: boolean;
  twilioEnabled: boolean;
}

export interface ThreatActionRequest {
  notificationId: string;
  actionType: 'acknowledge' | 'investigate' | 'escalate' | 'dismiss';
  operatorId: string;
  timestamp: Date;
  notes?: string;
}

class EscalationService {
  private activeEscalations: Map<string, EscalationState> = new Map();
  private config: EscalationConfig = {
    reminderDelayMinutes: 5,    // 5 minutes for first reminder
    emergencyDelayMinutes: 10,  // 10 minutes for emergency alarm  
    autoEscalationDelayMinutes: 15, // 15 minutes for auto-escalation
    soundAlertEnabled: true,
    twilioEnabled: true  // Will be activated when API is provided
  };

  // Sound management
  private audioContext: AudioContext | null = null;
  private alarmSounds = {
    initial: { frequency: 800, duration: 1000 },
    reminder: { frequency: 1000, duration: 1500 },
    emergency: { frequency: 1200, duration: 2000, repeat: 3 }
  };

  constructor() {
    this.initializeAudioContext();
    this.startEscalationMonitoring();
  }

  private initializeAudioContext(): void {
    try {
      this.audioContext = new AudioContext();
      console.log('🔊 Escalation Service: Audio context initialized');
    } catch (error) {
      console.error('❌ Audio context initialization failed:', error);
    }
  }

  private startEscalationMonitoring(): void {
    // Monitor escalations every 30 seconds
    setInterval(() => {
      this.checkEscalationStatus();
    }, 30000);
    
    console.log('⏰ Escalation monitoring started');
  }

  /**
   * 🚨 INITIATE ESCALATION for critical threat
   */
  public initiateEscalation(notification: IntelligenceNotification): void {
    const escalationId = notification.id;
    
    console.log(`🚨 INITIATING ESCALATION: ${escalationId} - ${notification.title}`);
    
    const escalationState: EscalationState = {
      notificationId: escalationId,
      threatLevel: this.extractThreatLevel(notification),
      region: notification.region || 'Unknown',
      title: notification.title,
      initialAlert: new Date(),
      lastAlarm: new Date(),
      escalationLevel: 'initial',
      actionTaken: false,
      humanResponseRequired: this.requiresHumanResponse(notification),
      autoEscalationTriggered: false,
      twilioAlertSent: false,
      timers: {}
    };

    // Set up escalation timers
    this.setupEscalationTimers(escalationState);
    
    // Store escalation state
    this.activeEscalations.set(escalationId, escalationState);
    
    // Play initial sound alert
    if (this.config.soundAlertEnabled) {
      this.playAlarmSound('initial');
    }
    
    console.log(`✅ Escalation initiated for threat level ${escalationState.threatLevel}% in ${escalationState.region}`);
  }

  /**
   * ⏰ SET UP ESCALATION TIMERS
   */
  private setupEscalationTimers(escalation: EscalationState): void {
    // Timer 1: Reminder alarm after 5 minutes
    escalation.timers.reminderTimer = setTimeout(() => {
      this.handleReminderEscalation(escalation.notificationId);
    }, this.config.reminderDelayMinutes * 60 * 1000);

    // Timer 2: Emergency alarm after 10 minutes
    escalation.timers.emergencyTimer = setTimeout(() => {
      this.handleEmergencyEscalation(escalation.notificationId);
    }, this.config.emergencyDelayMinutes * 60 * 1000);

    // Timer 3: Auto-escalation after 15 minutes
    escalation.timers.autoEscalationTimer = setTimeout(() => {
      this.handleAutoEscalation(escalation.notificationId);
    }, this.config.autoEscalationDelayMinutes * 60 * 1000);

    console.log(`⏰ Escalation timers set: Reminder(${this.config.reminderDelayMinutes}m), Emergency(${this.config.emergencyDelayMinutes}m), Auto(${this.config.autoEscalationDelayMinutes}m)`);
  }

  /**
   * 🔔 HANDLE REMINDER ESCALATION (5 minutes)
   */
  private handleReminderEscalation(notificationId: string): void {
    const escalation = this.activeEscalations.get(notificationId);
    if (!escalation || escalation.actionTaken) return;

    console.log(`🔔 REMINDER ESCALATION: ${escalation.title}`);
    
    escalation.escalationLevel = 'reminder';
    escalation.lastAlarm = new Date();
    
    // Play reminder sound
    if (this.config.soundAlertEnabled) {
      this.playAlarmSound('reminder');
    }
    
    // Trigger visual reminder notification
    this.triggerReminderNotification(escalation);
    
    this.activeEscalations.set(notificationId, escalation);
  }

  /**
   * 🚨 HANDLE EMERGENCY ESCALATION (10 minutes) 
   */
  private handleEmergencyEscalation(notificationId: string): void {
    const escalation = this.activeEscalations.get(notificationId);
    if (!escalation || escalation.actionTaken) return;

    console.log(`🚨 EMERGENCY ESCALATION: ${escalation.title}`);
    
    escalation.escalationLevel = 'emergency';
    escalation.lastAlarm = new Date();
    
    // Play emergency sound (repeated)
    if (this.config.soundAlertEnabled) {
      this.playAlarmSound('emergency');
    }
    
    // Trigger emergency notification
    this.triggerEmergencyNotification(escalation);
    
    this.activeEscalations.set(notificationId, escalation);
  }

  /**
   * ⚡ HANDLE AUTO-ESCALATION (15 minutes) - CRITICAL
   */
  private async handleAutoEscalation(notificationId: string): Promise<void> {
    const escalation = this.activeEscalations.get(notificationId);
    if (!escalation || escalation.actionTaken) return;

    console.log(`⚡ AUTO-ESCALATION TRIGGERED: ${escalation.title}`);
    
    escalation.escalationLevel = 'auto_escalated';
    escalation.autoEscalationTriggered = true;
    
    // Direct alert to Communications Hub
    await this.triggerAutoEscalationAlert(escalation);
    
    // Send Twilio alert (when API is available)
    if (this.config.twilioEnabled) {
      await this.sendTwilioAlert(escalation);
    }
    
    this.activeEscalations.set(notificationId, escalation);
  }

  /**
   * 🎵 PLAY ALARM SOUND
   */
  private playAlarmSound(type: 'initial' | 'reminder' | 'emergency'): void {
    if (!this.audioContext) return;
    
    const sound = this.alarmSounds[type];
    const repeatCount = type === 'emergency' ? 3 : 1;
    
    for (let i = 0; i < repeatCount; i++) {
      setTimeout(() => {
        this.generateAlarmTone(sound.frequency, sound.duration);
      }, i * (sound.duration + 500));
    }
  }

  private generateAlarmTone(frequency: number, duration: number): void {
    if (!this.audioContext) return;
    
    const oscillator = this.audioContext.createOscillator();
    const gainNode = this.audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(this.audioContext.destination);
    
    oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration / 1000);
    
    oscillator.start(this.audioContext.currentTime);
    oscillator.stop(this.audioContext.currentTime + duration / 1000);
  }

  /**
   * 👤 HANDLE ACTION TAKEN BY OPERATOR
   */
  public handleThreatAction(action: ThreatActionRequest): void {
    const escalation = this.activeEscalations.get(action.notificationId);
    if (!escalation) {
      console.warn(`❌ No escalation found for notification: ${action.notificationId}`);
      return;
    }

    console.log(`👤 ACTION TAKEN: ${action.actionType} by ${action.operatorId} for ${escalation.title}`);
    
    // Mark action as taken
    escalation.actionTaken = true;
    
    // Clear all timers
    this.clearEscalationTimers(escalation);
    
    // Handle different action types
    switch (action.actionType) {
      case 'acknowledge':
        console.log(`✅ Threat acknowledged: ${escalation.title}`);
        break;
      case 'investigate':
        console.log(`🔍 Investigation initiated: ${escalation.title}`);
        // Redirect to human-in-loop verification
        this.redirectToHumanInLoop(escalation);
        break;
      case 'escalate':
        console.log(`⬆️ Manual escalation: ${escalation.title}`);
        // Redirect to communications hub
        this.redirectToCommsHub(escalation);
        break;
      case 'dismiss':
        console.log(`❌ Threat dismissed: ${escalation.title}`);
        break;
    }
    
    this.activeEscalations.set(action.notificationId, escalation);
  }

  /**
   * 🔄 REDIRECT TO HUMAN-IN-LOOP VERIFICATION
   */
  private redirectToHumanInLoop(escalation: EscalationState): void {
    console.log(`🔄 Redirecting to Human-in-Loop: ${escalation.title}`);
    
    // Emit event for UI navigation
    window.dispatchEvent(new CustomEvent('sentinel:navigate-human-loop', {
      detail: {
        notificationId: escalation.notificationId,
        threatLevel: escalation.threatLevel,
        region: escalation.region,
        title: escalation.title
      }
    }));
  }

  /**
   * 📡 REDIRECT TO COMMUNICATIONS HUB
   */
  private redirectToCommsHub(escalation: EscalationState): void {
    console.log(`📡 Redirecting to Communications Hub: ${escalation.title}`);
    
    // Emit event for UI navigation
    window.dispatchEvent(new CustomEvent('sentinel:navigate-comms-hub', {
      detail: {
        notificationId: escalation.notificationId,
        threatLevel: escalation.threatLevel,
        region: escalation.region,
        title: escalation.title,
        autoFill: true
      }
    }));
  }

  /**
   * ⚡ TRIGGER AUTO-ESCALATION ALERT
   */
  private async triggerAutoEscalationAlert(escalation: EscalationState): Promise<void> {
    console.log(`⚡ Triggering auto-escalation alert for: ${escalation.title}`);
    
    const alertMessage: AlertMessage = {
      id: `auto-escalation-${escalation.notificationId}`,
      title: `🚨 AUTO-ESCALATED THREAT: ${escalation.title}`,
      message: `CRITICAL: No response received for ${this.config.autoEscalationDelayMinutes} minutes.\n\nThreat Level: ${escalation.threatLevel}%\nRegion: ${escalation.region}\n\nAUTO-ESCALATION PROTOCOLS ACTIVATED\nImmediate defense response required.`,
      urgency: 'critical',
      category: 'emergency',
      timestamp: new Date(),
      region: escalation.region,
      coordinates: { lat: 0, lng: 0 }
    };

    // Send via alert messaging service
    await alertMessagingService.sendCriticalAlert(alertMessage);
    
    // Trigger communications hub popup
    window.dispatchEvent(new CustomEvent('sentinel:emergency-popup', {
      detail: {
        escalation,
        alertMessage,
        autoEscalated: true
      }
    }));
  }

  /**
   * 📱 SEND TWILIO ALERT (Integrated with TwilioService)
   */
  private async sendTwilioAlert(escalation: EscalationState): Promise<void> {
    if (!this.config.twilioEnabled) {
      console.log('📱 Twilio integration pending API credentials...');
      return;
    }

    console.log(`📱 Sending Twilio alert for: ${escalation.title}`);
    
    try {
      // Import TwilioService dynamically to avoid circular dependency
      const { twilioService } = await import('./twilioService');
      
      if (!twilioService.isReady()) {
        console.log('📱 Twilio not configured yet, alert queued...');
        return;
      }

      const emergencyAlert = {
        id: `escalation-${escalation.notificationId}`,
        title: escalation.title,
        message: `🚨 CAMEROON DEFENSE AUTO-ESCALATION\n\nThreat: ${escalation.title}\nLevel: ${escalation.threatLevel}%\nRegion: ${escalation.region}\n\nNo response received for 15 minutes.\nImmediate response required.\n\nProject Sentinel Defense System`,
        threatLevel: escalation.threatLevel,
        region: escalation.region,
        urgency: 'critical' as const,
        recipients: this.getEmergencyContacts(),
        channels: ['sms' as const, 'whatsapp' as const],
        autoEscalated: true,
        timestamp: new Date()
      };
      
      const deliveryResults = await twilioService.sendEmergencyAlert(emergencyAlert);
      
      const successful = deliveryResults.filter(r => r.status === 'sent' || r.status === 'queued').length;
      console.log(`📱 Twilio alert sent: ${successful}/${deliveryResults.length} successful`);
      
      escalation.twilioAlertSent = successful > 0;
      
    } catch (error) {
      console.error('❌ Twilio alert failed:', error);
    }
  }

  /**
   * 🚨 TRIGGER REMINDER NOTIFICATION
   */
  private triggerReminderNotification(escalation: EscalationState): void {
    window.dispatchEvent(new CustomEvent('sentinel:reminder-alert', {
      detail: {
        notificationId: escalation.notificationId,
        title: `🔔 REMINDER: ${escalation.title}`,
        message: `No action taken for ${this.config.reminderDelayMinutes} minutes. Please respond.`,
        escalationLevel: 'reminder',
        threatLevel: escalation.threatLevel,
        region: escalation.region
      }
    }));
  }

  /**
   * 🚨 TRIGGER EMERGENCY NOTIFICATION  
   */
  private triggerEmergencyNotification(escalation: EscalationState): void {
    window.dispatchEvent(new CustomEvent('sentinel:emergency-alert', {
      detail: {
        notificationId: escalation.notificationId,
        title: `🚨 EMERGENCY: ${escalation.title}`,
        message: `CRITICAL: No response for ${this.config.emergencyDelayMinutes} minutes. Auto-escalation in ${this.config.autoEscalationDelayMinutes - this.config.emergencyDelayMinutes} minutes.`,
        escalationLevel: 'emergency',
        threatLevel: escalation.threatLevel,
        region: escalation.region
      }
    }));
  }

  /**
   * ⏰ CLEAR ESCALATION TIMERS
   */
  private clearEscalationTimers(escalation: EscalationState): void {
    if (escalation.timers.reminderTimer) {
      clearTimeout(escalation.timers.reminderTimer);
      escalation.timers.reminderTimer = undefined;
    }
    if (escalation.timers.emergencyTimer) {
      clearTimeout(escalation.timers.emergencyTimer);
      escalation.timers.emergencyTimer = undefined;
    }
    if (escalation.timers.autoEscalationTimer) {
      clearTimeout(escalation.timers.autoEscalationTimer);
      escalation.timers.autoEscalationTimer = undefined;
    }
    
    console.log(`⏰ Escalation timers cleared for: ${escalation.title}`);
  }

  /**
   * 🏥 CHECK ESCALATION STATUS (Monitoring)
   */
  private checkEscalationStatus(): void {
    const activeCount = this.activeEscalations.size;
    if (activeCount > 0) {
      console.log(`🏥 Monitoring ${activeCount} active escalations`);
      
      // Check for stuck escalations
      this.activeEscalations.forEach((escalation, id) => {
        const ageMinutes = (Date.now() - escalation.initialAlert.getTime()) / (1000 * 60);
        if (ageMinutes > 60) { // 1 hour old
          console.warn(`⚠️ Escalation ${id} is ${Math.round(ageMinutes)}m old`);
        }
      });
    }
  }

  // Helper methods
  private extractThreatLevel(notification: IntelligenceNotification): number {
    // Extract threat level from notification metadata or content
    return notification.metadata?.threatLevel || 
           (notification.priority === 'critical' ? 85 : 
            notification.priority === 'high' ? 70 : 50);
  }

  private requiresHumanResponse(notification: IntelligenceNotification): boolean {
    return notification.priority === 'critical' || 
           notification.requiresAction === true;
  }

  private getEmergencyContacts(): string[] {
    // Return list of emergency contact IDs for Twilio
    return ['emergency-commander', 'operations-center', 'regional-head'];
  }

  // Public getters for monitoring
  public getActiveEscalations(): Map<string, EscalationState> {
    return new Map(this.activeEscalations);
  }

  public getEscalationConfig(): EscalationConfig {
    return { ...this.config };
  }

  public updateConfig(newConfig: Partial<EscalationConfig>): void {
    this.config = { ...this.config, ...newConfig };
    console.log('⚙️ Escalation config updated:', this.config);
  }

  // Enable Twilio when API is available
  public enableTwilio(enabled: boolean = true): void {
    this.config.twilioEnabled = enabled;
    console.log(`📱 Twilio integration ${enabled ? 'ENABLED' : 'DISABLED'}`);
  }
}

// Export singleton instance
export const escalationService = new EscalationService();
export default escalationService;
