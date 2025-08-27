# -*- coding: utf-8 -*-
"""
Project Sentinel Dashboard Serializers
Cameroon Defense Force OSINT Analysis System

Serializers for REST API endpoints.
"""

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import NewsArticle, ProcessingLog


class NewsArticleSerializer(serializers.ModelSerializer):
    """
    Full serializer for NewsArticle model with all fields.
    """
    
    coordinates = serializers.SerializerMethodField()
    translated_text = serializers.SerializerMethodField()
    entities = serializers.SerializerMethodField()
    person_entities = serializers.SerializerMethodField()
    location_entities = serializers.SerializerMethodField()
    organization_entities = serializers.SerializerMethodField()
    
    class Meta:
        model = NewsArticle
        fields = [
            'id', 'url', 'title', 'source', 'raw_text', 'processed_json',
            'published_date', 'location', 'coordinates', 'language',
            'classification', 'priority', 'processing_status',
            'created_at', 'updated_at', 'sentiment_score', 'entity_count',
            'relevance_score', 'content_length', 'word_count',
            'translated_text', 'entities', 'person_entities',
            'location_entities', 'organization_entities'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'processing_status',
            'entity_count', 'content_length', 'word_count', 'coordinates',
            'translated_text', 'entities', 'person_entities',
            'location_entities', 'organization_entities'
        ]
    
    def get_coordinates(self, obj):
        """Get latitude and longitude coordinates."""
        return obj.get_coordinates()
    
    def get_translated_text(self, obj):
        """Get translated text from processed_json."""
        return obj.translated_text
    
    def get_entities(self, obj):
        """Get all entities from processed_json."""
        return obj.entities
    
    def get_person_entities(self, obj):
        """Get person entities only."""
        return obj.person_entities
    
    def get_location_entities(self, obj):
        """Get location entities only."""
        return obj.location_entities
    
    def get_organization_entities(self, obj):
        """Get organization entities only."""
        return obj.organization_entities


class NewsArticleCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new NewsArticle instances.
    Only includes fields that should be provided during creation.
    """
    
    class Meta:
        model = NewsArticle
        fields = [
            'url', 'title', 'source', 'raw_text', 'published_date',
            'classification', 'priority'
        ]
        extra_kwargs = {
            'classification': {'default': 'UNCLASSIFIED'},
            'priority': {'default': 3},
        }


class NewsArticleSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for article listings and summaries.
    """
    
    coordinates = serializers.SerializerMethodField()
    entity_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = NewsArticle
        fields = [
            'id', 'title', 'source', 'published_date', 'created_at',
            'processing_status', 'priority', 'classification',
            'entity_count', 'language', 'coordinates', 'entity_summary'
        ]
    
    def get_coordinates(self, obj):
        """Get latitude and longitude coordinates."""
        return obj.get_coordinates()
    
    def get_entity_summary(self, obj):
        """Get summary of entities by type."""
        entities = obj.entities
        if not entities:
            return None
        
        return {
            'persons': len(obj.person_entities),
            'locations': len(obj.location_entities),
            'organizations': len(obj.organization_entities),
        }


class NewsArticleGeoJSONSerializer(GeoFeatureModelSerializer):
    """
    GeoJSON serializer for map visualization.
    """
    
    entities = serializers.SerializerMethodField()
    text_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = NewsArticle
        geo_field = 'location'
        fields = [
            'id', 'title', 'source', 'url', 'published_date', 'created_at',
            'priority', 'classification', 'language', 'entity_count',
            'entities', 'text_preview'
        ]
    
    def get_entities(self, obj):
        """Get entities grouped by type."""
        entities = obj.entities
        if not entities:
            return None
        
        return {
            'persons': [e['word'] for e in entities if e.get('entity_group') == 'PERSON'],
            'locations': [e['word'] for e in entities if e.get('entity_group') == 'LOCATION'],
            'organizations': [e['word'] for e in entities if e.get('entity_group') == 'ORGANIZATION'],
        }
    
    def get_text_preview(self, obj):
        """Get preview of translated text."""
        translated_text = obj.translated_text or obj.raw_text
        if len(translated_text) > 200:
            return translated_text[:200] + '...'
        return translated_text


class ProcessingLogSerializer(serializers.ModelSerializer):
    """
    Serializer for ProcessingLog model.
    """
    
    class Meta:
        model = ProcessingLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
