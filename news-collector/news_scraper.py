"""
PROJECT SENTINEL - NEWS SCRAPING ENGINE
Cameroon Defense Force OSINT Intelligence System

Advanced multi-source news collection system for geopolitical intelligence.
"""

import asyncio
import aiohttp
import requests
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import feedparser
from bs4 import BeautifulSoup
import re
import hashlib
import logging
from urllib.parse import urljoin, urlparse
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from comprehensive_sources_config import (
    AdvancedNewsSource as NewsSource, SourceType, Language, 
    COMPREHENSIVE_INTELLIGENCE_SOURCES as ACTIVE_SOURCES,
    IntelligenceCategory
)
from sources_config import GEOPOLITICAL_KEYWORDS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ScrapedArticle:
    """Data structure for scraped articles."""
    url: str
    title: str
    content: str
    source: str
    language: str
    publish_date: Optional[datetime] = None
    author: Optional[str] = None
    hash_id: Optional[str] = None
    relevance_score: float = 0.0
    geopolitical_keywords: List[str] = None
    region_mentions: List[str] = None
    
    def __post_init__(self):
        # Generate unique hash ID for deduplication
        content_hash = hashlib.md5(f"{self.title}{self.content}".encode()).hexdigest()
        self.hash_id = content_hash
        
        # Initialize lists if None
        if self.geopolitical_keywords is None:
            self.geopolitical_keywords = []
        if self.region_mentions is None:
            self.region_mentions = []

class NewsScrapingEngine:
    """
    Advanced news scraping engine with multiple extraction methods.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Selenium WebDriver setup
        self.driver = None
        self.setup_selenium()
        
        # Cache for processed URLs to avoid duplicates
        self.processed_urls = set()
        
        # Geopolitical keyword patterns
        self.french_keywords = GEOPOLITICAL_KEYWORDS['french']
        self.english_keywords = GEOPOLITICAL_KEYWORDS['english']
        
        # Cameroon regions for location detection
        self.cameroon_regions = [
            'Yaoundé', 'Douala', 'Bamenda', 'Buea', 'Maroua', 'Garoua', 
            'Bertoua', 'Ebolowa', 'Bafoussam', 'Kumbo', 'Nord-Ouest', 
            'Sud-Ouest', 'Extrême-Nord', 'Centre', 'Littoral', 'Ouest',
            'Northwest', 'Southwest', 'Far North', 'Center', 'West'
        ]
    
    def setup_selenium(self):
        """Initialize Selenium WebDriver for dynamic content."""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("✅ Selenium WebDriver initialized successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Selenium setup failed: {e}. Falling back to requests-only mode.")
            self.driver = None
    
    def calculate_relevance_score(self, article: ScrapedArticle) -> float:
        """
        Calculate geopolitical relevance score (0-100) for an article.
        """
        score = 0.0
        text = f"{article.title} {article.content}".lower()
        
        # Determine language and use appropriate keywords
        keywords = self.french_keywords if article.language == 'fr' else self.english_keywords
        
        # Keyword scoring
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text)
        keyword_score = min(keyword_matches * 5, 40)  # Max 40 points for keywords
        
        # Regional mention scoring
        region_matches = sum(1 for region in self.cameroon_regions if region.lower() in text)
        region_score = min(region_matches * 10, 30)  # Max 30 points for regions
        
        # Title importance scoring
        title_keywords = sum(1 for keyword in keywords if keyword.lower() in article.title.lower())
        title_score = min(title_keywords * 15, 30)  # Max 30 points for title keywords
        
        total_score = keyword_score + region_score + title_score
        article.relevance_score = min(total_score, 100.0)
        
        # Store matched keywords and regions
        article.geopolitical_keywords = [kw for kw in keywords if kw.lower() in text][:10]
        article.region_mentions = [reg for reg in self.cameroon_regions if reg.lower() in text][:5]
        
        return article.relevance_score
    
    def scrape_rss_feed(self, source: NewsSource) -> List[ScrapedArticle]:
        """
        Scrape articles from RSS feeds.
        """
        articles = []
        
        try:
            logger.info(f"📡 Scraping RSS feed: {source.rss_feed}")
            
            feed = feedparser.parse(source.rss_feed)
            
            for entry in feed.entries[:20]:  # Limit to 20 most recent articles
                try:
                    # Extract article details
                    title = entry.get('title', '').strip()
                    url = entry.get('link', '').strip()
                    summary = entry.get('summary', '').strip()
                    
                    # Get full article content
                    full_content = self.extract_article_content(url, source)
                    content = full_content if full_content else summary
                    
                    # Parse publication date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    
                    # Skip if URL already processed
                    if url in self.processed_urls:
                        continue
                        
                    article = ScrapedArticle(
                        url=url,
                        title=title,
                        content=content,
                        source=source.name,
                        language=source.language.value,
                        publish_date=pub_date,
                        author=entry.get('author', None)
                    )
                    
                    # Calculate relevance score
                    relevance = self.calculate_relevance_score(article)
                    
                    # Only keep articles with relevance > 20
                    if relevance > 20:
                        articles.append(article)
                        self.processed_urls.add(url)
                        logger.info(f"✅ RSS Article: {title[:50]}... (Relevance: {relevance:.1f})")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing RSS entry: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ RSS feed error for {source.name}: {e}")
        
        return articles
    
    def extract_article_content(self, url: str, source: NewsSource) -> Optional[str]:
        """
        Extract full article content from URL using CSS selectors or intelligent extraction.
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try CSS selectors first if available
            if source.css_selectors and 'content' in source.css_selectors:
                content_elem = soup.select_one(source.css_selectors['content'])
                if content_elem:
                    return content_elem.get_text(strip=True)
            
            # Fallback: Intelligent content extraction
            return self.intelligent_content_extraction(soup)
            
        except Exception as e:
            logger.error(f"❌ Content extraction failed for {url}: {e}")
            return None
    
    def intelligent_content_extraction(self, soup: BeautifulSoup) -> str:
        """
        Intelligent content extraction without predefined selectors.
        """
        # Remove unwanted elements
        for unwanted in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            unwanted.decompose()
        
        # Common content selectors to try
        content_selectors = [
            'article', '.article-content', '.post-content', '.entry-content',
            '.article-body', '.post-body', '.content', '.main-content',
            '[class*="content"]', '[class*="article"]', '[class*="post"]'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                text = content_elem.get_text(strip=True)
                if len(text) > 200:  # Minimum content length
                    return text
        
        # Last resort: get all paragraph text
        paragraphs = soup.find_all('p')
        if paragraphs:
            content = ' '.join([p.get_text(strip=True) for p in paragraphs])
            return content
        
        return soup.get_text(strip=True)[:2000]  # Limit to first 2000 chars
    
    def scrape_web_source(self, source: NewsSource) -> List[ScrapedArticle]:
        """
        Scrape articles directly from website.
        """
        articles = []
        
        try:
            logger.info(f"🌐 Scraping website: {source.url}")
            
            # Use Selenium for dynamic sites if available
            if self.driver and 'javascript' in source.url.lower():
                html_content = self.selenium_scrape(source.url)
            else:
                response = self.session.get(source.url, timeout=15)
                response.raise_for_status()
                html_content = response.content
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find article links
            article_links = self.find_article_links(soup, source.url)
            
            # Process each article link
            for link in article_links[:15]:  # Limit to 15 articles per source
                try:
                    if link in self.processed_urls:
                        continue
                        
                    article_content = self.extract_article_content(link, source)
                    if not article_content or len(article_content) < 100:
                        continue
                    
                    # Extract title from the article page
                    title = self.extract_article_title(link, source)
                    
                    article = ScrapedArticle(
                        url=link,
                        title=title or "Article Title",
                        content=article_content,
                        source=source.name,
                        language=source.language.value
                    )
                    
                    # Calculate relevance
                    relevance = self.calculate_relevance_score(article)
                    
                    if relevance > 25:  # Higher threshold for web scraping
                        articles.append(article)
                        self.processed_urls.add(link)
                        logger.info(f"✅ Web Article: {article.title[:50]}... (Relevance: {relevance:.1f})")
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"❌ Error processing article {link}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Web scraping error for {source.name}: {e}")
        
        return articles
    
    def selenium_scrape(self, url: str) -> bytes:
        """Use Selenium for dynamic content scraping."""
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            return self.driver.page_source.encode()
        except Exception as e:
            logger.error(f"❌ Selenium scraping failed: {e}")
            # Fallback to requests
            response = self.session.get(url, timeout=10)
            return response.content
    
    def find_article_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Find article links on a news website homepage.
        """
        links = []
        
        # Common patterns for article links
        link_selectors = [
            'a[href*="/article/"]', 'a[href*="/news/"]', 'a[href*="/post/"]',
            'a[href*="/story/"]', '.article-link a', '.news-link a',
            'h1 a', 'h2 a', 'h3 a', '.title a', '.headline a'
        ]
        
        for selector in link_selectors:
            elements = soup.select(selector)
            for elem in elements:
                href = elem.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    if self.is_valid_article_url(full_url):
                        links.append(full_url)
        
        # Remove duplicates and return
        return list(set(links))
    
    def extract_article_title(self, url: str, source: NewsSource) -> Optional[str]:
        """Extract article title from URL."""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try CSS selector first
            if source.css_selectors and 'title' in source.css_selectors:
                title_elem = soup.select_one(source.css_selectors['title'])
                if title_elem:
                    return title_elem.get_text(strip=True)
            
            # Fallback to common title selectors
            title_selectors = ['h1', '.title', '.headline', '.article-title', '.post-title']
            for selector in title_selectors:
                elem = soup.select_one(selector)
                if elem:
                    return elem.get_text(strip=True)
            
            # Last resort: HTML title tag
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text(strip=True)
                
        except Exception as e:
            logger.error(f"❌ Title extraction failed for {url}: {e}")
        
        return None
    
    def is_valid_article_url(self, url: str) -> bool:
        """Check if URL looks like a valid article URL."""
        if not url or len(url) < 10:
            return False
            
        # Skip common non-article URLs
        skip_patterns = [
            '/category/', '/tag/', '/author/', '/search/', '/page/',
            'javascript:', 'mailto:', 'tel:', '#', '?',
            '.jpg', '.png', '.gif', '.pdf', '.doc'
        ]
        
        for pattern in skip_patterns:
            if pattern in url.lower():
                return False
        
        return True
    
    def scrape_source(self, source: NewsSource) -> List[ScrapedArticle]:
        """
        Main method to scrape a single news source.
        """
        logger.info(f"🚀 Starting scraping: {source.name} ({source.language.value})")
        
        try:
            if source.source_type == SourceType.RSS and hasattr(source, 'rss_feed') and source.rss_feed:
                return self.scrape_rss_feed(source)
            elif source.source_type in [SourceType.WEB_SCRAPING, SourceType.GOVERNMENT_PORTAL, SourceType.WIRE_SERVICE, SourceType.API]:
                # Treat all these as web scraping sources for now
                return self.scrape_web_source(source)
            else:
                # Try web scraping as fallback for any unrecognized type
                logger.info(f"🔄 Attempting web scraping for {source.name} (type: {source.source_type})")
                return self.scrape_web_source(source)
                
        except Exception as e:
            logger.error(f"❌ Scraping failed for {source.name}: {e}")
            return []
    
    def scrape_all_sources(self, max_sources: int = 10) -> List[ScrapedArticle]:
        """
        Scrape multiple news sources.
        """
        all_articles = []
        sources = [s for s in ACTIVE_SOURCES if s.is_active][:max_sources]
        
        logger.info(f"🎯 Starting comprehensive scraping of {len(sources)} sources")
        
        for i, source in enumerate(sources, 1):
            try:
                logger.info(f"📊 Progress: {i}/{len(sources)} - {source.name}")
                articles = self.scrape_source(source)
                
                if articles:
                    all_articles.extend(articles)
                    logger.info(f"✅ Collected {len(articles)} articles from {source.name}")
                else:
                    logger.warning(f"⚠️ No articles found for {source.name}")
                
                # Rate limiting between sources
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Failed to scrape {source.name}: {e}")
                continue
        
        logger.info(f"🏆 SCRAPING COMPLETE: {len(all_articles)} total articles collected")
        return all_articles
    
    def __del__(self):
        """Clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass

