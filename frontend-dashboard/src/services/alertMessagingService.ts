/**
 * 🚨 MULTI-CHANNEL ALERT MESSAGING SERVICE
 * Sends critical defense alerts via Email, WhatsApp, and SMS
 * Ensures message delivery even with internet/network issues
 */

export interface AlertRecipient {
  id: string;
  name: string;
  email?: string;
  whatsapp?: string; // Phone number with country code
  sms?: string; // Phone number for SMS
  role: 'commander' | 'field_officer' | 'analyst' | 'emergency_contact';
  region: string;
  priority: 'critical' | 'high' | 'medium';
}

export interface AlertMessage {
  id: string;
  title: string;
  message: string;
  urgency: 'critical' | 'high' | 'medium' | 'low';
  category: 'security_threat' | 'emergency' | 'tactical' | 'intelligence';
  timestamp: Date;
  region?: string;
  coordinates?: { lat: number; lng: number };
  attachments?: string[];
}

export interface AlertDeliveryStatus {
  messageId: string;
  recipientId: string;
  email?: { status: 'sent' | 'delivered' | 'failed'; timestamp?: Date; error?: string };
  whatsapp?: { status: 'sent' | 'delivered' | 'read' | 'failed'; timestamp?: Date; error?: string };
  sms?: { status: 'sent' | 'delivered' | 'failed'; timestamp?: Date; error?: string };
  overallStatus: 'success' | 'partial' | 'failed';
}

class AlertMessagingService {
  private recipients: AlertRecipient[] = [];
  private deliveryHistory: AlertDeliveryStatus[] = [];
  private retryAttempts = 3;
  private retryDelay = 5000; // 5 seconds

  constructor() {
    this.initializeCameroonDefenseContacts();
  }

  /**
   * Initialize realistic Cameroon Defense Force contact list
   */
  private initializeCameroonDefenseContacts(): void {
    this.recipients = [
      // Primary Test Contact - Your Number Only
      {
        id: 'primary-contact-01',
        name: 'Defense Command Center',
        email: 'command@defense.cm',
        whatsapp: '+250792104982',
        sms: '+250792104982',
        role: 'commander',
        region: 'All',
        priority: 'critical'
      }
    ];

    console.log('🎯 Alert Messaging: Initialized Cameroon Defense contacts', this.recipients.length);
  }

  /**
   * Send critical alert via all 3 channels with intelligent fallback
   */
  async sendCriticalAlert(message: AlertMessage, targetRecipients?: string[]): Promise<AlertDeliveryStatus[]> {
    console.log('🚨 CRITICAL ALERT INITIATED:', message.title);
    
    // Determine recipients based on urgency and region
    const relevantRecipients = this.selectRecipientsForAlert(message, targetRecipients);
    console.log(`📡 Sending to ${relevantRecipients.length} recipients across 3 channels`);

    const deliveryStatuses: AlertDeliveryStatus[] = [];

    // Send alerts to each recipient via all available channels
    for (const recipient of relevantRecipients) {
      const status: AlertDeliveryStatus = {
        messageId: message.id,
        recipientId: recipient.id,
        overallStatus: 'failed'
      };

      console.log(`📱 Alerting ${recipient.name} (${recipient.role}) in ${recipient.region}`);

      // Attempt delivery via all channels with delays to avoid rate limits
      const deliveryPromises = [
        this.sendEmailAlert(recipient, message),
        // Add 1 second delay before WhatsApp
        new Promise(resolve => setTimeout(resolve, 1000)).then(() => this.sendWhatsAppAlert(recipient, message)),
        // Add 2 second delay before SMS
        new Promise(resolve => setTimeout(resolve, 2000)).then(() => this.sendSMSAlert(recipient, message))
      ];

      try {
        const results = await Promise.allSettled(deliveryPromises);
        
        status.email = results[0].status === 'fulfilled' ? results[0].value : { status: 'failed', error: 'Network error' };
        status.whatsapp = results[1].status === 'fulfilled' ? results[1].value : { status: 'failed', error: 'Network error' };
        status.sms = results[2].status === 'fulfilled' ? results[2].value : { status: 'failed', error: 'Network error' };

        // Determine overall status
        const successCount = [status.email, status.whatsapp, status.sms]
          .filter(channel => channel && (channel.status === 'sent' || channel.status === 'delivered')).length;

        if (successCount === 3) {
          status.overallStatus = 'success';
        } else if (successCount > 0) {
          status.overallStatus = 'partial';
        }

        console.log(`✅ ${recipient.name}: ${successCount}/3 channels delivered`);

      } catch (error) {
        console.error(`❌ Failed to alert ${recipient.name}:`, error);
      }

      deliveryStatuses.push(status);
    }

    // Store delivery history
    this.deliveryHistory.push(...deliveryStatuses);

    // Log summary
    const totalSuccess = deliveryStatuses.filter(s => s.overallStatus === 'success').length;
    const totalPartial = deliveryStatuses.filter(s => s.overallStatus === 'partial').length;
    const totalFailed = deliveryStatuses.filter(s => s.overallStatus === 'failed').length;

    console.log(`🎯 Alert delivery summary: ${totalSuccess} full success, ${totalPartial} partial, ${totalFailed} failed`);

    return deliveryStatuses;
  }

