#!/usr/bin/env python3
"""Test if real Cameroon news sources are accessible and have content"""
import requests
import feedparser
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin

def test_news_source(name, url, source_type="web"):
    """Test if a news source is accessible"""
    try:
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ Status: {response.status_code} OK")
            
            if source_type == "rss":
                # Parse RSS feed
                feed = feedparser.parse(response.content)
                if feed.entries:
                    print(f"   📰 RSS Entries: {len(feed.entries)}")
                    if feed.entries:
                        latest = feed.entries[0]
                        print(f"   📄 Latest: {latest.title[:60]}...")
                        print(f"   📅 Date: {latest.get('published', 'No date')}")
                    return True, len(feed.entries)
                else:
                    print(f"   ⚠️  RSS feed has no entries")
                    return False, 0
            else:
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.find('title')
                articles = soup.find_all(['article', 'div'], class_=lambda x: x and ('article' in x.lower() or 'post' in x.lower() or 'news' in x.lower()))
                
                print(f"   📰 Page Title: {title.text.strip()[:60] if title else 'No title'}...")
                print(f"   📄 Potential Articles Found: {len(articles)}")
                
                # Look for recent news indicators
                text_content = response.text.lower()
                today_indicators = ['today', 'aujourd\'hui', '2025', 'september', 'septembre', 'october', 'octobre']
                recent_count = sum(1 for indicator in today_indicators if indicator in text_content)
                print(f"   📅 Recent Content Indicators: {recent_count}")
                
                return True, len(articles)
                
        else:
            print(f"   ❌ Status: {response.status_code} - {response.reason}")
            return False, 0
            
    except requests.exceptions.Timeout:
        print(f"   ⏱️  Timeout - Source too slow")
        return False, 0
    except requests.exceptions.ConnectionError:
        print(f"   🔌 Connection Error - Source unreachable")
        return False, 0
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}...")
        return False, 0

def main():
    print("🔍 TESTING REAL CAMEROON NEWS SOURCES")
    print("=" * 60)
    
    # Major Cameroon news sources
    sources = [
        ("Cameroon Tribune", "https://www.cameroon-tribune.cm/", "web"),
        ("Journal du Cameroun", "https://www.journalducameroun.com/", "web"),
        ("Business in Cameroon", "https://www.businessincameroon.com/", "web"), 
        ("237actu", "https://237actu.com/", "web"),
        ("Camer.be", "https://camer.be/", "web"),
        ("Actu Cameroun", "https://actucameroun.com/", "web"),
        ("Cameroon News Agency", "https://cna.cm/", "web"),
        
        # Try RSS feeds  
        ("Cameroon Tribune RSS", "https://www.cameroon-tribune.cm/rss.xml", "rss"),
        ("Business in Cameroon RSS", "https://www.businessincameroon.com/rss", "rss"),
    ]
    
    working_sources = []
    failed_sources = []
    
    for name, url, source_type in sources:
        success, content_count = test_news_source(name, url, source_type)
        
        if success and content_count > 0:
            working_sources.append((name, url, content_count))
        else:
            failed_sources.append((name, url))
            
        time.sleep(2)  # Be polite to servers
    
    print("\n" + "=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60)
    
    if working_sources:
        print("✅ WORKING SOURCES:")
        for name, url, count in working_sources:
            print(f"   🟢 {name}: {count} articles/items")
    
    if failed_sources:
        print("\n❌ FAILED SOURCES:")
        for name, url in failed_sources:
            print(f"   🔴 {name}: {url}")
    
    print(f"\n📈 SUCCESS RATE: {len(working_sources)}/{len(sources)} sources working ({len(working_sources)/len(sources)*100:.1f}%)")
    
    if len(working_sources) >= 2:
        print("✅ ENOUGH SOURCES AVAILABLE - Scraping should work!")
    else:
        print("⚠️  LIMITED SOURCES - May need alternative approach")

if __name__ == '__main__':
    main()