# Test the scraping system
if __name__ == "__main__":
    print("🚀 PROJECT SENTINEL - NEWS COLLECTOR TEST")
    print("=" * 50)
    
    scraper = NewsScrapingEngine()
    
    # Test with sources that have supported source types
    supported_types = [SourceType.RSS, SourceType.WEB_SCRAPING, SourceType.GOVERNMENT_PORTAL]
    test_sources = [source for source in ACTIVE_SOURCES 
                   if source.is_active and source.source_type in supported_types][:5]
    
    if not test_sources:
        print("❌ No active sources available for testing")
        exit(1)
    
    print(f"🎯 Testing {len(test_sources)} high-priority sources...")
    
    all_articles = []
    for i, source in enumerate(test_sources, 1):
        print(f"\n🧪 [{i}/{len(test_sources)}] Testing: {source.name}")
        print(f"   URL: {source.url}")
        print(f"   Type: {source.source_type.value}")
        print(f"   Language: {source.language.value}")
        print(f"   Credibility: {source.credibility_score}/10")
        
        try:
            articles = scraper.scrape_source(source)
            all_articles.extend(articles)
            print(f"✅ Found {len(articles)} relevant articles")
            
            # Show top article from this source
            if articles:
                top_article = max(articles, key=lambda x: x.relevance_score)
                print(f"   📰 Top Article: {top_article.title[:60]}...")
                print(f"   🎯 Relevance Score: {top_article.relevance_score:.1f}/100")
            
        except Exception as e:
            print(f"❌ Error testing {source.name}: {e}")
            continue
    
    print(f"\n🏆 TEST RESULTS:")
    print(f"Total articles collected: {len(all_articles)}")
    
    if all_articles:
        # Sort by relevance
        sorted_articles = sorted(all_articles, key=lambda x: x.relevance_score, reverse=True)
        avg_relevance = sum(a.relevance_score for a in all_articles) / len(all_articles)
        
        print(f"Average relevance score: {avg_relevance:.1f}/100")
        print(f"Highest relevance: {sorted_articles[0].relevance_score:.1f}/100")
        
        print(f"\n📊 TOP 3 ARTICLES:")
        for i, article in enumerate(sorted_articles[:3], 1):
            print(f"\n{i}. 📰 {article.title}")
            print(f"   🌍 Source: {article.source} ({article.language})")
            print(f"   🎯 Relevance: {article.relevance_score:.1f}/100")
            print(f"   🔗 URL: {article.url}")
            print(f"   📄 Content: {article.content[:150]}...")
            if article.geopolitical_keywords:
                print(f"   🏷️ Keywords: {', '.join(article.geopolitical_keywords[:5])}")
            if article.region_mentions:
                print(f"   📍 Regions: {', '.join(article.region_mentions[:3])}")
        
        print(f"\n✅ NEWS COLLECTOR TEST COMPLETED SUCCESSFULLY!")
        print(f"🛡️ CAMEROON DEFENSE FORCE - INTELLIGENCE COLLECTION OPERATIONAL")
        
    else:
        print("⚠️ No articles found - may need to adjust filtering criteria or check source availability")


