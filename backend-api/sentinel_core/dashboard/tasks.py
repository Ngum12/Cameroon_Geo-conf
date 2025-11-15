"""
PROJECT SENTINEL - AUTOMATED INTELLIGENCE TASKS
Celery tasks for real-time news collection and threat analysis
Making the system ALIVE and ACTIVE with fresh intelligence daily!
"""
import os
import sys
import django
from django.conf import settings
from celery import Celery
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests
import logging
from pathlib import Path

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentinel_core.step1_settings')
django.setup()

from .models import NewsArticle
from django.utils import timezone
from django.db import transaction

# Import news scraping system
sys.path.append(str(Path(__file__).parent.parent.parent.parent / 'news-collector'))

try:
    from django_integration import AdvancedIntelligenceProcessor
    from news_scraper import NewsScrapingEngine
    from comprehensive_sources_config import COMPREHENSIVE_INTELLIGENCE_SOURCES
except ImportError as e:
    print(f"⚠️ Could not import news scraper: {e}")
    AdvancedIntelligenceProcessor = None
    NewsScrapingEngine = None
    COMPREHENSIVE_INTELLIGENCE_SOURCES = []

# Configure Celery
app = Celery('sentinel_tasks')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.task(bind=True)
def collect_fresh_intelligence(self, max_sources: int = 10):
    """
    🚀 AUTOMATED INTELLIGENCE COLLECTION TASK
    Runs the complete news scraping and processing pipeline
    Makes the system ALIVE with fresh daily intelligence!
    """
    start_time = datetime.now()
    
    logger.info("🎯 STARTING FRESH INTELLIGENCE COLLECTION")
    logger.info(f"   📅 Timestamp: {start_time}")
    logger.info(f"   🎯 Target Sources: {max_sources}")
    
    if not AdvancedIntelligenceProcessor:
        logger.error("❌ News scraping system not available")
        return {
            'success': False,
            'error': 'News scraping system not available',
            'timestamp': start_time.isoformat()
        }
    
    try:
        # Initialize the intelligence processor
        processor = AdvancedIntelligenceProcessor()
        
        # Get the current count before processing
        initial_count = NewsArticle.objects.count()
        logger.info(f"📊 Database status: {initial_count} articles before processing")
        
        # Run the complete intelligence cycle
        logger.info("🔄 Running advanced intelligence processing cycle...")
        stats = processor.run_advanced_intelligence_cycle(max_sources=max_sources)
        
        # Get final count
        final_count = NewsArticle.objects.count()
        new_articles = final_count - initial_count
        
        # Update processing statistics
        processing_time = datetime.now() - start_time
        
        result = {
            'success': True,
            'processing_stats': stats,
            'articles_added': new_articles,
            'total_articles': final_count,
            'processing_time_seconds': processing_time.total_seconds(),
            'sources_processed': stats.get('sources_processed', 0),
            'ml_predictions': stats.get('ml_predictions', 0),
            'timestamp': start_time.isoformat()
        }
        
        logger.info("✅ INTELLIGENCE COLLECTION COMPLETE!")
        logger.info(f"   📊 New Articles: {new_articles}")
        logger.info(f"   📊 Total Articles: {final_count}")
        logger.info(f"   ⏱️ Processing Time: {processing_time.total_seconds():.2f}s")
        
        # Mark recent articles for priority processing
        if new_articles > 0:
            recent_articles = NewsArticle.objects.filter(
                scraped_at__gte=start_time
            ).update(priority=1, processing_status='PENDING')
            logger.info(f"   🔝 Marked {recent_articles} articles for priority processing")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Intelligence collection failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': start_time.isoformat(),
            'processing_time_seconds': (datetime.now() - start_time).total_seconds()
        }

@app.task(bind=True)
def cleanup_old_articles(self, days_to_keep: int = 90):
    """
    🧹 CLEANUP OLD ARTICLES
    Removes articles older than specified days to keep database efficient
    """
    cutoff_date = timezone.now() - timedelta(days=days_to_keep)
    
    try:
        with transaction.atomic():
            old_articles = NewsArticle.objects.filter(scraped_at__lt=cutoff_date)
            count = old_articles.count()
            old_articles.delete()
            
        logger.info(f"🧹 Cleaned up {count} articles older than {days_to_keep} days")
        return {'success': True, 'articles_removed': count}
        
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")
        return {'success': False, 'error': str(e)}

