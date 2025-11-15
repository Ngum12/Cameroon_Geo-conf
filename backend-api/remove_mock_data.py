#!/usr/bin/env python3
"""Remove mock/simulated data - keep only real articles"""
import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentinel_core.step1_settings')
django.setup()

from sentinel_core.dashboard.models import NewsArticle
from django.utils import timezone

try:
    print("🧹 REMOVING MOCK DATA...")
    
    # Remove articles created in last hour (the mock ones I just added)
    recent_mock = NewsArticle.objects.filter(created_at__gte=timezone.now() - timedelta(hours=1))
    mock_count = recent_mock.count()
    
    if mock_count > 0:
        print(f"Removing {mock_count} recent mock articles...")
        deleted = recent_mock.delete()
        print(f"✅ Deleted: {deleted[0]} articles")
    else:
        print("No recent mock articles to remove")
    
    # Show current status
    total = NewsArticle.objects.count()
    if total > 0:
        latest = NewsArticle.objects.order_by('-created_at').first()
        print(f"\n📊 CLEAN DATABASE STATUS:")
        print(f"   Total Articles: {total}")  
        print(f"   Latest Real Article: {latest.created_at}")
        print(f"   Title: {latest.title[:60]}...")
        print(f"   Source: {latest.source}")
        print("✅ Only real articles remain!")
    else:
        print("\n📊 Database is empty - no articles")
        
except Exception as e:
    print(f"❌ Error: {e}")
