#!/usr/bin/env python3
"""
🧪 QUICK TWILIO BACKEND TEST
Test the Twilio integration directly
"""

import requests
import base64
import json

# Twilio credentials
TWILIO_ACCOUNT_SID = "AC40368ffce5d19d39eb9f18bd7240bd07"
TWILIO_AUTH_TOKEN = "7109ed26d66ec1ccddf9f3a8e00e5158"
TWILIO_SMS_NUMBER = "+16054675941"

def test_direct_twilio():
    """Test Twilio API directly"""
    
    print("🧪 Testing direct Twilio API connection...")
    
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    
    # Base64 encode credentials
    credentials = f"{TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}"
    auth_header = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    message_data = {
        'From': TWILIO_SMS_NUMBER,
        'To': '+250792104982',  # Your number
        'Body': '🧪 BACKEND TEST from Harmony Flow\n\nFrontend integration test successful!\n\n✅ Backend → Twilio API working'
    }
    
    try:
        response = requests.post(url, headers=headers, data=message_data)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ SMS sent successfully!")
            print(f"   Message SID: {result.get('sid')}")
            print(f"   Status: {result.get('status')}")
            print(f"   To: {result.get('to')}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("🎯 HARMONY FLOW - BACKEND TWILIO TEST")
    print("="*45)
    
    success = test_direct_twilio()
    
    if success:
        print("\n🎉 Backend integration working!")
        print("📱 Check your phone for test message")
        print("🔧 Now the frontend should work too")
    else:
        print("\n❌ Backend test failed")
        print("🔍 Check credentials and network connection")


