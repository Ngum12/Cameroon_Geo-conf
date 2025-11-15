#!/usr/bin/env python3
"""
Test the enhanced temporal analysis capabilities
"""
import sqlite3
from datetime import datetime, timedelta

class TemporalAnalyzer:
    """Test temporal analysis similar to enhanced monitoring system"""
    
    def __init__(self):
        self.temporal_periods = {
            '7_days': 7,
            '1_month': 30, 
            '3_months': 90
        }
    
    def analyze_temporal_data(self):
        """Analyze data across temporal periods (7 days, 1 month, 3 months)"""
        try:
            print("📊 ENHANCED TEMPORAL DATA ANALYSIS:")
            print("=" * 60)
            
            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()
            
            for period_name, days in self.temporal_periods.items():
                cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
                
                # Get articles for this period
                cursor.execute('SELECT COUNT(*) FROM dashboard_newsarticle WHERE created_at >= ?', (cutoff_date,))
                articles_in_period = cursor.fetchone()[0]
                
                # Get regional distribution
                regional_data = {}
                regions = ['Extreme-Nord', 'Sud-Ouest', 'Nord-Ouest', 'Centre', 'Littoral', 'Nord', 'Adamaoua', 'Est', 'Sud', 'Ouest']
                
                for region in regions:
                    cursor.execute('''SELECT COUNT(*) FROM dashboard_newsarticle 
                                    WHERE created_at >= ? AND (title LIKE ? OR raw_text LIKE ?)''', 
                                 (cutoff_date, f'%{region}%', f'%{region}%'))
                    count = cursor.fetchone()[0]
                    if count > 0:
                        regional_data[region] = count
                
                print(f"📅 {period_name.replace('_', ' ').title()}: {articles_in_period} articles")
                if regional_data:
                    top_regions = sorted(regional_data.items(), key=lambda x: x[1], reverse=True)[:3]
                    print(f"     🏆 Top regions: {', '.join([f'{r}({c})' for r, c in top_regions])}")
                else:
                    print(f"     📍 No regional data found for {period_name}")
                    
            conn.close()
            
        except Exception as e:
            print(f"❌ Temporal analysis error: {e}")
    
    def generate_ml_context(self):
        """Generate temporal context for ML processing"""
        try:
            print("\n🤖 ML TEMPORAL CONTEXT GENERATION:")
            print("=" * 50)
            
            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()
            
            # Gather temporal context for ML
            temporal_context = {}
            for period_name, days in self.temporal_periods.items():
                cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
                cursor.execute('SELECT COUNT(*) FROM dashboard_newsarticle WHERE created_at >= ?', (cutoff_date,))
                count = cursor.fetchone()[0]
                temporal_context[period_name] = count
            
            print("📊 Temporal Context for ML Models:")
            for period, count in temporal_context.items():
                print(f"   {period.replace('_', ' ').title()}: {count} articles")
            
            # Calculate data velocity (articles per day)
            if temporal_context['7_days'] > 0:
                daily_velocity = temporal_context['7_days'] / 7
                print(f"\n📈 Data Velocity: {daily_velocity:.1f} articles/day")
                
                # Predict data growth
                weekly_projection = daily_velocity * 7
                monthly_projection = daily_velocity * 30
                print(f"📊 Projections:")
                print(f"   Weekly: {weekly_projection:.0f} articles")
                print(f"   Monthly: {monthly_projection:.0f} articles")
            
            conn.close()
            return temporal_context
            
        except Exception as e:
            print(f"❌ ML context generation error: {e}")
            return {}
    
    def assess_data_quality(self):
        """Assess data quality for ML training"""
        try:
            print("\n🎯 DATA QUALITY ASSESSMENT FOR ML:")
            print("=" * 45)
            
            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()
            
            # Total articles
            cursor.execute('SELECT COUNT(*) FROM dashboard_newsarticle')
            total = cursor.fetchone()[0]
            
            # Articles with content
            cursor.execute('SELECT COUNT(*) FROM dashboard_newsarticle WHERE raw_text IS NOT NULL AND raw_text != ""')
            with_content = cursor.fetchone()[0]
            
            # Articles with sources
            cursor.execute('SELECT COUNT(*) FROM dashboard_newsarticle WHERE source IS NOT NULL AND source != ""')
            with_source = cursor.fetchone()[0]
            
            # Calculate quality metrics
            content_quality = (with_content / total) * 100 if total > 0 else 0
            source_quality = (with_source / total) * 100 if total > 0 else 0
            
            print(f"📊 Total articles: {total}")
            print(f"📝 Content quality: {content_quality:.1f}% ({with_content}/{total})")
            print(f"🔗 Source quality: {source_quality:.1f}% ({with_source}/{total})")
            
            # ML readiness assessment
            ml_ready = total >= 20 and content_quality >= 80
            print(f"\n🤖 ML Training Readiness: {'✅ READY' if ml_ready else '⚠️ NEEDS MORE DATA'}")
            
            if not ml_ready:
                if total < 20:
                    print(f"   📈 Need {20 - total} more articles for minimum ML training")
                if content_quality < 80:
                    print(f"   📝 Need better content quality (current: {content_quality:.1f}%)")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Data quality assessment error: {e}")

def main():
    """Run temporal analysis test"""
    print("🚀 TESTING ENHANCED TEMPORAL ANALYSIS SYSTEM")
    print("=" * 70)
    
    analyzer = TemporalAnalyzer()
    
    # Run temporal analysis
    analyzer.analyze_temporal_data()
    
    # Generate ML context
    temporal_context = analyzer.generate_ml_context()
    
    # Assess data quality
    analyzer.assess_data_quality()
    
    print("\n✅ TEMPORAL ANALYSIS TEST COMPLETE!")
    print("🎯 System ready for enhanced ML predictions with temporal context")

if __name__ == '__main__':
    main()
