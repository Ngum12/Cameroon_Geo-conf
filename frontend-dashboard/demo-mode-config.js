/**
 * 🎯 DEMO MODE CONFIGURATION
 * Reduces API calls for academic defense demonstration
 */

// Demo mode settings
window.DEMO_MODE = {
  enabled: true,
  
  // Rate limiting settings
  rateLimiting: {
    enabled: true,
    delayBetweenMessages: 3000, // 3 seconds between messages
    maxMessagesPerMinute: 5
  },
  
  // Channel preferences for demo
  channels: {
    preferWhatsApp: true, // WhatsApp works better than SMS
    enableSMS: false,     // Disable SMS to avoid rate limits
    enableEmail: true     // Email always works
  },
  
  // Demo messages
  messages: {
    rateLimitWarning: "⏳ Demo Mode: Spacing messages to avoid rate limits",
    successMessage: "✅ Demo Mode: Message sent successfully for defense demonstration"
  }
};

// Apply demo mode settings
if (window.DEMO_MODE.enabled) {
  console.log('🎯 DEMO MODE ACTIVATED - Optimized for academic defense');
  console.log('📱 WhatsApp preferred, SMS disabled to avoid rate limits');
  console.log('⏳ 3-second delays between messages');
}

// Export for use in other components
window.getDemoConfig = () => window.DEMO_MODE;
