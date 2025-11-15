#!/usr/bin/env python3
"""Test database connection and schema"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentinel_core.step1_settings')
django.setup()

from sentinel_core.dashboard.models import NewsArticle
from django.utils import timezone

try:
    print("🔍 Testing database connection...")
    
    # Test basic query
    total = NewsArticle.objects.count()
    print(f"✅ Total articles: {total}")
    
    # Test recent articles
    recent_24h = NewsArticle.objects.filter(created_at__gte=timezone.now() - timedelta(hours=24)).count()
    recent_7d = NewsArticle.objects.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()
    
    print(f"📊 Recent articles:")
    print(f"   Last 24 hours: {recent_24h}")
    print(f"   Last 7 days: {recent_7d}")
    
    # Get latest article info
    if total > 0:
        latest = NewsArticle.objects.order_by('-created_at').first()
        print(f"🔍 Latest article:")
        print(f"   Title: {latest.title[:60]}...")
        print(f"   Source: {latest.source}")
        print(f"   Date: {latest.created_at}")
        print(f"   Priority: {latest.priority}")
        
        # Check when articles stop
        old_count = NewsArticle.objects.filter(created_at__lt=timezone.now() - timedelta(days=1)).count()
        print(f"📅 Older than 24h: {old_count}")
    
    print("✅ Database schema is working correctly!")
    
    # Test if we can create a new article
    test_article = NewsArticle(
        title="Test Article - " + str(datetime.now()),
        raw_text="This is a test article to verify database write capabilities.",
        url=f"http://test.com/article-{int(timezone.now().timestamp())}",
        source="Test Source",
        published_date=timezone.now(),
        priority=3,
        classification="test"
    )
    test_article.save()
    print("✅ Can write new articles to database!")
    
    # Delete test article
    test_article.delete()
    print("✅ Database write/delete working!")
    
except Exception as e:
    print(f"❌ Database error: {e}")
    import traceback
    traceback.print_exc()
