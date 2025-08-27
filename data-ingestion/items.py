# -*- coding: utf-8 -*-
"""
Data items definition for Project Sentinel news spider
Defines the structured format for scraped news articles
"""

import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join
from w3lib.html import remove_tags


def clean_text(value):
    """Clean text content by removing extra whitespace and HTML artifacts."""
    if value:
        # Remove HTML tags if any remain
        value = remove_tags(value)
        # Clean up whitespace
        value = ' '.join(value.split())
        return value.strip()
    return value


def validate_url(value):
    """Validate and clean URL."""
    if value and isinstance(value, str):
        value = value.strip()
        if value.startswith(('http://', 'https://')):
            return value
    return None


class NewsArticleItem(scrapy.Item):
    """
    Structured item for news articles collected by Project Sentinel.
    
    Fields match the required specification:
    {'url', 'title', 'published_time', 'text', 'source'}
    """
    
    # Required fields as specified
    url = scrapy.Field(
        input_processor=MapCompose(validate_url),
        output_processor=TakeFirst()
    )
    
    title = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    
    published_time = scrapy.Field(
        output_processor=TakeFirst()
    )
    
    text = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=Join(' ')
    )
    
    source = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    
    # Additional metadata fields for enhanced analysis
    scraped_at = scrapy.Field(
        output_processor=TakeFirst()
    )
    
    content_length = scrapy.Field(
        output_processor=TakeFirst()
    )
    
    language = scrapy.Field(
        output_processor=TakeFirst()
    )
    
    category = scrapy.Field(
        output_processor=TakeFirst()
    )
    
    keywords = scrapy.Field()
    
    author = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )


class NewsSourceItem(scrapy.Item):
    """
    Item for tracking news source metadata and health.
    """
    
    source_name = scrapy.Field()
    source_url = scrapy.Field()
    last_scraped = scrapy.Field()
    articles_found = scrapy.Field()
    scrape_status = scrapy.Field()
    error_message = scrapy.Field()
    response_time = scrapy.Field()
