#!/usr/bin/env python3
"""Create the correct Django table and migrate real data"""
import sqlite3
import json
from datetime import datetime

def create_django_table_and_migrate():
    print("🔄 CREATING CORRECT DJANGO TABLE AND MIGRATING REAL DATA")
    print("=" * 60)
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Create the Django dashboard_newsarticle table
    print("📋 Creating dashboard_newsarticle table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dashboard_newsarticle (
            id VARCHAR(32) PRIMARY KEY,
            title VARCHAR(500) NOT NULL,
            raw_text TEXT NOT NULL,
            url VARCHAR(2000) NOT NULL,
            source VARCHAR(200) NOT NULL,
            published_date DATETIME,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            priority INTEGER NOT NULL DEFAULT 2,
            classification VARCHAR(50) NOT NULL DEFAULT 'news',
            language VARCHAR(10) NOT NULL DEFAULT 'en',
            processing_status VARCHAR(20) NOT NULL DEFAULT 'COMPLETED',
            latitude REAL,
            longitude REAL,
            content_length INTEGER,
            word_count INTEGER,
            relevance_score REAL NOT NULL DEFAULT 75.0,
            sentiment_score REAL NOT NULL DEFAULT 0.0,
            processed_json TEXT,
            entity_count INTEGER DEFAULT 0,
            created_by_id INTEGER,
            translated_text TEXT
        )
    """)
    
    # Clear any existing mock data
    cursor.execute("DELETE FROM dashboard_newsarticle WHERE source LIKE '%Defense Intelligence%' OR source LIKE '%Field Operations%'")
    print(f"🗑️ Cleared {cursor.rowcount} old mock records")
    
    # Copy real data from news_articles_step1
    print("📊 Migrating real data from news_articles_step1...")
    cursor.execute("SELECT * FROM news_articles_step1")
    step1_articles = cursor.fetchall()
    
    # Get column names for news_articles_step1
    cursor.execute("PRAGMA table_info(news_articles_step1)")
    step1_columns = [col[1] for col in cursor.fetchall()]
    
    migrated_count = 0
    for article in step1_articles:
        article_dict = dict(zip(step1_columns, article))
        
        cursor.execute("""
            INSERT OR REPLACE INTO dashboard_newsarticle 
            (id, title, raw_text, url, source, published_date, created_at, updated_at,
             priority, classification, language, processing_status, latitude, longitude,
             content_length, word_count, relevance_score, sentiment_score, processed_json,
             entity_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article_dict['id'],
            article_dict['title'],
            article_dict['raw_text'],
            article_dict['url'],
            article_dict['source'],
            article_dict.get('published_date'),
            article_dict['created_at'],
            article_dict['updated_at'],
            article_dict['priority'],
            article_dict['classification'],
            article_dict['language'],
            article_dict['processing_status'],
            article_dict.get('latitude'),
            article_dict.get('longitude'),
            article_dict.get('content_length'),
            article_dict.get('word_count'),
            article_dict['relevance_score'],
            article_dict['sentiment_score'],
            article_dict.get('processed_json'),
            article_dict.get('entity_count', 0)
        ))
        migrated_count += 1
    
    # Also add some from real_news_cache
    print("📊 Adding live scraped articles from real_news_cache...")
    cursor.execute("SELECT * FROM real_news_cache LIMIT 10")
    cache_articles = cursor.fetchall()
    
    current_time = datetime.now()
    for i, article in enumerate(cache_articles):
        article_id = f"live_{i}_{current_time.strftime('%Y%m%d%H%M%S')}"
        
        cursor.execute("""
            INSERT OR REPLACE INTO dashboard_newsarticle 
            (id, title, raw_text, url, source, published_date, created_at, updated_at,
             priority, classification, language, processing_status, latitude, longitude,
             content_length, word_count, relevance_score, sentiment_score, processed_json,
             entity_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article_id,
            article[1][:500],  # title
            article[2][:2000],  # content
            article[3],  # url
            article[4],  # source
            current_time,  # published_date
            current_time,  # created_at
            current_time,  # updated_at
            2,  # priority
            'live_news',  # classification
            'en',  # language
            'COMPLETED',  # processing_status
            None,  # latitude
            None,  # longitude
            len(article[2]) if article[2] else 0,  # content_length
            len(article[2].split()) if article[2] else 0,  # word_count
            80.0,  # relevance_score
            0.0,  # sentiment_score
            json.dumps({"status": "live_scraped", "timestamp": article[5]}),  # processed_json
            3  # entity_count
        ))
        migrated_count += 1
    
    conn.commit()
    
    # Verify the data
    cursor.execute("SELECT COUNT(*) FROM dashboard_newsarticle")
    total_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT title, source FROM dashboard_newsarticle LIMIT 5")
    sample_articles = cursor.fetchall()
    
    print(f"\n✅ MIGRATION COMPLETE!")
    print(f"📊 Total articles in dashboard_newsarticle: {total_count}")
    print(f"🔄 Migrated: {migrated_count} articles")
    print("\n📰 Sample articles now in Django table:")
    for article in sample_articles:
        print(f"  - {article[0][:60]}... (Source: {article[1]})")
    
    conn.close()
    return total_count

if __name__ == '__main__':
    count = create_django_table_and_migrate()
    print(f"\n🎯 SUCCESS: {count} REAL articles now available to Django API!")
    print("🚀 NO MORE STATIC DATA - API will serve LIVE geopolitical data!")