  /**
   * Send Email Alert (Primary channel for detailed information)
   */
  private async sendEmailAlert(recipient: AlertRecipient, message: AlertMessage) {
    if (!recipient.email) {
      throw new Error('No email address available');
    }

    console.log(`📧 Sending email to ${recipient.email}`);

    // Simulate email API call
    return new Promise<{ status: 'sent' | 'delivered' | 'failed'; timestamp?: Date; error?: string }>((resolve) => {
      setTimeout(() => {
        // 95% success rate for email (good internet infrastructure in cities)
        if (Math.random() > 0.05) {
          resolve({ status: 'sent', timestamp: new Date() });
        } else {
          resolve({ status: 'failed', error: 'SMTP server unavailable' });
        }
      }, 1000 + Math.random() * 2000);
    });
  }

  /**
   * Send WhatsApp Alert (Secondary channel for instant delivery)
   */
  private async sendWhatsAppAlert(recipient: AlertRecipient, message: AlertMessage) {
    if (!recipient.whatsapp) {
      throw new Error('No WhatsApp number available');
    }

    console.log(`💬 Sending WhatsApp to ${recipient.whatsapp}`);

    try {
      // 🎯 REAL TWILIO API CALL - Replace simulation with actual backend call
      const response = await fetch('/api/v1/twilio/send-message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          to: `whatsapp:${recipient.whatsapp}`,
          body: `${message.title}\n\n${message.message}`,
          channel: 'whatsapp'
        })
      });

      if (response.ok) {
        const result = await response.json();
        console.log(`✅ WhatsApp sent successfully to ${recipient.name}:`, result.sid);
        return { status: 'sent' as const, timestamp: new Date() };
      } else {
        const error = await response.json();
        if (response.status === 429) {
          console.warn(`⏳ WhatsApp rate limited for ${recipient.name} - will retry later`);
          return { status: 'failed' as const, error: 'Rate limited - try again in a few minutes' };
        }
        console.error(`❌ WhatsApp failed for ${recipient.name}:`, error);
        return { status: 'failed' as const, error: error.error || 'API call failed' };
      }
    } catch (error) {
      console.error(`❌ WhatsApp network error for ${recipient.name}:`, error);
      return { status: 'failed' as const, error: 'Network error' };
    }
  }

  /**
   * Send SMS Alert (Fallback channel for network issues)
   */
  private async sendSMSAlert(recipient: AlertRecipient, message: AlertMessage) {
    if (!recipient.sms) {
      throw new Error('No SMS number available');
    }

    console.log(`📱 Sending SMS to ${recipient.sms}`);

    try {
      // 🎯 REAL TWILIO API CALL - Replace simulation with actual backend call
      const response = await fetch('/api/v1/twilio/send-message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          to: recipient.sms,
          body: `${message.title}\n\n${message.message}`,
          channel: 'sms'
        })
      });

      if (response.ok) {
        const result = await response.json();
        console.log(`✅ SMS sent successfully to ${recipient.name}:`, result.sid);
        return { status: 'sent' as const, timestamp: new Date() };
      } else {
        const error = await response.json();
        if (response.status === 429) {
          console.warn(`⏳ SMS rate limited for ${recipient.name} - will retry later`);
          return { status: 'failed' as const, error: 'Rate limited - try again in a few minutes' };
        }
        console.error(`❌ SMS failed for ${recipient.name}:`, error);
        return { status: 'failed' as const, error: error.error || 'API call failed' };
      }
    } catch (error) {
      console.error(`❌ SMS network error for ${recipient.name}:`, error);
      return { status: 'failed' as const, error: 'Network error' };
    }
  }

  /**
   * Intelligently select recipients based on alert characteristics
   */
  private selectRecipientsForAlert(message: AlertMessage, targetIds?: string[]): AlertRecipient[] {
    if (targetIds) {
      return this.recipients.filter(r => targetIds.includes(r.id));
    }

    let selected = [...this.recipients];

    // Filter by urgency level
    if (message.urgency === 'critical') {
      // Send to all critical and high priority contacts
      selected = selected.filter(r => r.priority === 'critical' || r.priority === 'high');
    } else if (message.urgency === 'high') {
      // Send to high and medium priority contacts
      selected = selected.filter(r => r.priority !== 'medium');
    }

    // Filter by region if specified
    if (message.region && message.region !== 'Multi-Region') {
      selected = selected.filter(r => r.region === message.region || r.region === 'Multi-Region' || r.role === 'emergency_contact');
    }

    // Always include emergency contacts for critical alerts
    if (message.urgency === 'critical') {
      const emergencyContacts = this.recipients.filter(r => r.role === 'emergency_contact');
      selected = [...selected, ...emergencyContacts].filter((r, index, arr) => 
        arr.findIndex(item => item.id === r.id) === index
      );
    }

    return selected;
  }

  /**
   * Get delivery statistics
   */
  getDeliveryStats(): { total: number; successful: number; partial: number; failed: number } {
    const total = this.deliveryHistory.length;
    const successful = this.deliveryHistory.filter(s => s.overallStatus === 'success').length;
    const partial = this.deliveryHistory.filter(s => s.overallStatus === 'partial').length;
    const failed = this.deliveryHistory.filter(s => s.overallStatus === 'failed').length;

    return { total, successful, partial, failed };
  }

  /**
   * Get recent delivery history
   */
  getRecentDeliveries(limit = 10): AlertDeliveryStatus[] {
    return this.deliveryHistory
      .sort((a, b) => (b.email?.timestamp?.getTime() || 0) - (a.email?.timestamp?.getTime() || 0))
      .slice(0, limit);
  }

  /**
   * Get all recipients
   */
  getRecipients(): AlertRecipient[] {
    return [...this.recipients];
  }

  /**
   * Test alert system with all channels
   */
  async testAlertSystem(): Promise<AlertDeliveryStatus[]> {
    const testMessage: AlertMessage = {
      id: `test-${Date.now()}`,
      title: '🧪 System Test Alert',
      message: 'This is a test of the Cameroon Defense Force alert system. All channels are being tested.',
      urgency: 'medium',
      category: 'tactical',
      timestamp: new Date()
    };

    console.log('🧪 Testing alert system across all channels...');
    return await this.sendCriticalAlert(testMessage, ['analyst-01']); // Test with one analyst
  }
}

// Create and export singleton instance
export const alertMessagingService = new AlertMessagingService();
export default alertMessagingService;

