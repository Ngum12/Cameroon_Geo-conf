#!/usr/bin/env python3
"""Check the data in the existing news_articles_step1 table"""
import sqlite3

try:
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Check the structure of news_articles_step1
    cursor.execute("PRAGMA table_info(news_articles_step1);")
    columns = cursor.fetchall()
    print("📋 news_articles_step1 TABLE STRUCTURE:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Count total articles
    cursor.execute("SELECT COUNT(*) FROM news_articles_step1;")
    total = cursor.fetchone()[0]
    print(f"\n📊 TOTAL ARTICLES: {total}")
    
    # Check recent articles
    cursor.execute("SELECT COUNT(*) FROM news_articles_step1 WHERE created_at >= datetime('now', '-1 day');")
    recent_24h = cursor.fetchone()[0]
    print(f"📊 LAST 24H ARTICLES: {recent_24h}")
    
    # Check processing status
    cursor.execute("SELECT processing_status, COUNT(*) FROM news_articles_step1 GROUP BY processing_status;")
    status_counts = cursor.fetchall()
    print(f"\n📊 PROCESSING STATUS:")
    for status, count in status_counts:
        print(f"  - {status}: {count}")
    
    # Show 3 most recent articles
    cursor.execute("SELECT title, created_at, processing_status FROM news_articles_step1 ORDER BY created_at DESC LIMIT 3;")
    recent = cursor.fetchall()
    print(f"\n📰 MOST RECENT ARTICLES:")
    for title, created_at, status in recent:
        print(f"  - [{status}] {created_at}: {title[:60]}...")
        
    conn.close()
    
except Exception as e:
    print(f"❌ Database error: {e}")
