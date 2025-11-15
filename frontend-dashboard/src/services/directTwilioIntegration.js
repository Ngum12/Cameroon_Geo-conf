// 🔧 DIRECT TWILIO INTEGRATION FOR COMMUNICATIONS HUB
// Add this to your Communications Hub component

const sendDirectTwilioMessage = async (to, message, channel = 'sms') => {
  console.log(`📱 Sending ${channel} directly via Twilio...`);
  
  // Your working credentials
  const accountSid = 'AC40368ffce5d19d39eb9f18bd7240bd07';
  const authToken = '7109ed26d66ec1ccddf9f3a8e00e5158';
  const smsNumber = '+16054675941';
  const whatsappNumber = 'whatsapp:+14155238886';
  
  const url = `https://api.twilio.com/2010-04-01/Accounts/${accountSid}/Messages.json`;
  
  // Base64 encode credentials
  const credentials = btoa(`${accountSid}:${authToken}`);
  
  const fromNumber = channel === 'whatsapp' ? whatsappNumber : smsNumber;
  
  const formData = new URLSearchParams();
  formData.append('From', fromNumber);
  formData.append('To', to);
  formData.append('Body', message);
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData
    });
    
    if (response.ok) {
      const result = await response.json();
      console.log(`✅ ${channel.toUpperCase()} sent successfully!`, result.sid);
      
      // Show success message in your UI
      alert(`🎉 ${channel.toUpperCase()} message sent successfully!\nMessage SID: ${result.sid}\n\nCheck your phone!`);
      
      return { success: true, sid: result.sid, status: result.status };
    } else {
      const error = await response.json();
      console.error(`❌ ${channel.toUpperCase()} failed:`, error);
      alert(`❌ Failed to send ${channel}: ${error.message}`);
      return { success: false, error: error.message };
    }
  } catch (error) {
    console.error(`❌ Network error:`, error);
    alert(`❌ Network error: ${error.message}`);
    return { success: false, error: error.message };
  }
};

// Usage in your Communications Hub:
const handleSendAlert = async () => {
  const phoneNumber = '+250792104982'; // Your test number
  const alertMessage = `🚨🇨🇲 CAMEROON DEFENSE ALERT

🎯 THREAT: ${threatTitle}
📊 LEVEL: ${threatLevel}%
📍 REGION: ${region}

${alertDescription}

⚠️ SENT FROM COMMUNICATIONS HUB

👤 TO: Defense Command
🕒 ${new Date().toLocaleString()}

🛡️ Harmony Flow Defense System`;

  // Send both SMS and WhatsApp
  const smsResult = await sendDirectTwilioMessage(phoneNumber, alertMessage, 'sms');
  const whatsappResult = await sendDirectTwilioMessage(`whatsapp:${phoneNumber}`, alertMessage, 'whatsapp');
  
  if (smsResult.success || whatsappResult.success) {
    console.log('🎉 Alert sent successfully!');
  }
};


