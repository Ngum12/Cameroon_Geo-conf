#!/usr/bin/env python3
"""
🔄 CONTINUOUS NEWS MONITORING SERVICE
Automatically check Cameroon news sources every 30 minutes and update database
"""
import os
import django
import time
import threading
import schedule
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentinel_core.minimal_settings')
django.setup()

from real_news_scraper import scrape_real_news
from sentinel_core.dashboard.models import NewsArticle

class ContinuousNewsMonitor:
    """Background service for continuous news monitoring with temporal data analysis"""
    
    def __init__(self):
        self.running = False
        self.last_check = None
        self.total_collected = 0
        
        # Temporal analysis periods
        self.temporal_periods = {
            '7_days': 7,
            '1_month': 30, 
            '3_months': 90
        }
    
    def check_and_collect(self):
        """MIGHTY data collection - Check sources and collect new articles"""
        try:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🌍 ENHANCED GEOPOLITICAL INTELLIGENCE: Scanning 45+ sophisticated sources...")
            
            # Get current article count
            before_count = NewsArticle.objects.count()
            
            # Run enhanced scraper
            new_articles = scrape_real_news()
            
            # Check results
            after_count = NewsArticle.objects.count()
            newly_added = after_count - before_count
            
            if newly_added > 0:
                print(f"SUCCESS: Collected {newly_added} new articles from live sources!")
                print(f"DATABASE: Total articles now {after_count}")
                print(f"PIPELINE: {self.total_collected + newly_added} articles collected since start")
                self.total_collected += newly_added
                
                # Perform temporal data analysis
                self.analyze_temporal_data()
                
                # Trigger ML processing for new articles with temporal context
                self.trigger_ml_processing_with_temporal_data(newly_added)
            else:
                print("MONITORING: All sources current - no new articles")
            
            self.last_check = datetime.now()
            
        except Exception as e:
            print(f"ERROR: Monitoring cycle failed: {e}")
    
    def analyze_temporal_data(self):
        """Analyze data across temporal periods (7 days, 1 month, 3 months)"""
        try:
            print("📊 TEMPORAL DATA ANALYSIS:")
            
            for period_name, days in self.temporal_periods.items():
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Get articles for this period
                articles_in_period = NewsArticle.objects.filter(
                    created_at__gte=cutoff_date
                ).count()
                
                # Get regional distribution
                regional_data = {}
                for region in ['Extreme-Nord', 'Sud-Ouest', 'Nord-Ouest', 'Centre', 'Littoral', 'Nord', 'Adamaoua', 'Est', 'Sud', 'Ouest']:
                    region_count = NewsArticle.objects.filter(
                        created_at__gte=cutoff_date,
                        raw_text__icontains=region
                    ).count()
                    if region_count > 0:
                        regional_data[region] = region_count
                
                print(f"  📅 {period_name.replace('_', ' ').title()}: {articles_in_period} articles")
                if regional_data:
                    top_regions = sorted(regional_data.items(), key=lambda x: x[1], reverse=True)[:3]
                    print(f"     Top regions: {', '.join([f'{r}({c})' for r, c in top_regions])}")
                    
        except Exception as e:
            print(f"❌ Temporal analysis error: {e}")
    
    def trigger_ml_processing_with_temporal_data(self, new_count):
        """Enhanced ML processing with temporal context"""
        try:
            import requests
            
            # Gather temporal context for ML
            temporal_context = {}
            for period_name, days in self.temporal_periods.items():
                cutoff_date = datetime.now() - timedelta(days=days)
                count = NewsArticle.objects.filter(created_at__gte=cutoff_date).count()
                temporal_context[period_name] = count
            
            # Call ML API with temporal context
            ml_payload = {
                'limit': new_count,
                'temporal_context': temporal_context,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            response = requests.post('http://localhost:8001/predict_batch', 
                                   json=ml_payload, 
                                   timeout=10)
            if response.status_code == 200:
                print(f"🤖 ML PROCESSING: Analyzed {new_count} new articles with temporal context")
                print(f"   📊 Context: 7d({temporal_context.get('7_days', 0)}) 1m({temporal_context.get('1_month', 0)}) 3m({temporal_context.get('3_months', 0)})")
            else:
                print(f"❌ ML PROCESSING: API call failed - {response.status_code}")
        except Exception as e:
            print(f"❌ ML PROCESSING: Error - {e}")
    
    def trigger_ml_processing(self, new_count):
        """Legacy ML processing method (kept for compatibility)"""
        try:
            import requests
            # Call ML API for processing
            response = requests.post('http://localhost:8001/predict_batch', 
                                   json={'limit': new_count}, 
                                   timeout=10)
            if response.status_code == 200:
                print(f"ML PROCESSING: Analyzed {new_count} new articles")
            else:
                print(f"ML PROCESSING: API call failed - {response.status_code}")
        except Exception as e:
            print(f"ML PROCESSING: Error - {e}")
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        print("🚀 STARTING SOPHISTICATED GEOPOLITICAL INTELLIGENCE SYSTEM")
        print("=" * 80)
        print("🌍 COMPREHENSIVE GLOBAL COVERAGE:")
        print("   📍 All 10 Cameroon Regions (Extreme-Nord → Sud)")
        print("   📡 45+ Premium Intelligence Sources")
        print("   🎯 6-Tier Sophisticated Source Hierarchy")
        print("")
        print("📊 INTELLIGENCE ARCHITECTURE:")
        print("   🏛️  Tier 1: Official Government & Defense Sources")
        print("   🗺️  Tier 2: Complete Regional Coverage (10 Regions)")
        print("   🌍 Tier 3: Pan-African Geopolitical Intelligence")
        print("   🔒 Tier 4: International Security Monitoring")
        print("   🎯 Tier 5: Specialized Conflict Analysis")
        print("   💼 Tier 6: Economic & Resource Intelligence")
        print("")
        print("🔍 ENHANCED CAPABILITIES:")
        print("   • Regional Priority Mapping (Critical/High/Medium)")
        print("   • Advanced Geopolitical Keyword Analysis")
        print("   • International Relations Monitoring")
        print("   • Multi-tier Security Threat Classification")
        print("   • Temporal Analysis: 7d/1m/3m data collection")
        print("   • ML Integration: Real-time context processing")
        print("")
        print("🔄 AUTO-MONITORING: Every 30 minutes | Press Ctrl+C to stop")
        print("=" * 80)
        
        # Schedule checks every 30 minutes
        schedule.every(30).minutes.do(self.check_and_collect)
        
        # Run initial check
        self.check_and_collect()
        
        self.running = True
        
        # Keep running
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute for scheduled tasks
                
                # Show enhanced status every 10 minutes
                if datetime.now().minute % 10 == 0:
                    current_total = NewsArticle.objects.count()
                    recent_24h = NewsArticle.objects.filter(
                        created_at__gte=datetime.now() - timedelta(hours=24)
                    ).count()
                    recent_7d = NewsArticle.objects.filter(
                        created_at__gte=datetime.now() - timedelta(days=7)
                    ).count()
                    recent_30d = NewsArticle.objects.filter(
                        created_at__gte=datetime.now() - timedelta(days=30)
                    ).count()
                    
                    print(f"📊 TEMPORAL STATUS: Total({current_total}) | 24h({recent_24h}) | 7d({recent_7d}) | 30d({recent_30d})")
                    if self.last_check:
                        print(f"🕐 Last check: {self.last_check.strftime('%H:%M:%S')}")
                    
                    # Show data growth trends
                    if recent_30d > 0:
                        growth_7d = (recent_7d / recent_30d) * 100 if recent_30d > 0 else 0
                        print(f"📈 Data trends: 7-day activity represents {growth_7d:.1f}% of 30-day volume")
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                self.running = False
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(60)  # Wait before retrying
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        print("🛑 Continuous monitoring stopped")

# Quick setup function
def setup_quick_monitoring():
    """Set up monitoring with 10-minute intervals for testing"""
    print("⚡ QUICK MONITORING MODE (10-minute intervals)")
    
    def quick_check():
        try:
            print(f"\n⚡ [{datetime.now().strftime('%H:%M:%S')}] Quick check...")
            
            before = NewsArticle.objects.count()
            scrape_real_news()
            after = NewsArticle.objects.count()
            
            if after > before:
                print(f"✅ Found {after - before} new articles!")
            else:
                print("📰 No new articles")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Schedule every 10 minutes for testing
    schedule.every(10).minutes.do(quick_check)
    
    print("🚀 Quick monitoring started - checking every 10 minutes")
    print("🔄 Press Ctrl+C to stop")
    
    # Run initial check
    quick_check()
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Quick monitoring stopped")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        # Quick mode for testing (10-minute intervals)
        setup_quick_monitoring()
    else:
        # Normal mode (30-minute intervals)
        monitor = ContinuousNewsMonitor()
        monitor.start_monitoring()
