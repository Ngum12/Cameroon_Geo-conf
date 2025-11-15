// 🔧 TWILIO SETUP FOR FRONTEND
// Add this to your main App.tsx or initialization file

import { defenseIntegrationService } from './services/defenseIntegrationService';

// Initialize Twilio when app starts
export const initializeTwilioIntegration = () => {
  console.log('🔧 Initializing Twilio integration...');
  
  const twilioConfig = {
    accountSid: 'AC40368ffce5d19d39eb9f18bd7240bd07',
    authToken: '7109ed26d66ec1ccddf9f3a8e00e5158',
    smsNumber: '+16054675941',
    whatsappNumber: 'whatsapp:+14155238886'
  };
  
  // Configure Twilio integration
  defenseIntegrationService.configureTwilio(twilioConfig);
  
  console.log('📱 Twilio integration activated for frontend');
};

// Test the integration
export const testTwilioFromFrontend = async () => {
  console.log('🧪 Testing Twilio from frontend...');
  
  try {
    // Test backend API endpoint
    const response = await fetch('/api/v1/twilio/test', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const result = await response.json();
      console.log('✅ Frontend → Backend → Twilio test successful:', result);
      alert('🎉 Twilio integration working! Check your phone for test message.');
      return true;
    } else {
      console.error('❌ Test failed:', response.status);
      alert('❌ Test failed. Check console for details.');
      return false;
    }
  } catch (error) {
    console.error('❌ Test error:', error);
    alert('❌ Network error. Make sure backend is running.');
    return false;
  }
};

// Send custom message from frontend
export const sendCustomTwilioMessage = async (to: string, message: string, channel: 'sms' | 'whatsapp' = 'sms') => {
  console.log(`📱 Sending ${channel} message from frontend...`);
  
  try {
    const response = await fetch('/api/v1/twilio/send-message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        to: to,
        body: message,
        channel: channel
      })
    });
    
    if (response.ok) {
      const result = await response.json();
      console.log(`✅ ${channel.toUpperCase()} sent successfully:`, result);
      return result;
    } else {
      const error = await response.json();
      console.error(`❌ ${channel.toUpperCase()} failed:`, error);
      throw new Error(error.error || 'Send failed');
    }
  } catch (error) {
    console.error(`❌ Send error:`, error);
    throw error;
  }
};


