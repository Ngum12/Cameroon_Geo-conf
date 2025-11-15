# Project Sentinel - Step 1 Views
# Real Django views with mock NLP services

import json
import time
from datetime import datetime
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import NewsArticle

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint - same as demo but with Django"""
    return Response({
        'status': 'healthy',
        'service': 'Project Sentinel Django Backend - Step 1',
        'message': 'Cameroon Defense Force OSINT Analysis System',
        'version': '1.0.0',
        'step': 'Django Backend with SQLite',
        'classification': 'RESTRICTED',
        'timestamp': timezone.now().isoformat(),
        'database': 'Connected',
        'articles_count': NewsArticle.objects.count()
    })

@api_view(['GET'])
@permission_classes([AllowAny]) 
def get_events(request):
    """Return processed articles as GeoJSON - now from real database"""
    try:
        # Get query parameters
        limit = min(int(request.GET.get('limit', 100)), 1000)
        days = int(request.GET.get('days', 30))
        source_filter = request.GET.get('source')
        priority_filter = request.GET.get('priority')
        
        # Build queryset from real database
        queryset = NewsArticle.objects.filter(
            processing_status='processed'
        ).exclude(
            latitude__isnull=True, longitude__isnull=True
        ).order_by('-created_at')
        
        # Apply filters
        if days > 0:
            cutoff_date = timezone.now() - timezone.timedelta(days=days)
            queryset = queryset.filter(created_at__gte=cutoff_date)
        
        if source_filter:
            queryset = queryset.filter(source__icontains=source_filter)
            
        if priority_filter:
            try:
                priority_int = int(priority_filter)
                if 1 <= priority_int <= 4:
                    queryset = queryset.filter(priority=priority_int)
            except ValueError:
                pass
        
        # Limit results
        articles = queryset[:limit]
        
        # Build GeoJSON features
        features = []
        for article in articles:
            if article.coordinates:
                # Extract entities from processed_json
                entities = article.entities
                entity_groups = {'persons': [], 'locations': [], 'organizations': []}
                
                for entity in entities:
                    group = entity.get('entity_group', '').upper()
                    word = entity.get('word', '')
                    if group == 'PERSON':
                        entity_groups['persons'].append(word)
                    elif group == 'LOCATION':
                        entity_groups['locations'].append(word) 
                    elif group == 'ORGANIZATION':
                        entity_groups['organizations'].append(word)
                
                # Get translated text
                translated_text = ''
                if article.processed_json and 'translation' in article.processed_json:
                    translated_text = article.processed_json['translation'].get('translated_text', '')
                
                feature = {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [article.longitude, article.latitude]
                    },
                    'properties': {
                        'id': str(article.id),
                        'title': article.title,
                        'source': article.source,
                        'url': article.url,
                        'published_date': article.published_date.isoformat() if article.published_date else None,
                        'created_at': article.created_at.isoformat(),
                        'priority': article.priority,
                        'classification': article.classification,
                        'language': article.language,
                        'entity_count': article.entity_count,
                        'content_length': article.content_length,
                        'word_count': article.word_count,
                        'entities': entity_groups,
                        'text_preview': translated_text[:200] + '...' if len(translated_text) > 200 else translated_text
                    }
                }
                features.append(feature)
        
        # Create GeoJSON response
        geojson = {
            'type': 'FeatureCollection',
            'features': features,
            'metadata': {
                'total_features': len(features),
                'generated_at': timezone.now().isoformat(),
                'system': 'Project Sentinel Django Backend',
                'step': 1,
                'database': 'SQLite',
                'classification': 'RESTRICTED',
                'query_parameters': {
                    'limit': limit,
                    'days': days,
                    'source': source_filter,
                    'priority': priority_filter,
                }
            }
        }
        
        return Response(geojson)
        
    except Exception as e:
        return Response(
            {'error': 'Internal server error', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def statistics_view(request):
    """Return system statistics - now from real database"""
    try:
        from django.db.models import Count
        
        # Basic counts from database
        total_articles = NewsArticle.objects.count()
        processed_articles = NewsArticle.objects.filter(processing_status='processed').count()
        pending_articles = NewsArticle.objects.filter(processing_status='pending').count()
        failed_articles = NewsArticle.objects.filter(processing_status='failed').count()
        
        # Articles with location
        located_articles = NewsArticle.objects.exclude(
            latitude__isnull=True, longitude__isnull=True
        ).count()
        
        # Recent articles (last 24 hours)
        from datetime import timedelta
        recent_cutoff = timezone.now() - timedelta(hours=24)
        recent_articles = NewsArticle.objects.filter(created_at__gte=recent_cutoff).count()
        
        # Priority breakdown
        critical_priority = NewsArticle.objects.filter(priority=1).count()
        high_priority = NewsArticle.objects.filter(priority=2).count()
        
        # Source breakdown
        source_stats = NewsArticle.objects.values('source').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Priority breakdown
        priority_stats = NewsArticle.objects.values('priority').annotate(
            count=Count('id') 
        ).order_by('priority')
        
        # Status breakdown
        status_stats = NewsArticle.objects.values('processing_status').annotate(
            count=Count('id')
        )
        
        stats = {
            'overview': {
                'total_articles': total_articles,
                'processed_articles': processed_articles,
                'pending_articles': pending_articles,
                'failed_articles': failed_articles,
                'located_articles': located_articles,
                'recent_articles_24h': recent_articles,
                'critical_priority': critical_priority,
                'high_priority': high_priority,
            },
            'by_source': list(source_stats),
            'by_priority': list(priority_stats),
            'by_status': list(status_stats),
            'generated_at': timezone.now().isoformat(),
            'system': 'Project Sentinel Django Backend',
            'step': 1,
            'database': 'SQLite'
        }
        
        return Response(stats)
        
    except Exception as e:
        return Response(
            {'error': 'Internal server error', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def process_article(request):
    """Process article - Step 1 with mock NLP services"""
    try:
        data = request.data
        
        # Create article in database
        article = NewsArticle.objects.create(
            url=data.get('url', f'http://example.com/article-{int(time.time())}'),
            title=data.get('title', 'Untitled Article'),
            source=data.get('source', 'Unknown Source'),
            raw_text=data.get('raw_text', ''),
            published_date=timezone.now() if not data.get('published_date') else None,
            classification=data.get('classification', 'RESTRICTED'),
            priority=data.get('priority', 2),
            processing_status='pending'
        )
        
        # Mock NLP processing for Step 1
        time.sleep(0.5)  # Simulate processing time
        
        # Mock translation results
        mock_translation = {
            'detected_language': 'fr' if 'français' in article.raw_text.lower() else 'en',
            'translated_text': article.raw_text,  # Mock: same text for now
            'processing_time': 0.3
        }
        
        # Mock NER results with Cameroon-specific entities
        mock_entities = []
        text_lower = article.raw_text.lower()
        
        # Check for common Cameroon locations
        cameroon_locations = {
            'yaoundé': {'latitude': 3.8480, 'longitude': 11.5021},
            'douala': {'latitude': 4.0511, 'longitude': 9.7679},
            'bamenda': {'latitude': 5.9631, 'longitude': 10.1591},
            'maroua': {'latitude': 10.5969, 'longitude': 14.3197},
            'garoua': {'latitude': 9.3265, 'longitude': 13.3971},
        }
        
        for location, coords in cameroon_locations.items():
            if location in text_lower:
                mock_entities.append({
                    'word': location.title(),
                    'entity_group': 'LOCATION',
                    'confidence': 0.95
                })
                # Set article coordinates to first found location
                if not article.latitude:
                    article.latitude = coords['latitude']
                    article.longitude = coords['longitude']
                break
        
        # Add mock person and organization entities
        if 'président' in text_lower or 'president' in text_lower:
            mock_entities.append({
                'word': 'Paul Biya',
                'entity_group': 'PERSON',
                'confidence': 0.90
            })
        
        if 'battalion' in text_lower or 'military' in text_lower:
            mock_entities.append({
                'word': 'Rapid Intervention Battalion',
                'entity_group': 'ORGANIZATION', 
                'confidence': 0.85
            })
        
        # Update article with mock results
        article.processed_json = {
            'translation': mock_translation,
            'entities': {
                'entities': mock_entities,
                'entity_count': len(mock_entities),
                'processing_time': 0.5
            }
        }
        article.entity_count = len(mock_entities)
        article.processing_status = 'processed'
        
        # Set default location if none found (Yaoundé)
        if not article.latitude:
            article.latitude = 3.8480
            article.longitude = 11.5021
            
        article.save()
        
        # Return response similar to demo
        response = {
            'success': True,
            'message': 'Article processed successfully through Project Sentinel Django backend',
            'step': 1,
            'nlp_mode': 'mock',
            'article': {
                'id': str(article.id),
                'title': article.title,
                'source': article.source,
                'processing_status': article.processing_status,
                'priority': article.priority,
                'classification': article.classification,
                'entity_count': article.entity_count,
                'coordinates': article.coordinates,
                'processing_results': {
                    'translation': mock_translation,
                    'entities': {
                        'entity_count': len(mock_entities),
                        'processing_time': 0.5
                    }
                }
            }
        }
        
        return Response(response, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': 'Processing failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )









