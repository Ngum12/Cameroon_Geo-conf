#!/usr/bin/env python3
"""
🚀 LONG-TERM DATA COLLECTION STRATEGY
Implements the next phase recommendations for 30-day collection
"""
import os
import django
import time
import schedule
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentinel_core.minimal_settings')
django.setup()

from continuous_news_monitor import ContinuousNewsMonitor
from real_news_scraper import scrape_real_news
from sentinel_core.dashboard.models import NewsArticle

class LongTermCollectionStrategy:
    """Enhanced collection strategy for 30-day ML dataset building"""
    
    def __init__(self):
        self.monitor = ContinuousNewsMonitor()
        self.collection_goals = {
            'daily_target': 5,      # 5 articles per day
            'weekly_target': 35,    # 35 articles per week  
            'monthly_target': 150,  # 150 articles per month
            'regional_balance': {   # Target distribution
                'Nord-Ouest': 0.20,    # 20% (conflict zone)
                'Sud-Ouest': 0.20,     # 20% (conflict zone)
                'Extreme-Nord': 0.15,  # 15% (terrorism)
                'Est': 0.10,           # 10% (CAR spillover)
                'Nord': 0.10,          # 10% (farmer conflicts)
                'Centre': 0.10,        # 10% (political)
                'Other': 0.15          # 15% (other regions)
            }
        }
        
    def assess_collection_progress(self):
        """Assess progress toward collection goals"""
        try:
            print("\n📊 LONG-TERM COLLECTION PROGRESS ASSESSMENT")
            print("=" * 60)
            
            # Get temporal data
            now = datetime.now()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # Count articles by period
            total_articles = NewsArticle.objects.count()
            daily_articles = NewsArticle.objects.filter(created_at__gte=today).count()
            weekly_articles = NewsArticle.objects.filter(created_at__gte=week_ago).count()
            monthly_articles = NewsArticle.objects.filter(created_at__gte=month_ago).count()
            
            print(f"📈 PROGRESS METRICS:")
            print(f"   📅 Today: {daily_articles}/{self.collection_goals['daily_target']} articles ({(daily_articles/self.collection_goals['daily_target']*100):.1f}%)")
            print(f"   📅 This week: {weekly_articles}/{self.collection_goals['weekly_target']} articles ({(weekly_articles/self.collection_goals['weekly_target']*100):.1f}%)")
            print(f"   📅 This month: {monthly_articles}/{self.collection_goals['monthly_target']} articles ({(monthly_articles/self.collection_goals['monthly_target']*100):.1f}%)")
            print(f"   📊 Total dataset: {total_articles} articles")
            
            # Regional balance assessment
            print(f"\n🌍 REGIONAL BALANCE ASSESSMENT:")
            regions = ['Nord-Ouest', 'Sud-Ouest', 'Extreme-Nord', 'Est', 'Nord', 'Centre']
            
            for region in regions:
                count = NewsArticle.objects.filter(
                    created_at__gte=month_ago,
                    raw_text__icontains=region
                ).count()
                
                target_count = int(monthly_articles * self.collection_goals['regional_balance'].get(region, 0.05))
                percentage = (count / monthly_articles * 100) if monthly_articles > 0 else 0
                target_percentage = self.collection_goals['regional_balance'].get(region, 0.05) * 100
                
                status = "✅" if percentage >= target_percentage * 0.8 else "⚠️" if percentage >= target_percentage * 0.5 else "❌"
                print(f"   {status} {region}: {count} articles ({percentage:.1f}% | target: {target_percentage:.1f}%)")
            
            # ML readiness assessment
            print(f"\n🤖 ML TRAINING READINESS:")
            ml_ready_threshold = 50  # Minimum for robust ML training
            
            if total_articles >= ml_ready_threshold:
                print(f"   ✅ Dataset size: {total_articles} articles (READY for ML training)")
            else:
                needed = ml_ready_threshold - total_articles
                print(f"   ⚠️ Dataset size: {total_articles} articles (need {needed} more for robust ML)")
            
            # Data quality metrics
            with_content = NewsArticle.objects.exclude(raw_text__isnull=True).exclude(raw_text='').count()
            content_quality = (with_content / total_articles * 100) if total_articles > 0 else 0
            
            print(f"   📝 Content quality: {content_quality:.1f}% ({with_content}/{total_articles})")
            
            # Recommendations
            print(f"\n🎯 RECOMMENDATIONS:")
            if daily_articles < self.collection_goals['daily_target']:
                print(f"   📈 Increase daily collection: Need {self.collection_goals['daily_target'] - daily_articles} more articles today")
            
            # Find underrepresented regions
            underrepresented = []
            for region in regions:
                count = NewsArticle.objects.filter(
                    created_at__gte=month_ago,
                    raw_text__icontains=region
                ).count()
                target_count = int(monthly_articles * self.collection_goals['regional_balance'].get(region, 0.05))
                if count < target_count * 0.8:
                    underrepresented.append(region)
            
            if underrepresented:
                print(f"   🎯 Focus on regions: {', '.join(underrepresented)}")
            
            return {
                'total_articles': total_articles,
                'daily_progress': daily_articles / self.collection_goals['daily_target'],
                'weekly_progress': weekly_articles / self.collection_goals['weekly_target'],
                'monthly_progress': monthly_articles / self.collection_goals['monthly_target'],
                'ml_ready': total_articles >= ml_ready_threshold,
                'content_quality': content_quality
            }
            
        except Exception as e:
            print(f"❌ Progress assessment error: {e}")
            return {}
    
    def run_enhanced_collection_cycle(self):
        """Run enhanced collection with progress tracking"""
        try:
            print(f"\n🔄 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ENHANCED COLLECTION CYCLE")
            print("=" * 70)
            
            # Assess current progress
            progress = self.assess_collection_progress()
            
            # Run collection
            print(f"\n📡 Starting enhanced regional news collection...")
            before_count = NewsArticle.objects.count()
            
            # Run the enhanced scraper
            scrape_real_news()
            
            after_count = NewsArticle.objects.count()
            newly_collected = after_count - before_count
            
            if newly_collected > 0:
                print(f"\n✅ SUCCESS: Collected {newly_collected} new articles!")
                print(f"📊 Total dataset: {after_count} articles")
                
                # Trigger ML processing with temporal context
                self.monitor.trigger_ml_processing_with_temporal_data(newly_collected)
            else:
                print(f"\n📰 No new articles this cycle - sources current")
            
            # Update progress
            if progress:
                daily_progress = progress.get('daily_progress', 0) * 100
                weekly_progress = progress.get('weekly_progress', 0) * 100
                monthly_progress = progress.get('monthly_progress', 0) * 100
                
                print(f"\n📈 UPDATED PROGRESS:")
                print(f"   Daily: {daily_progress:.1f}% | Weekly: {weekly_progress:.1f}% | Monthly: {monthly_progress:.1f}%")
            
        except Exception as e:
            print(f"❌ Enhanced collection cycle error: {e}")
    
    def start_longterm_strategy(self):
        """Start the 30-day long-term collection strategy"""
        print("🚀 STARTING 30-DAY LONG-TERM COLLECTION STRATEGY")
        print("=" * 80)
        print("🎯 GOAL: Build robust 150+ article dataset for ML training")
        print("📊 TARGET: 5 articles/day with balanced regional coverage")
        print("🤖 OUTCOME: Defense-grade ML predictions with temporal context")
        print("=" * 80)
        
        # Initial assessment
        self.assess_collection_progress()
        
        # Schedule enhanced collection every 2 hours (12 times per day)
        schedule.every(2).hours.do(self.run_enhanced_collection_cycle)
        
        # Schedule daily progress reports
        schedule.every().day.at("08:00").do(self.assess_collection_progress)
        
        # Run initial collection
        self.run_enhanced_collection_cycle()
        
        print(f"\n🔄 Long-term collection strategy active!")
        print(f"📅 Collection cycles: Every 2 hours")
        print(f"📊 Progress reports: Daily at 08:00")
        print(f"🛑 Press Ctrl+C to stop")
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(300)  # Check every 5 minutes
                
        except KeyboardInterrupt:
            print(f"\n🛑 Long-term collection strategy stopped")
            print(f"📊 Final assessment:")
            self.assess_collection_progress()

def main():
    """Start long-term collection strategy"""
    strategy = LongTermCollectionStrategy()
    strategy.start_longterm_strategy()

if __name__ == '__main__':
    main()
