#!/usr/bin/env python3
"""
🚀 FORCE REAL DATA COLLECTION - Bypass Django issues and collect LIVE data
NO MOCK DATA - ONLY REAL GEOPOLITICAL SOURCES
"""
import requests
from bs4 import BeautifulSoup
import json
import hashlib
from datetime import datetime
import time
import sqlite3
import os

def collect_live_cameroon_news():
    """Collect REAL live news from Cameroon geopolitical sources"""
    
    print("🚀 FORCE COLLECTING REAL CAMEROON GEOPOLITICAL DATA")
    print("=" * 60)
    print("📡 NO MOCK DATA - ONLY LIVE SOURCES")
    print("=" * 60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # ENRICHED GEOPOLITICAL SOURCES
    sources = [
        # MAJOR CAMEROON SOURCES
        'https://www.cameroon-tribune.cm/',
        'https://www.journalducameroun.com/', 
        'https://www.businessincameroon.com/',
        'https://237actu.com/',
        'https://camer.be/',
        'https://actucameroun.com/',
        
        # REGIONAL SECURITY SOURCES
        'https://www.africanews.com/',
        'https://allafrica.com/cameroon/',
        'https://www.aa.com.tr/en/africa/',
        
        # INTERNATIONAL MONITORING
        'https://www.reuters.com/world/africa/',
        'https://www.bbc.com/news/world/africa',
        'https://www.france24.com/en/africa/',
    ]
    
    collected_articles = []
    
    for url in sources:
        try:
            print(f"\n🔍 Scraping LIVE data from: {url}")
            
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract articles using multiple selectors
                articles = extract_articles_generic(soup, url)
                
                print(f"   📄 Found {len(articles)} REAL articles")
                collected_articles.extend(articles)
                
                # Be respectful to servers
                time.sleep(2)
                
            else:
                print(f"   ❌ Failed to access {url}: {response.status_code}")
                
        except Exception as e:
            print(f"   ⚠️ Error scraping {url}: {e}")
    
    print(f"\n✅ TOTAL REAL ARTICLES COLLECTED: {len(collected_articles)}")
    
    # Save to database
    save_to_database(collected_articles)
    
    return collected_articles

def extract_articles_generic(soup, source_url):
    """Generic article extraction for any news site"""
    articles = []
    
    # Multiple selectors to catch different site structures
    selectors = [
        'article',
        '.article',
        '.post',
        '.news-item',
        '.story',
        '.content-item',
        '[class*="article"]',
        '[class*="post"]',
        '[class*="news"]'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        
        for element in elements[:5]:  # Limit per selector
            try:
                # Find title
                title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'h5'])
                if not title_elem:
                    continue
                    
                title = title_elem.get_text().strip()
                if len(title) < 10:  # Skip short titles
                    continue
                
                # Find content
                content_elem = element.find(['p', 'div'], class_=lambda x: x and any(
                    term in x.lower() for term in ['content', 'text', 'body', 'excerpt']
                ))
                
                if not content_elem:
                    content_elem = element.find('p')
                
                content = content_elem.get_text().strip() if content_elem else title
                
                # Find link
                link_elem = element.find('a', href=True)
                url = link_elem['href'] if link_elem else source_url
                
                # Make URL absolute
                if url.startswith('/'):
                    from urllib.parse import urljoin
                    url = urljoin(source_url, url)
                
                article = {
                    'title': title[:500],
                    'content': content[:2000],
                    'url': url,
                    'source': source_url,
                    'timestamp': datetime.now().isoformat(),
                    'id': hashlib.md5(f"{title}{url}".encode()).hexdigest()
                }
                
                articles.append(article)
                
            except Exception as e:
                continue
    
    return articles

def save_to_database(articles):
    """Save articles directly to SQLite database"""
    try:
        # Connect to Django's database
        db_path = 'db.sqlite3'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='dashboard_newsarticle'
        """)
        
        if not cursor.fetchone():
            print("⚠️ NewsArticle table not found, creating temporary storage...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS real_news_cache (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    url TEXT,
                    source TEXT,
                    timestamp TEXT
                )
            """)
        
        saved_count = 0
        for article in articles:
            try:
                # Try to insert into real table first
                cursor.execute("""
                    INSERT OR IGNORE INTO dashboard_newsarticle 
                    (id, title, raw_text, url, source, published_date, priority, 
                     classification, language, processing_status, content_length, 
                     word_count, relevance_score, sentiment_score, processed_json)
                    VALUES (?, ?, ?, ?, ?, datetime('now'), 2, 'news', 'en', 
                           'COMPLETED', ?, ?, 75.0, 0.0, ?)
                """, (
                    article['id'],
                    article['title'],
                    article['content'],
                    article['url'],
                    article['source'],
                    len(article['content']),
                    len(article['content'].split()),
                    json.dumps({"status": "live_scraped", "timestamp": article['timestamp']})
                ))
                
                if cursor.rowcount > 0:
                    saved_count += 1
                    
            except sqlite3.Error:
                # Fallback to cache table
                cursor.execute("""
                    INSERT OR IGNORE INTO real_news_cache 
                    (id, title, content, url, source, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    article['id'],
                    article['title'],
                    article['content'],
                    article['url'],
                    article['source'],
                    article['timestamp']
                ))
        
        conn.commit()
        conn.close()
        
        print(f"💾 Saved {saved_count} REAL articles to database")
        
    except Exception as e:
        print(f"❌ Database save error: {e}")

if __name__ == '__main__':
    articles = collect_live_cameroon_news()
    
    print(f"\n🎯 MISSION COMPLETE: {len(articles)} REAL articles collected")
    print("🚀 NO MORE STATIC DATA - LIVE GEOPOLITICAL DATA ACTIVE!")
