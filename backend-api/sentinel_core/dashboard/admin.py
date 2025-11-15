# -*- coding: utf-8 -*-
"""
Project Sentinel Dashboard Admin
Cameroon Defense Force OSINT Analysis System

Django admin interface for managing news articles and processing logs.
"""

from django.contrib import admin
# from django.contrib.gis.admin import OSMGeoAdmin  # Disabled for now
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

from .models import NewsArticle


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    """Admin interface for NewsArticle model."""
    
    list_display = [
        'title_short', 'source', 'processing_status',
        'priority_display', 'published_date', 'scraped_at'
    ]
    
    list_filter = [
        'processing_status', 'source', 'priority',
        'classification', 'scraped_at', 'published_date'
    ]
    
    search_fields = [
        'title', 'source', 'content', 'url'
    ]
    
    readonly_fields = [
        'scraped_at', 'entities_display'
    ]
    
    fieldsets = (
        ('Article Information', {
            'fields': ('url', 'title', 'source', 'published_date')
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('collapse',)
        }),
        ('Processing Results', {
            'fields': (
                'processing_status', 'entities_display'
            ),
            'classes': ('collapse',)
        }),
        ('Classification & Priority', {
            'fields': ('classification', 'priority', 'sentiment_score', 'threat_level')
        }),
        ('Location Data', {
            'fields': ('region',),
            'description': 'Geographic information associated with this article'
        }),
        ('Metadata', {
            'fields': (
                'scraped_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-scraped_at']
    date_hierarchy = 'scraped_at'
    
    def title_short(self, obj):
        """Display shortened title in list view."""
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Title'
    
    def priority_display(self, obj):
        """Display priority with color coding."""
        colors = {1: 'red', 2: 'orange', 3: 'blue', 4: 'gray'}
        labels = {1: 'Critical', 2: 'High', 3: 'Medium', 4: 'Low'}
        
        color = colors.get(obj.priority, 'gray')
        label = labels.get(obj.priority, 'Unknown')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, label
        )
    priority_display.short_description = 'Priority'
    
    # Removed processed_json_display method since field doesn't exist in model
    
    def entities_display(self, obj):
        """Display extracted entities in a formatted way."""
        entities = obj.entities
        if not entities:
            return 'No entities extracted'
        
        # Display as simple text for now
        return format_html(
            '<div style="background: #f0f8ff; padding: 10px; border-left: 4px solid #007cba; margin: 10px 0;">'
            '<strong>Entities:</strong><br/>'
            '<em>{}</em>'
            '</div>',
            entities[:200] + '...' if len(entities) > 200 else entities
        )
    entities_display.short_description = 'Extracted Entities'
    
    # Removed translation_display method since field doesn't exist in model
    
    def get_queryset(self, request):
        """Optimize queryset for admin list view."""
        return super().get_queryset(request).select_related('created_by')


# ProcessingLog functionality temporarily removed for simplified setup





