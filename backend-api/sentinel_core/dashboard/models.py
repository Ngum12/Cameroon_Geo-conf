# -*- coding: utf-8 -*-
"""
Project Sentinel Dashboard Models
Cameroon Defense Force OSINT Analysis System

Models for storing and managing OSINT intelligence data.
"""

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.core.validators import URLValidator
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
import logging

logger = logging.getLogger(__name__)


class NewsArticle(models.Model):
    """
    Model for storing news articles and their processed intelligence data.
    
    This model stores raw article data and processed results from the NLP pipeline,
    including translations and entity extractions for OSINT analysis.
    """
    
    # Primary key
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the article"
    )
    
    # Required fields as specified
    url = models.URLField(
        max_length=2000,
        validators=[URLValidator()],
        help_text="Original URL of the news article",
        db_index=True
    )
    
    title = models.CharField(
        max_length=500,
        help_text="Article title",
        db_index=True
    )
    
    source = models.CharField(
        max_length=200,
        help_text="News source name (e.g., Cameroon Tribune)",
        db_index=True
    )
    
    raw_text = models.TextField(
        help_text="Original article text before processing"
    )
    
    processed_json = models.JSONField(
        default=dict,
        blank=True,
        help_text="Processed results from NLP pipeline (translation, entities, etc.)"
    )
    
    published_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Article publication date",
        db_index=True
    )
    
    # GeoDjango location field
    location = models.PointField(
        null=True,
        blank=True,
        srid=4326,  # WGS84 coordinate system
        help_text="Geographic location associated with the article (latitude, longitude)"
    )
    
    # Additional metadata fields for enhanced functionality
    language = models.CharField(
        max_length=10,
        default='unknown',
        help_text="Detected language of the article",
        db_index=True
    )
    
    classification = models.CharField(
        max_length=50,
        default='UNCLASSIFIED',
        choices=[
            ('UNCLASSIFIED', 'Unclassified'),
            ('RESTRICTED', 'Restricted'),
            ('CONFIDENTIAL', 'Confidential'),
            ('SECRET', 'Secret'),
        ],
        help_text="Security classification level"
    )
    
    priority = models.IntegerField(
        default=3,
        choices=[
            (1, 'Critical'),
            (2, 'High'),
            (3, 'Medium'),
            (4, 'Low'),
        ],
        help_text="Intelligence priority level",
        db_index=True
    )
    
    # Processing status
    processing_status = models.CharField(
        max_length=20,
        default='pending',
        choices=[
            ('pending', 'Pending Processing'),
            ('translating', 'Translating'),
            ('extracting_entities', 'Extracting Entities'),
            ('processed', 'Processing Complete'),
            ('failed', 'Processing Failed'),
        ],
        help_text="Current processing status",
        db_index=True
    )
    
    # Audit fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when article was first saved"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when article was last updated"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles_created',
        help_text="User who created this article record"
    )
    
    # Analysis fields
    sentiment_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Sentiment analysis score (-1.0 to 1.0)"
    )
    
    entity_count = models.IntegerField(
        default=0,
        help_text="Number of named entities extracted"
    )
    
    relevance_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Relevance score for intelligence analysis (0.0 to 1.0)"
    )
    
    # Content metadata
    content_length = models.IntegerField(
        null=True,
        blank=True,
        help_text="Length of article content in characters"
    )
    
    word_count = models.IntegerField(
        null=True,
        blank=True,
        help_text="Approximate word count of article"
    )
    
    class Meta:
        db_table = 'news_articles'
        verbose_name = 'News Article'
        verbose_name_plural = 'News Articles'
        ordering = ['-published_date', '-created_at']
        indexes = [
            models.Index(fields=['published_date', 'source']),
            models.Index(fields=['processing_status', 'priority']),
            models.Index(fields=['classification', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title[:50]}... ({self.source})"
    
    def save(self, *args, **kwargs):
        """Override save to calculate content metrics."""
        if self.raw_text:
            self.content_length = len(self.raw_text)
            self.word_count = len(self.raw_text.split())
        
        super().save(*args, **kwargs)
    
    @property
    def has_location(self):
        """Check if article has location data."""
        return self.location is not None
    
    @property
    def is_processed(self):
        """Check if article has been fully processed."""
        return self.processing_status == 'processed'
    
    @property
    def translated_text(self):
        """Get translated text from processed_json."""
        if self.processed_json and 'translation' in self.processed_json:
            return self.processed_json['translation'].get('translated_text', '')
        return ''
    
    @property
    def entities(self):
        """Get extracted entities from processed_json."""
        if self.processed_json and 'entities' in self.processed_json:
            return self.processed_json['entities'].get('entities', [])
        return []
    
    @property
    def person_entities(self):
        """Get person entities only."""
        return [e for e in self.entities if e.get('entity_group') == 'PERSON']
    
    @property
    def location_entities(self):
        """Get location entities only."""
        return [e for e in self.entities if e.get('entity_group') == 'LOCATION']
    
    @property
    def organization_entities(self):
        """Get organization entities only."""
        return [e for e in self.entities if e.get('entity_group') == 'ORGANIZATION']
    
    def get_coordinates(self):
        """Get latitude and longitude coordinates."""
        if self.location:
            return {
                'latitude': self.location.y,
                'longitude': self.location.x
            }
        return None
    
    def set_coordinates(self, latitude, longitude):
        """Set location from latitude and longitude."""
        try:
            self.location = Point(longitude, latitude, srid=4326)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid coordinates for article {self.id}: {e}")
    
    def add_processing_result(self, result_type, data):
        """Add processing result to processed_json field."""
        if not self.processed_json:
            self.processed_json = {}
        
        self.processed_json[result_type] = data
        self.save(update_fields=['processed_json', 'updated_at'])
    
    def mark_processing_complete(self):
        """Mark article as fully processed."""
        self.processing_status = 'processed'
        self.save(update_fields=['processing_status', 'updated_at'])
    
    def mark_processing_failed(self, error_message=None):
        """Mark article processing as failed."""
        self.processing_status = 'failed'
        if error_message and self.processed_json:
            self.processed_json['error'] = error_message
        self.save(update_fields=['processing_status', 'processed_json', 'updated_at'])


class ProcessingLog(models.Model):
    """
    Model for tracking processing operations and debugging.
    """
    
    article = models.ForeignKey(
        NewsArticle,
        on_delete=models.CASCADE,
        related_name='processing_logs'
    )
    
    operation = models.CharField(
        max_length=50,
        choices=[
            ('translation', 'Translation'),
            ('ner_extraction', 'Named Entity Recognition'),
            ('geocoding', 'Location Geocoding'),
            ('sentiment_analysis', 'Sentiment Analysis'),
        ]
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('started', 'Started'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ]
    )
    
    message = models.TextField(
        blank=True,
        help_text="Log message or error details"
    )
    
    processing_time = models.FloatField(
        null=True,
        blank=True,
        help_text="Processing time in seconds"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'processing_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.article.title[:30]}... - {self.operation} ({self.status})"
