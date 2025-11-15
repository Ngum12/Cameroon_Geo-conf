from django.db import models
from django.contrib.auth.models import User
import uuid
import json

class NewsArticle(models.Model):
    # Basic fields for Step 1
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=500)
    source = models.CharField(max_length=200)
    raw_text = models.TextField()
    processed_json = models.JSONField(default=dict, blank=True)
    published_date = models.DateTimeField(null=True, blank=True)
    
    # Simplified location as latitude/longitude floats for Step 1
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Classification and priority
    language = models.CharField(max_length=10, default='unknown')
    classification = models.CharField(max_length=50, default='UNCLASSIFIED', choices=[
        ('UNCLASSIFIED', 'Unclassified'),
        ('RESTRICTED', 'Restricted'), 
        ('CONFIDENTIAL', 'Confidential'),
        ('SECRET', 'Secret'),
    ])
    priority = models.IntegerField(default=3, choices=[
        (1, 'Critical'),
        (2, 'High'),
        (3, 'Medium'),
        (4, 'Low'),
    ])
    processing_status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending Processing'),
        ('translating', 'Translating'),
        ('extracting_entities', 'Extracting Entities'),
        ('processed', 'Processing Complete'),
        ('failed', 'Processing Failed'),
    ])
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Analysis fields
    entity_count = models.IntegerField(default=0)
    content_length = models.IntegerField(null=True, blank=True)
    word_count = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'news_articles_step1'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title[:50]}... ({self.source})"
    
    def save(self, *args, **kwargs):
        if self.raw_text:
            self.content_length = len(self.raw_text)
            self.word_count = len(self.raw_text.split())
        super().save(*args, **kwargs)
    
    @property
    def coordinates(self):
        if self.latitude is not None and self.longitude is not None:
            return {'latitude': self.latitude, 'longitude': self.longitude}
        return None
    
    @property
    def entities(self):
        if self.processed_json and 'entities' in self.processed_json:
            return self.processed_json['entities'].get('entities', [])
        return []
