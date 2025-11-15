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
        
        # Build queryset from real database - RETURN ALL ARTICLES TO MAKE SYSTEM ALIVE!
        queryset = NewsArticle.objects.all().order_by('-scraped_at')
        
        # Apply filters
        if days > 0:
            cutoff_date = timezone.now() - timezone.timedelta(days=days)
            queryset = queryset.filter(scraped_at__gte=cutoff_date)
        
        if source_filter:
            queryset = queryset.filter(source__icontains=source_filter)
            
        if priority_filter:
            try:
                priority_int = int(priority_filter)
                if 1 <= priority_int <= 5:  # Updated for 1-5 priority range
                    queryset = queryset.filter(priority=priority_int)
            except ValueError:
                pass
        
        # Limit results
        articles = queryset[:limit]
        
        # Region coordinates for mapping
        region_coordinates = {
            'Extreme-Nord': [14.2, 10.5],
            'Sud-Ouest': [9.3, 4.6],
            'Nord-Ouest': [10.4, 6.2],
            'Centre': [11.5, 4.0],
            'Littoral': [9.7, 4.0],
            'Nord': [13.4, 8.5],
            'Adamaoua': [12.3, 6.5],
            'Est': [14.5, 4.5],
            'Sud': [11.5, 2.8],
            'Ouest': [10.5, 5.5],
            'Unknown': [12.0, 6.0]  # Default Cameroon center
        }
        
        # Build GeoJSON features
        features = []
        for article in articles:
            # Get coordinates based on region
            coords = region_coordinates.get(article.region, region_coordinates['Unknown'])
            
            # Parse entities if they exist
            entity_groups = {'persons': [], 'locations': [], 'organizations': []}
            if article.entities:
                try:
                    if isinstance(article.entities, str):
                        import json
                        entities_data = json.loads(article.entities)
                    else:
                        entities_data = article.entities
                        
                    if isinstance(entities_data, list):
                        for entity in entities_data:
                            if isinstance(entity, dict):
                                group = entity.get('entity_group', '').upper()
                                word = entity.get('word', '')
                                if group == 'PERSON':
                                    entity_groups['persons'].append(word)
                                elif group in ['LOCATION', 'LOC']:
                                    entity_groups['locations'].append(word)
                                elif group in ['ORGANIZATION', 'ORG']:
                                    entity_groups['organizations'].append(word)
                except (json.JSONDecodeError, TypeError):
                    pass  # Keep empty entity groups if parsing fails
            
            # Create feature with actual model fields
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': coords
                },
                'properties': {
                    'id': str(article.id),
                    'title': article.title,
                    'source': article.source,
                    'url': article.url,
                    'published_date': article.published_date.isoformat() if article.published_date else None,
                    'scraped_at': article.scraped_at.isoformat(),
                    'priority': article.priority,
                    'region': article.region,
                    'classification': article.classification,
                    'threat_level': article.threat_level,
                    'processing_status': article.processing_status,
                    'sentiment_score': article.sentiment_score,
                    'entities': entity_groups,
                    'text_preview': article.content[:200] + '...' if len(article.content) > 200 else article.content,
                    'relevance_score': min(90, 50 + article.priority * 8),  # Calculate relevance based on priority
                    'raw_text': article.content
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
def get_statistics(request):
    """Return DYNAMIC system statistics - LIVE data from database"""
    try:
        from django.db.models import Count
        from datetime import timedelta
        
        # 🚀 LIVE DYNAMIC STATISTICS - NO MORE STATIC NUMBERS!
        total_articles = NewsArticle.objects.count()
        processed_articles = NewsArticle.objects.filter(processing_status='COMPLETED').count()
        pending_articles = NewsArticle.objects.filter(processing_status='PENDING').count()
        failed_articles = NewsArticle.objects.filter(processing_status='FAILED').count()
        
        # Recent articles (last 24 hours)
        recent_cutoff = timezone.now() - timedelta(hours=24)
        recent_articles = NewsArticle.objects.filter(scraped_at__gte=recent_cutoff).count()
        
        # This week's articles
        week_cutoff = timezone.now() - timedelta(days=7)
        weekly_articles = NewsArticle.objects.filter(scraped_at__gte=week_cutoff).count()
        
        # Priority breakdown (1=Critical, 2=High, 3=Medium, 4=Low, 5=Info)
        critical_priority = NewsArticle.objects.filter(priority=1).count()
        high_priority = NewsArticle.objects.filter(priority=2).count()
        medium_priority = NewsArticle.objects.filter(priority=3).count()
        low_priority = NewsArticle.objects.filter(priority=4).count()
        
        # Source breakdown - Top 10 sources
        source_stats = NewsArticle.objects.values('source').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Regional breakdown
        regional_stats = NewsArticle.objects.values('region').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Threat level distribution
        threat_stats = NewsArticle.objects.values('threat_level').annotate(
            count=Count('id')
        ).order_by('-count')
        priority_stats = NewsArticle.objects.values('priority').annotate(
            count=Count('id') 
        ).order_by('priority')
        
        # Status breakdown
        status_stats = NewsArticle.objects.values('processing_status').annotate(
            count=Count('id')
        )
        
        # Calculate processing rate
        processing_rate = (processed_articles / total_articles * 100) if total_articles > 0 else 0
        
        # 🎯 DYNAMIC STATISTICS RESPONSE - ALWAYS FRESH!
        stats = {
            'overview': {
                'total_reports': total_articles,  # This will now change dynamically!
                'processed': processed_articles,  # Dynamic processing count
                'pending_processing': pending_articles,
                'failed_processing': failed_articles,
                'recent_24h': recent_articles,
                'this_week': weekly_articles,
                'processing_rate': round(processing_rate, 1),
                'last_updated': timezone.now().isoformat()
            },
            'processing_stats': {
                'completed': processed_articles,
                'pending': pending_articles,
                'failed': failed_articles,
                'success_rate': round(processing_rate, 1)
            },
            'by_source': list(source_stats),
            'by_priority': [
                {'priority': 1, 'label': 'Critical', 'count': critical_priority},
                {'priority': 2, 'label': 'High', 'count': high_priority},
                {'priority': 3, 'label': 'Medium', 'count': medium_priority},
                {'priority': 4, 'label': 'Low', 'count': low_priority}
            ],
            'by_region': list(regional_stats),
            'threat_levels': {
                'critical': NewsArticle.objects.filter(threat_level='critical').count(),
                'high': NewsArticle.objects.filter(threat_level='high').count(),
                'medium': NewsArticle.objects.filter(threat_level='medium').count(),
                'low': NewsArticle.objects.filter(threat_level='low').count()
            },
            'system_info': {
                'name': 'Project Sentinel Intelligence System',
                'status': 'OPERATIONAL',
                'version': '2.0.0',
                'classification': 'RESTRICTED',
                'last_collection': timezone.now().isoformat(),
                'data_sources': len(source_stats),
                'coverage_regions': len(regional_stats)
            }
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