@app.task(bind=True) 
def generate_intelligence_summary(self):
    """
    📊 GENERATE DAILY INTELLIGENCE SUMMARY
    Creates summary statistics for dashboard display
    """
    try:
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Get today's statistics
        today_articles = NewsArticle.objects.filter(scraped_at__date=today).count()
        yesterday_articles = NewsArticle.objects.filter(scraped_at__date=yesterday).count()
        total_articles = NewsArticle.objects.count()
        processed_articles = NewsArticle.objects.filter(processing_status='COMPLETED').count()
        
        # Calculate processing rate
        if total_articles > 0:
            processing_rate = (processed_articles / total_articles) * 100
        else:
            processing_rate = 0
        
        # Get priority distribution
        priority_stats = {}
        for priority in [1, 2, 3, 4, 5]:
            count = NewsArticle.objects.filter(priority=priority).count()
            priority_stats[f'priority_{priority}'] = count
        
        # Get regional distribution
        regional_stats = {}
        regions = ['Extreme-Nord', 'Sud-Ouest', 'Nord-Ouest', 'Centre', 'Littoral', 
                  'Nord', 'Adamaoua', 'Est', 'Sud', 'Ouest']
        for region in regions:
            count = NewsArticle.objects.filter(region=region).count()
            regional_stats[region.lower().replace('-', '_')] = count
        
        summary = {
            'timestamp': timezone.now().isoformat(),
            'today_articles': today_articles,
            'yesterday_articles': yesterday_articles,
            'total_articles': total_articles,
            'processed_articles': processed_articles,
            'processing_rate': round(processing_rate, 2),
            'growth_rate': today_articles - yesterday_articles,
            'priority_distribution': priority_stats,
            'regional_distribution': regional_stats
        }
        
        logger.info(f"📊 Daily Intelligence Summary Generated:")
        logger.info(f"   📈 Today: {today_articles} | Yesterday: {yesterday_articles}")
        logger.info(f"   📊 Total: {total_articles} | Processed: {processed_articles}")
        logger.info(f"   📈 Processing Rate: {processing_rate:.2f}%")
        
        return {'success': True, 'summary': summary}
        
    except Exception as e:
        logger.error(f"❌ Summary generation failed: {e}")
        return {'success': False, 'error': str(e)}

@app.task(bind=True)
def test_intelligence_sources(self):
    """
    🔍 TEST INTELLIGENCE SOURCES
    Verifies that news sources are accessible and returning data
    """
    try:
        accessible_sources = []
        failed_sources = []
        
        if COMPREHENSIVE_INTELLIGENCE_SOURCES:
            # Test a sample of sources
            test_sources = [s for s in COMPREHENSIVE_INTELLIGENCE_SOURCES if s.is_active][:5]
            
            for source in test_sources:
                try:
                    response = requests.get(source.base_url, timeout=10)
                    if response.status_code == 200:
                        accessible_sources.append(source.name)
                    else:
                        failed_sources.append(f"{source.name} (HTTP {response.status_code})")
                except Exception as e:
                    failed_sources.append(f"{source.name} ({str(e)})")
        
        result = {
            'success': True,
            'accessible_sources': accessible_sources,
            'failed_sources': failed_sources,
            'total_tested': len(accessible_sources) + len(failed_sources),
            'success_rate': len(accessible_sources) / (len(accessible_sources) + len(failed_sources)) * 100 if (accessible_sources or failed_sources) else 0
        }
        
        logger.info(f"🔍 Source Test Results:")
        logger.info(f"   ✅ Accessible: {len(accessible_sources)}")
        logger.info(f"   ❌ Failed: {len(failed_sources)}")
        logger.info(f"   📊 Success Rate: {result['success_rate']:.1f}%")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Source testing failed: {e}")
        return {'success': False, 'error': str(e)}

# Periodic task scheduling (requires Celery Beat)
from celery.schedules import crontab

app.conf.beat_schedule = {
    # 🌅 MORNING INTELLIGENCE COLLECTION (6:00 AM daily)
    'morning-intelligence-collection': {
        'task': 'sentinel_core.dashboard.tasks.collect_fresh_intelligence',
        'schedule': crontab(hour=6, minute=0),
        'args': (12,)  # Max 12 sources for morning collection
    },
    
    # 🌆 EVENING INTELLIGENCE COLLECTION (6:00 PM daily)
    'evening-intelligence-collection': {
        'task': 'sentinel_core.dashboard.tasks.collect_fresh_intelligence',
        'schedule': crontab(hour=18, minute=0),
        'args': (8,)  # Max 8 sources for evening collection
    },
    
    # 🕐 HOURLY QUICK UPDATE (every hour during business hours)
    'hourly-quick-update': {
        'task': 'sentinel_core.dashboard.tasks.collect_fresh_intelligence',
        'schedule': crontab(minute=0, hour='8-20/2'),  # Every 2 hours from 8 AM to 8 PM
        'args': (3,)  # Max 3 sources for quick updates
    },
    
    # 📊 DAILY INTELLIGENCE SUMMARY (11:30 PM daily)
    'daily-intelligence-summary': {
        'task': 'sentinel_core.dashboard.tasks.generate_intelligence_summary',
        'schedule': crontab(hour=23, minute=30),
    },
    
    # 🧹 WEEKLY CLEANUP (Sunday 2:00 AM)
    'weekly-cleanup': {
        'task': 'sentinel_core.dashboard.tasks.cleanup_old_articles',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),
        'args': (90,)  # Keep 90 days of articles
    },
    
    # 🔍 SOURCE HEALTH CHECK (Daily 5:00 AM)
    'source-health-check': {
        'task': 'sentinel_core.dashboard.tasks.test_intelligence_sources',
        'schedule': crontab(hour=5, minute=0),
    }
}

app.conf.timezone = 'UTC'

if __name__ == '__main__':
    print("🎯 PROJECT SENTINEL - AUTOMATED INTELLIGENCE SYSTEM")
    print("   This system will make your defense intelligence ALIVE and ACTIVE!")
    print("   📅 Morning Collection: 6:00 AM daily (12 sources)")
    print("   🌆 Evening Collection: 6:00 PM daily (8 sources)")
    print("   🕐 Hourly Updates: Every 2 hours (3 sources)")
    print("   📊 Daily Summary: 11:30 PM daily")
    print("   🧹 Weekly Cleanup: Sunday 2:00 AM")
    print("   🔍 Health Check: Daily 5:00 AM")




