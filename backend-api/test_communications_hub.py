#!/usr/bin/env python3
"""
🧪 QUICK COMMUNICATIONS HUB TEST
Test Twilio integration directly to solve frontend issue
"""

import requests
import base64
import json
from datetime import datetime

# Your working Twilio credentials - using API key
TWILIO_ACCOUNT_SID = "AC40368ffce5d19d39eb9f18bd7240bd07"
TWILIO_API_KEY_SID = "SKec623ea3d1af61cff510f30a5fce100c"
TWILIO_API_KEY_SECRET = "LmJRMhyBvE7e5t0MbSF4ZBLSjFS0eGHC"
TWILIO_SMS_NUMBER = "+16054675941"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"

def send_communications_hub_message(to, message, channel='sms'):
    """Send message directly (bypassing Django for now)"""
    
    print(f"📱 COMMUNICATIONS HUB → Twilio {channel.upper()}")
    print(f"   To: {to}")
    print(f"   Message: {message[:50]}...")
    
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    
    # Base64 encode API key credentials
    credentials = f"{TWILIO_API_KEY_SID}:{TWILIO_API_KEY_SECRET}"
    auth_header = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # Set correct FROM number
    from_number = TWILIO_WHATSAPP_NUMBER if channel == 'whatsapp' else TWILIO_SMS_NUMBER
    
    message_data = {
        'From': from_number,
        'To': to,
        'Body': message
    }
    
    try:
        response = requests.post(url, headers=headers, data=message_data)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Message sent successfully!")
            print(f"   SID: {result.get('sid')}")
            print(f"   Status: {result.get('status')}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("🎯 COMMUNICATIONS HUB - TWILIO INTEGRATION TEST")
    print("="*50)
    
    # Test SMS
    sms_message = f"""🚨🇨🇲 HARMONY FLOW ALERT

🎯 THREAT: Communications Hub Integration Test
📊 LEVEL: HIGH (87%)
📍 REGION: Test Environment

Backend Twilio integration test to verify SMS and WhatsApp delivery capabilities for the Communications Hub.

⚠️ SYSTEM TEST - Integration successful

👤 TO: Defense Command Center
🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🛡️ Harmony Flow Defense System"""
    
    print("\n📱 Testing SMS...")
    sms_result = send_communications_hub_message(
        '+250792104982', 
        sms_message,
        'sms'
    )
    
    print("\n💬 Testing WhatsApp...")
    whatsapp_result = send_communications_hub_message(
        'whatsapp:+250792104982',
        sms_message,
        'whatsapp'
    )
    
    print("\n" + "="*50)
    if sms_result and whatsapp_result:
        print("🎉 COMMUNICATIONS HUB INTEGRATION WORKING!")
        print("📱 Both SMS and WhatsApp delivered successfully")
        print("🔧 Your frontend should now work with these settings")
    elif sms_result or whatsapp_result:
        print("⚠️ PARTIAL SUCCESS - At least one channel working")
    else:
        print("❌ INTEGRATION FAILED - Check credentials")
    
    print("\n💡 FRONTEND FIX:")
    print("   1. Make sure your frontend calls this exact API")
    print("   2. Use these exact credentials in your service")
    print("   3. Test with the HTML file I created")
    
    print("\n📞 Check your phone for messages!")


