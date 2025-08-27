# -*- coding: utf-8 -*-
"""
Project Sentinel Dashboard Admin
Cameroon Defense Force OSINT Analysis System

Django admin interface for managing news articles and processing logs.
"""

from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

from .models import NewsArticle, ProcessingLog


@admin.register(NewsArticle)
class NewsArticleAdmin(OSMGeoAdmin):
    """Admin interface for NewsArticle model with map integration."""
    
    list_display = [
        'title_short', 'source', 'language', 'processing_status',
        'priority_display', 'entity_count', 'published_date', 'created_at'
    ]
    
    list_filter = [
        'processing_status', 'language', 'source', 'priority',
        'classification', 'created_at', 'published_date'
    ]
    
    search_fields = [
        'title', 'source', 'raw_text', 'url'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'content_length', 'word_count',
        'entity_count', 'processed_json_display', 'entities_display',
        'translation_display'
    ]
    
    fieldsets = (
        ('Article Information', {
            'fields': ('url', 'title', 'source', 'published_date')
        }),
        ('Content', {
            'fields': ('raw_text',),
            'classes': ('collapse',)
        }),
        ('Processing Results', {
            'fields': (
                'processing_status', 'language', 'processed_json_display',
                'translation_display', 'entities_display'
            ),
            'classes': ('collapse',)
        }),
        ('Classification & Priority', {
            'fields': ('classification', 'priority', 'relevance_score', 'sentiment_score')
        }),
        ('Location Data', {
            'fields': ('location',),
            'description': 'Geographic location associated with this article'
        }),
        ('Metadata', {
            'fields': (
                'id', 'created_at', 'updated_at', 'created_by',
                'content_length', 'word_count', 'entity_count'
            ),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    # Map settings for GeoDjango admin
    default_lat = 3.8480  # Yaoundé latitude
    default_lon = 11.5021  # Yaoundé longitude
    default_zoom = 7
    
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
    
    def processed_json_display(self, obj):
        """Display formatted JSON in read-only field."""
        if obj.processed_json:
            return format_html(
                '<pre style="background: #f8f8f8; padding: 10px; border-radius: 5px; max-height: 400px; overflow-y: scroll;">{}</pre>',
                json.dumps(obj.processed_json, indent=2, ensure_ascii=False)
            )
        return 'No processing data available'
    processed_json_display.short_description = 'Processing Results (JSON)'
    
    def entities_display(self, obj):
        """Display extracted entities in a formatted way."""
        entities = obj.entities
        if not entities:
            return 'No entities extracted'
        
        entity_groups = {}
        for entity in entities:
            group = entity.get('entity_group', 'Unknown')
            if group not in entity_groups:
                entity_groups[group] = []
            entity_groups[group].append({
                'word': entity.get('word', ''),
                'confidence': entity.get('confidence', 0.0)
            })
        
        html_parts = []
        colors = {'PERSON': 'blue', 'LOCATION': 'green', 'ORGANIZATION': 'purple', 'MISCELLANEOUS': 'gray'}
        
        for group, group_entities in entity_groups.items():
            color = colors.get(group, 'black')
            html_parts.append(f'<h4 style="color: {color}; margin: 10px 0 5px 0;">{group}</h4>')
            html_parts.append('<ul style="margin: 0; padding-left: 20px;">')
            
            for entity in group_entities:
                confidence = entity['confidence']
                confidence_color = 'green' if confidence > 0.8 else 'orange' if confidence > 0.5 else 'red'
                html_parts.append(
                    f'<li>{entity["word"]} '
                    f'<span style="color: {confidence_color}; font-size: 0.9em;">({confidence:.3f})</span></li>'
                )
            html_parts.append('</ul>')
        
        return format_html(''.join(html_parts))
    entities_display.short_description = 'Extracted Entities'
    
    def translation_display(self, obj):
        """Display translation information."""
        translated_text = obj.translated_text
        if not translated_text:
            return 'No translation available'
        
        # Show first 300 characters
        preview = translated_text[:300] + '...' if len(translated_text) > 300 else translated_text
        
        return format_html(
            '<div style="background: #f0f8ff; padding: 10px; border-left: 4px solid #007cba; margin: 10px 0;">'
            '<strong>Translated Text:</strong><br/>'
            '<em>{}</em>'
            '</div>',
            preview
        )
    translation_display.short_description = 'Translation'
    
    def get_queryset(self, request):
        """Optimize queryset for admin list view."""
        return super().get_queryset(request).select_related('created_by')


class ProcessingLogInline(admin.TabularInline):
    """Inline admin for ProcessingLog."""
    
    model = ProcessingLog
    extra = 0
    readonly_fields = ['operation', 'status', 'message', 'processing_time', 'created_at']
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ProcessingLog)
class ProcessingLogAdmin(admin.ModelAdmin):
    """Admin interface for ProcessingLog model."""
    
    list_display = [
        'article_title', 'operation', 'status', 'processing_time', 'created_at'
    ]
    
    list_filter = [
        'operation', 'status', 'created_at'
    ]
    
    search_fields = [
        'article__title', 'article__source', 'message'
    ]
    
    readonly_fields = [
        'article', 'operation', 'status', 'message', 'processing_time', 'created_at'
    ]
    
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    def article_title(self, obj):
        """Display article title with link."""
        if obj.article:
            url = reverse('admin:dashboard_newsarticle_change', args=[obj.article.pk])
            title = obj.article.title[:50] + '...' if len(obj.article.title) > 50 else obj.article.title
            return format_html('<a href="{}">{}</a>', url, title)
        return 'No article'
    article_title.short_description = 'Article'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# Add ProcessingLog inline to NewsArticle admin
NewsArticleAdmin.inlines = [ProcessingLogInline]
