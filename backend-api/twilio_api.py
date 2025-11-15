#!/usr/bin/env python3
"""
🎯 TWILIO API ENDPOINT - Backend Integration
Handle Twilio SMS/WhatsApp requests from frontend
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import requests
import base64
from datetime import datetime

# Twilio credentials (from your setup)
TWILIO_ACCOUNT_SID = "AC40368ffce5d19d39eb9f18bd7240bd07"
TWILIO_AUTH_TOKEN = "7109ed26d66ec1ccddf9f3a8e00e5158"
TWILIO_SMS_NUMBER = "+16054675941"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"

@csrf_exempt
@require_http_methods(["POST"])
def send_twilio_message(request):
    """Send SMS or WhatsApp message via Twilio API"""
    
    try:
        # Parse request data
        data = json.loads(request.body)
        
        to = data.get('to')
        body = data.get('body')
        channel = data.get('channel', 'sms')
        
        if not to or not body:
            return JsonResponse({
                'error': 'Missing required fields (to, body)'
            }, status=400)
        
        # Prepare Twilio API call
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
        
        # Base64 encode credentials
        credentials = f"{TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}"
        auth_header = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Set correct FROM number based on channel
        from_number = TWILIO_WHATSAPP_NUMBER if channel == 'whatsapp' else TWILIO_SMS_NUMBER
        
        # Prepare message data
        message_data = {
            'From': from_number,
            'To': to,
            'Body': body
        }
        
        print(f"📱 Sending {channel.upper()} to {to}")
        print(f"📞 From: {from_number}")
        
        # Make Twilio API call
        response = requests.post(url, headers=headers, data=message_data)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Message sent successfully - SID: {result.get('sid')}")
            
            return JsonResponse({
                'success': True,
                'sid': result.get('sid'),
                'status': result.get('status'),
                'to': result.get('to'),
                'from': result.get('from'),
                'date_created': result.get('date_created'),
                'price': result.get('price'),
                'channel': channel
            })
        
        else:
            error_data = response.json() if response.content else {}
            print(f"❌ Twilio API error: {response.status_code} - {error_data}")
            
            return JsonResponse({
                'error': f"Twilio API error: {response.status_code}",
                'details': error_data
            }, status=response.status_code)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body'
        }, status=400)
    
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return JsonResponse({
            'error': f'Network error: {str(e)}'
        }, status=500)
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return JsonResponse({
            'error': f'Server error: {str(e)}'
        }, status=500)

@csrf_exempt  
@require_http_methods(["GET"])
def twilio_status(request):
    """Get Twilio service status"""
    
    return JsonResponse({
        'service': 'Twilio Integration',
        'status': 'operational',
        'account_sid': TWILIO_ACCOUNT_SID,
        'sms_number': TWILIO_SMS_NUMBER,
        'whatsapp_number': TWILIO_WHATSAPP_NUMBER,
        'timestamp': datetime.now().isoformat()
    })

# Test endpoint
@csrf_exempt
@require_http_methods(["POST"])
def test_twilio_integration(request):
    """Test Twilio integration with demo message"""
    
    # Demo message to your number
    demo_data = {
        'to': '+250792104982',  # Your number from screenshot
        'body': '🧪 TWILIO TEST from Harmony Flow Platform\n\nFrontend → Backend → Twilio API\n\n✅ Integration working successfully!',
        'channel': 'sms'
    }
    
    # Use the same send function
    test_request = type('TestRequest', (), {
        'body': json.dumps(demo_data).encode(),
        'method': 'POST'
    })()
    
    return send_twilio_message(test_request)


