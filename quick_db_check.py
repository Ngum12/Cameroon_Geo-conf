#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent
sys.path.append(str(project_root / 'backend-api'))
os.chdir(str(project_root / 'backend-api'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentinel_core.step1_settings')

import django
django.setup()

from sentinel_core.dashboard.models import NewsArticle
from django.utils import timezone
from datetime import timedelta

try:
    total = NewsArticle.objects.count()
    recent = NewsArticle.objects.filter(created_at__gte=timezone.now() - timedelta(hours=24)).count()
    
    print("=" * 40)
    print("📊 DATABASE STATUS CHECK")  
    print("=" * 40)
    print(f"Total Articles: {total}")
    print(f"Recent (24h): {recent}")
    
    if total > 0:
        latest = NewsArticle.objects.order_by('-created_at').first()
        print(f"Latest: {latest.title[:50]}...")
        print(f"Source: {latest.source}")
        print(f"Date: {latest.created_at}")
        print("✅ DATABASE HAS DATA!")
    else:
        print("❌ DATABASE IS STILL EMPTY")
        print("🔧 Data collection may have failed")
    
    print("=" * 40)
    
except Exception as e:
    print(f"❌ Error checking database: {e}")
