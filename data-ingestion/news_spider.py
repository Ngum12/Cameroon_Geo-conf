# -*- coding: utf-8 -*-
"""
Scrapy spider for ingesting news articles from Cameroonian sources
Part of Project Sentinel - Cameroon Defense Force OSINT Analysis System
"""

import scrapy
import json
import os
import re
from dateparser import parse as parse_date
from urllib.parse import urljoin, urlparse
from scrapy.http import Request
from scrapy.utils.response import get_base_url


class CmrNewsSpider(scrapy.Spider):
    """
    Cameroonian news spider for Project Sentinel OSINT data collection.
    
    This spider crawls configured news sources to collect article content
    for intelligence analysis purposes.
    """
    
    name = 'cmr_news_spider'
    
    # Respect robots.txt for ethical scraping
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 3,  # 3 second delay between requests
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,  # Randomize delay (0.5 * to 1.5 * DOWNLOAD_DELAY)
        'CONCURRENT_REQUESTS': 1,  # Conservative concurrent requests
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,  # One request per domain at a time
        'AUTOTHROTTLE_ENABLED': True,  # Enable AutoThrottle extension
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'AUTOTHROTTLE_DEBUG': False,  # Set to True for debugging throttling
        'RETRY_TIMES': 3,  # Retry failed requests up to 3 times
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],  # HTTP codes to retry
        'USER_AGENT': 'Project Sentinel News Crawler 1.0 (+https://github.com/Ngum12/Cameroon_Geo-conf)',
    }
    
    def __init__(self, *args, **kwargs):
        """Initialize the spider with configuration."""
        super(CmrNewsSpider, self).__init__(*args, **kwargs)
        self.config_file = os.path.join(os.path.dirname(__file__), 'config', 'sources.json')
        self.sources = self.load_sources()
        
    def load_sources(self):
        """Load news sources from configuration file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.logger.info(f"Loaded {len(config.get('sources', []))} news sources from config")
                return config.get('sources', [])
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {self.config_file}")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error loading sources: {e}")
            return []
    
    def start_requests(self):
        """Generate initial requests from configured sources."""
        if not self.sources:
            self.logger.warning("No sources configured. Please check config/sources.json")
            return
            
        for source in self.sources:
            url = source.get('url')
            source_name = source.get('name', 'Unknown')
            
            if not url:
                self.logger.warning(f"No URL specified for source: {source_name}")
                continue
                
            self.logger.info(f"Starting crawl of {source_name}: {url}")
            yield Request(
                url=url,
                callback=self.parse,
                meta={'source_info': source},
                errback=self.handle_error
            )
    
    def parse(self, response):
        """
        Parse the news website response to extract article links and content.
        """
        source_info = response.meta.get('source_info', {})
        source_name = source_info.get('name', 'Unknown')
        
        # Extract article links if this is a listing page
        article_links = self.extract_article_links(response, source_info)
        
        # If article links found, follow them
        if article_links:
            for link in article_links:
                yield Request(
                    url=urljoin(response.url, link),
                    callback=self.parse_article,
                    meta={'source_info': source_info},
                    errback=self.handle_error
                )
        else:
            # Try to parse current page as an article
            article_data = self.parse_article(response)
            if article_data:
                yield article_data
    
    def extract_article_links(self, response, source_info):
        """Extract article links from a news website's main page."""
        # Common CSS selectors for article links
        link_selectors = [
            'article a::attr(href)',
            '.article-link::attr(href)',
            '.post-title a::attr(href)',
            'h2 a::attr(href)',
            'h3 a::attr(href)',
            '.entry-title a::attr(href)',
            '.news-item a::attr(href)',
        ]
        
        # Use custom selectors if provided in config
        custom_selectors = source_info.get('article_link_selectors', [])
        if custom_selectors:
            link_selectors = custom_selectors + link_selectors
        
        links = []
        for selector in link_selectors:
            found_links = response.css(selector).getall()
            links.extend(found_links)
            if found_links:
                self.logger.debug(f"Found {len(found_links)} links using selector: {selector}")
                break  # Use first successful selector
        
        # Filter and clean links
        valid_links = []
        for link in links[:20]:  # Limit to 20 articles per page
            if link and not link.startswith('#') and not link.startswith('javascript:'):
                valid_links.append(link)
        
        return valid_links
    
    def parse_article(self, response):
        """
        Parse individual article page to extract content.
        """
        source_info = response.meta.get('source_info', {})
        source_name = source_info.get('name', urlparse(response.url).netloc)
        
        # Extract article title
        title = self.extract_title(response, source_info)
        if not title:
            self.logger.warning(f"No title found for {response.url}")
            return None
        
        # Extract article text
        text = self.extract_text(response, source_info)
        if not text or len(text.strip()) < 100:  # Skip very short articles
            self.logger.warning(f"Insufficient content for {response.url}")
            return None
        
        # Extract publication time
        published_time = self.extract_published_time(response, source_info)
        
        # Create structured item with required fields
        item = {
            'url': response.url,
            'title': title.strip(),
            'published_time': published_time,
            'text': text.strip(),
            'source': source_name,
        }
        
        self.logger.info(f"Extracted article: {title[:50]}... from {source_name}")
        return item
    
    def extract_title(self, response, source_info):
        """Extract article title using various selectors."""
        title_selectors = [
            'h1::text',
            '.entry-title::text',
            '.post-title::text',
            '.article-title::text',
            'title::text',
        ]
        
        # Use custom selectors if provided
        custom_selectors = source_info.get('title_selectors', [])
        if custom_selectors:
            title_selectors = custom_selectors + title_selectors
        
        for selector in title_selectors:
            title = response.css(selector).get()
            if title:
                return self.clean_text(title)
        
        return None
    
    def extract_text(self, response, source_info):
        """Extract main article text using CSS selectors for article or p tags."""
        # Priority order of selectors for article content
        text_selectors = [
            'article p::text',
            '.entry-content p::text',
            '.post-content p::text',
            '.article-content p::text',
            '.content p::text',
            'p::text',
        ]
        
        # Use custom selectors if provided
        custom_selectors = source_info.get('text_selectors', [])
        if custom_selectors:
            text_selectors = custom_selectors + text_selectors
        
        text_parts = []
        
        for selector in text_selectors:
            paragraphs = response.css(selector).getall()
            if paragraphs and len(paragraphs) > 2:  # Ensure we have substantial content
                text_parts = [self.clean_text(p) for p in paragraphs if self.clean_text(p)]
                break  # Use first successful selector
        
        if not text_parts:
            return None
        
        # Join paragraphs with proper spacing
        full_text = ' '.join(text_parts)
        
        # Remove excessive whitespace
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        
        return full_text
    
    def extract_published_time(self, response, source_info):
        """Extract article publication time."""
        time_selectors = [
            'time::attr(datetime)',
            '.published::attr(datetime)',
            '.date::attr(datetime)',
            '[property="article:published_time"]::attr(content)',
            '.entry-date::text',
            '.post-date::text',
        ]
        
        # Use custom selectors if provided
        custom_selectors = source_info.get('time_selectors', [])
        if custom_selectors:
            time_selectors = custom_selectors + time_selectors
        
        for selector in time_selectors:
            time_str = response.css(selector).get()
            if time_str:
                parsed_time = parse_date(time_str.strip())
                if parsed_time:
                    return parsed_time.isoformat()
        
        return None
    
    def clean_text(self, text):
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove HTML entities and excessive whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        cleaned = cleaned.replace('\xa0', ' ')  # Non-breaking space
        cleaned = cleaned.replace('\n', ' ').replace('\r', ' ')
        
        return cleaned.strip()
    
    def handle_error(self, failure):
        """Handle request failures and errors."""
        request = failure.request
        source_info = request.meta.get('source_info', {})
        source_name = source_info.get('name', 'Unknown')
        
        self.logger.error(f"Request failed for {source_name} ({request.url}): {failure.value}")
        
        # Log specific error types
        if failure.check(scrapy.exceptions.IgnoreRequest):
            self.logger.warning(f"Request ignored: {request.url}")
        elif failure.check(scrapy.exceptions.DNSLookupError):
            self.logger.error(f"DNS lookup failed: {request.url}")
        elif failure.check(scrapy.exceptions.TimeoutError):
            self.logger.error(f"Request timeout: {request.url}")
        else:
            self.logger.error(f"Unexpected error: {failure.value}")
