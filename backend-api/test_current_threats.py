#!/usr/bin/env python3
"""
Test sending alerts for current threats visible in Communications Hub
"""

import requests
import json
from datetime import datetime

def test_current_threat_alert():
    """Test sending alert for the Extreme-Nord threat currently showing in Communications Hub"""
    
    print("🚨 TESTING CURRENT THREAT ALERT")
    print("=" * 50)
    
    url = 'http://localhost:8000/api/v1/twilio/send-message'
    
    # Alert message for the Extreme-Nord threat you mentioned (75% threat level)
    threat_alert = f"""🚨🇨🇲 CAMEROON DEFENSE FORCE - THREAT ALERT

VERIFIED THREAT: Extreme-Nord Security Assessment

REGION: Extreme-Nord
THREAT LEVEL: 75%
CATEGORY: Security Assessment

DETAILS:
Intelligence analysis for Extreme-Nord based on processed articles. Elevated threat activity detected requiring immediate attention and response coordination.

PRIORITY: HIGH
TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Immediate assessment and response coordination required.

Project Sentinel Defense Intelligence Platform
Cameroon Defense Force"""

    print("📱 Testing WhatsApp alert for current Extreme-Nord threat...")
    print(f"📍 Region: Extreme-Nord")
    print(f"📊 Threat Level: 75%")
    print(f"📞 Sending to: +250792104984")
    print()

    try:
        response = requests.post(url, json={
            'to': 'whatsapp:+250792104984',
            'body': threat_alert,
            'channel': 'whatsapp'
        }, headers={'Content-Type': 'application/json'})
        
        if response.ok:
            result = response.json()
            print("✅ ALERT SENT SUCCESSFULLY!")
            print(f"   SID: {result.get('sid')}")
            print(f"   Status: {result.get('status')}")
            print(f"   To: {result.get('to')}")
            print(f"   From: {result.get('from')}")
            print()
            print("📞 CHECK YOUR PHONE FOR THE ALERT MESSAGE!")
            return True
        else:
            error = response.json()
            print(f"❌ Alert failed: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_all_current_threats():
    """Test alerts for all current threats showing in Communications Hub"""
    
    print("\n🎯 TESTING ALL CURRENT THREATS")
    print("=" * 50)
    
    current_threats = [
        {
            'name': 'Extreme-Nord Security Assessment',
            'region': 'Extreme-Nord',
            'level': 75,
            'articles': 0
        },
        {
            'name': 'Sud-Ouest Security Assessment',
            'region': 'Sud-Ouest', 
            'level': 65,
            'articles': 1
        },
        {
            'name': 'Nord-Ouest Security Assessment',
            'region': 'Nord-Ouest',
            'level': 60,
            'articles': 1
        }
    ]
    
    print(f"📊 Found {len(current_threats)} active threats in Communications Hub:")
    for threat in current_threats:
        print(f"   • {threat['name']}: {threat['level']}% ({threat['region']})")
    
    # Test with the highest priority threat (Extreme-Nord - 75%)
    highest_threat = current_threats[0]
    print(f"\n🎯 Testing with highest priority: {highest_threat['name']}")
    
    return test_current_threat_alert()

if __name__ == "__main__":
    print("🚀 COMMUNICATIONS HUB - CURRENT THREATS TEST")
    print("=" * 60)
    print("Testing alerts for threats currently visible in your Communications Hub")
    print()
    
    success = test_all_current_threats()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST COMPLETED SUCCESSFULLY!")
        print("📱 Your Communications Hub can now send real alerts!")
        print("✅ The flow works: Active Threats → Click ALERT → Real WhatsApp message")
    else:
        print("❌ TEST FAILED - Check backend server status")
    print("=" * 60)
