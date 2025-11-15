# Project Sentinel - Advanced User Models
# Defense Intelligence Authentication System

# TEMPORARILY DISABLED FOR SYSTEM STARTUP
# from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid

# AUTHENTICATION MODELS TEMPORARILY DISABLED FOR SYSTEM STARTUP
# Will be re-enabled once basic system is working

# Enhanced NewsArticle model for the working system
class NewsArticle(models.Model):
    """Enhanced NewsArticle model with user tracking"""
    
    id = models.CharField(max_length=32, primary_key=True)  # Match database: char(32)
    title = models.CharField(max_length=500)
    raw_text = models.TextField()  # Match DB field name
    url = models.CharField(max_length=2000)  # Match DB field name
    source = models.CharField(max_length=200)
    published_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)  # Match DB field name
    
    # Enhanced fields (match database schema exactly)
    priority = models.IntegerField(default=1)
    classification = models.CharField(max_length=50, default='general')
    language = models.CharField(max_length=10, default='en')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Additional database fields (match existing schema)
    processed_json = models.TextField(blank=True)
    entity_count = models.IntegerField(default=0)
    content_length = models.IntegerField(default=0)
    word_count = models.IntegerField(default=0)
    relevance_score = models.FloatField(null=True, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    translated_text = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # User tracking fields exist in database as created_by_id (integer field)
    created_by_id = models.IntegerField(null=True, blank=True)
    
    # Processing status
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('PROCESSING', 'Processing'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed'),
            ('REVIEWED', 'Human Reviewed'),
        ],
        default='PENDING'
    )
    
    class Meta:
        db_table = 'news_articles_step1'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title[:50]}..."