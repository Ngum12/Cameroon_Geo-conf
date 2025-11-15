# Project Sentinel - Step 1 URLs
# Django URL routing for Step 1

from django.contrib import admin
from django.urls import path, include
from .dashboard.step1_views import health_check, get_events, get_statistics, process_article

# Import Twilio views
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from twilio_api import send_twilio_message, twilio_status, test_twilio_integration

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('api/v1/events/', get_events, name='get_events'),
    path('api/v1/statistics/', get_statistics, name='get_statistics'),
    path('api/v1/process-article/', process_article, name='process_article'),
    
    # Twilio integration endpoints
    path('api/v1/twilio/send-message', send_twilio_message, name='twilio_send_message'),
    path('api/v1/twilio/status', twilio_status, name='twilio_status'),
    path('api/v1/twilio/test', test_twilio_integration, name='twilio_test'),
]









