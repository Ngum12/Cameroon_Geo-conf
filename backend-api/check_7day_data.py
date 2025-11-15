#!/usr/bin/env python3
"""
Check 7-day data collection status
"""
import sqlite3
from datetime import datetime, timedelta

print('📊 7-DAY DATA COLLECTION ANALYSIS')
print('=' * 50)

try:
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dashboard_newsarticle'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        # Total articles
        cursor.execute('SELECT COUNT(*) FROM dashboard_newsarticle')
        total = cursor.fetchone()[0]
        print(f'📰 Total articles in database: {total}')
        
        # Last 7 days
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM dashboard_newsarticle WHERE created_at >= ?', (seven_days_ago,))
        last_7d = cursor.fetchone()[0]
        print(f'📅 Articles from last 7 days: {last_7d}')
        
        # Last 24 hours
        yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM dashboard_newsarticle WHERE created_at >= ?', (yesterday,))
        last_24h = cursor.fetchone()[0]
        print(f'🕐 Articles from last 24 hours: {last_24h}')
        
        # Recent articles
        cursor.execute('SELECT title, created_at FROM dashboard_newsarticle ORDER BY created_at DESC LIMIT 5')
        recent = cursor.fetchall()
        
        print('\n🔍 5 MOST RECENT ARTICLES:')
        for i, (title, created_at) in enumerate(recent, 1):
            title_short = title[:60] if title else 'No title'
            print(f'{i}. {title_short}... ({created_at})')
            
        # Regional analysis for last 7 days
        print('\n🌍 REGIONAL ANALYSIS (Last 7 days):')
        regions = ['Extreme-Nord', 'Sud-Ouest', 'Nord-Ouest', 'Centre', 'Littoral', 'Nord', 'Adamaoua', 'Est', 'Sud', 'Ouest']
        regional_data = {}
        
        for region in regions:
            cursor.execute('SELECT COUNT(*) FROM dashboard_newsarticle WHERE created_at >= ? AND (title LIKE ? OR raw_text LIKE ?)', 
                         (seven_days_ago, f'%{region}%', f'%{region}%'))
            count = cursor.fetchone()[0]
            if count > 0:
                regional_data[region] = count
                print(f'  📍 {region}: {count} articles')
        
        # Show temporal trends
        print('\n📈 TEMPORAL TRENDS:')
        periods = [
            ('Last 24 hours', 1),
            ('Last 3 days', 3), 
            ('Last 7 days', 7)
        ]
        
        for period_name, days in periods:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            cursor.execute('SELECT COUNT(*) FROM dashboard_newsarticle WHERE created_at >= ?', (cutoff,))
            count = cursor.fetchone()[0]
            print(f'  📊 {period_name}: {count} articles')
            
        # Data quality assessment
        print('\n🎯 DATA QUALITY ASSESSMENT:')
        if total > 0:
            coverage_7d = (last_7d / total) * 100 if total > 0 else 0
            print(f'  📈 7-day coverage: {coverage_7d:.1f}% of total data')
            
            if last_7d > 0:
                daily_avg = last_7d / 7
                print(f'  📅 Daily average (7d): {daily_avg:.1f} articles/day')
                
                if len(regional_data) > 0:
                    top_region = max(regional_data.items(), key=lambda x: x[1])
                    print(f'  🏆 Most active region: {top_region[0]} ({top_region[1]} articles)')
                    
        print(f'\n✅ Database contains {total} total articles')
        print(f'✅ {last_7d} articles collected in last 7 days')
        print('✅ Ready for enhanced temporal ML analysis')
                
    else:
        print('❌ dashboard_newsarticle table not found')
        
        # Check other tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print('Available tables:', [t[0] for t in tables])
    
    conn.close()
    
except Exception as e:
    print(f'❌ Database error: {e}')

print('\n🚀 7-day data analysis complete!')
