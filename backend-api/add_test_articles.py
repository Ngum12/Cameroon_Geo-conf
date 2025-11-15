#!/usr/bin/env python3
"""Add test articles to database for frontend testing"""
import os
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentinel_core.settings')
django.setup()

from sentinel_core.dashboard.models import NewsArticle
from django.utils import timezone

def create_test_articles():
    """Create test articles with various statuses and dates"""
    
    test_articles = [
        {
            'title': '🚨 Security Forces Deploy to Northwest Region',
            'raw_text': 'Security forces have been deployed to the Northwest region following reports of increased tensions in Bamenda and surrounding areas. Local authorities report heightened security measures.',
            'url': 'https://cameroon-tribune.cm/article-1',
            'source': 'Cameroon Tribune',
            'published_date': timezone.now() - timedelta(hours=2),
            'priority': 1,  # Critical
            'classification': 'security',
            'language': 'en',
            'latitude': 5.9597,
            'longitude': 10.1492,
            'processing_status': 'COMPLETED',
            'sentiment_score': -0.7,
            'relevance_score': 95.0,
            'content_length': 245,
            'word_count': 42
        },
        {
            'title': '📊 Economic Development in Douala Port Area',
            'raw_text': 'The port of Douala continues to see significant economic development with new infrastructure projects announced by the government. Business leaders express optimism.',
            'url': 'https://business-cameroon.cm/article-2', 
            'source': 'Business in Cameroon',
            'published_date': timezone.now() - timedelta(hours=6),
            'priority': 3,  # Medium
            'classification': 'economic',
            'language': 'en',
            'latitude': 4.0511,
            'longitude': 9.7679,
            'processing_status': 'COMPLETED',
            'sentiment_score': 0.6,
            'relevance_score': 75.0,
            'content_length': 198,
            'word_count': 35
        },
        {
            'title': '🔄 Manifestation à Yaoundé pour les Salaires',
            'raw_text': 'Des manifestations pacifiques ont eu lieu à Yaoundé concernant les retards de salaires dans le secteur public. Les autorités appellent au dialogue.',
            'url': 'https://journal-cameroun.fr/article-3',
            'source': 'Journal du Cameroun', 
            'published_date': timezone.now() - timedelta(hours=12),
            'priority': 2,  # High
            'classification': 'social',
            'language': 'fr',
            'latitude': 3.8480,
            'longitude': 11.5021,
            'processing_status': 'COMPLETED',
            'sentiment_score': -0.3,
            'relevance_score': 80.0,
            'content_length': 167,
            'word_count': 28
        },
        {
            'title': '⚡ Power Outages Affect Far North Region',
            'raw_text': 'Extended power outages in the Far North region are affecting daily life and business operations. ENEO promises quick restoration of service.',
            'url': 'https://237actu.cm/article-4',
            'source': '237actu',
            'published_date': timezone.now() - timedelta(hours=18),
            'priority': 3,  # Medium
            'classification': 'infrastructure',
            'language': 'en', 
            'latitude': 10.5910,
            'longitude': 14.2086,
            'processing_status': 'COMPLETED',
            'sentiment_score': -0.4,
            'relevance_score': 65.0,
            'content_length': 156,
            'word_count': 28
        },
        {
            'title': '🏥 New Healthcare Facilities in Southwest',
            'raw_text': 'The government announces new healthcare facilities to be built in the Southwest region, improving medical services for local populations.',
            'url': 'https://camer.be/article-5',
            'source': 'Camer.be',
            'published_date': timezone.now() - timedelta(hours=24),
            'priority': 4,  # Low
            'classification': 'healthcare', 
            'language': 'en',
            'latitude': 4.1395,
            'longitude': 9.2675,
            'processing_status': 'COMPLETED',
            'sentiment_score': 0.8,
            'relevance_score': 70.0,
            'content_length': 134,
            'word_count': 24
        },
        {
            'title': '⏳ Breaking: Tensions Rise in Anglophone Regions',
            'raw_text': 'Recent developments in the Anglophone crisis show escalating tensions. Security analysts warn of potential instability.',
            'url': 'https://cameroon-intelligence.com/article-6',
            'source': 'Cameroon Intelligence Report',
            'published_date': timezone.now() - timedelta(minutes=30),
            'priority': 1,  # Critical
            'classification': 'security',
            'language': 'en',
            'latitude': 5.4500,
            'longitude': 10.2900,
            'processing_status': 'PROCESSING',
            'sentiment_score': -0.9,
            'relevance_score': 98.0,
            'content_length': 123,
            'word_count': 21
        },
        {
            'title': '📅 Recent Article Processing Queue',
            'raw_text': 'This is a pending article that demonstrates the processing queue functionality of the system.',
            'url': 'https://test-source.cm/article-7',
            'source': 'Test Source',
            'published_date': timezone.now() - timedelta(minutes=15),
            'priority': 4,
            'classification': 'general',
            'language': 'en',
            'processing_status': 'PENDING',
            'sentiment_score': 0.0,
            'relevance_score': 30.0,
            'content_length': 89,
            'word_count': 16
        }
    ]
    
    # Create articles
    created_count = 0
    for article_data in test_articles:
        try:
            # Check if article already exists
            if NewsArticle.objects.filter(url=article_data['url']).exists():
                print(f"⏭️  Article already exists: {article_data['title'][:50]}...")
                continue
                
            # Create new article
            article = NewsArticle.objects.create(**article_data)
            print(f"✅ Created: {article.title[:50]}... (Priority: {article.priority}, Status: {article.processing_status})")
            created_count += 1
            
        except Exception as e:
            print(f"❌ Error creating article: {e}")
    
    print(f"\n🎉 SUCCESS: Created {created_count} new test articles!")
    
    # Show current statistics
    total = NewsArticle.objects.count()
    completed = NewsArticle.objects.filter(processing_status='COMPLETED').count()
    pending = NewsArticle.objects.filter(processing_status='PENDING').count() 
    processing = NewsArticle.objects.filter(processing_status='PROCESSING').count()
    
    recent_24h = NewsArticle.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    print(f"\n📊 UPDATED STATISTICS:")
    print(f"   Total Articles: {total}")
    print(f"   Completed: {completed}")
    print(f"   Processing: {processing}")
    print(f"   Pending: {pending}")
    print(f"   Recent (24h): {recent_24h}")

if __name__ == '__main__':
    create_test_articles()
