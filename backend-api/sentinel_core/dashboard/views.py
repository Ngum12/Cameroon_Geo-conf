# -*- coding: utf-8 -*-
"""
Project Sentinel Dashboard Views
Cameroon Defense Force OSINT Analysis System

Views for processing articles and providing data to the frontend dashboard.
"""

import asyncio
import aiohttp
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import NewsArticle, ProcessingLog
from .serializers import NewsArticleSerializer, NewsArticleCreateSerializer
from .utils import detect_language, extract_locations, geocode_location

logger = logging.getLogger(__name__)


class HealthCheckView(View):
    """Simple health check endpoint."""
    
    def get(self, request):
        return JsonResponse({
            'status': 'healthy',
            'service': 'Project Sentinel Backend API',
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0'
        })


class ProcessArticleView(APIView):
    """
    View to process a new article through the complete NLP pipeline.
    
    This view accepts POST requests with article data, saves it to the database,
    and processes it through translation and NER services.
    """
    
    permission_classes = [AllowAny]  # Adjust based on security requirements
    
    async def call_translation_service(self, text: str, source_lang: str = "auto") -> Optional[Dict]:
        """Call the translation service asynchronously."""
        translation_config = settings.NLP_SERVICES['TRANSLATION_SERVICE']
        url = f"{translation_config['BASE_URL']}/translate"
        
        payload = {
            "text": text,
            "source_lang": source_lang
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=translation_config['TIMEOUT'])
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Translation service error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Translation service connection error: {e}")
            return None
    
    async def call_ner_service(self, text: str) -> Optional[Dict]:
        """Call the NER service asynchronously."""
        ner_config = settings.NLP_SERVICES['NER_SERVICE']
        url = f"{ner_config['BASE_URL']}/analyze-entities"
        
        payload = {
            "text": text
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=ner_config['TIMEOUT'])
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"NER service error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"NER service connection error: {e}")
            return None
    
    def detect_article_language(self, text: str) -> str:
        """Detect the language of the article text."""
        # Simple language detection based on common words
        text_lower = text.lower()
        
        # French indicators
        french_indicators = ['le', 'la', 'les', 'de', 'du', 'des', 'et', 'dans', 'pour', 'avec']
        french_count = sum(1 for word in french_indicators if word in text_lower)
        
        # English indicators
        english_indicators = ['the', 'and', 'to', 'of', 'in', 'for', 'with', 'on', 'is', 'are']
        english_count = sum(1 for word in english_indicators if word in text_lower)
        
        if french_count > english_count:
            return 'fr'
        elif english_count > french_count:
            return 'en'
        else:
            return 'auto'
    
    async def process_article_pipeline(self, article: NewsArticle) -> Dict[str, Any]:
        """
        Process article through the complete NLP pipeline.
        
        1. Detect language
        2. Translate to English if needed
        3. Extract named entities
        4. Geocode locations if found
        """
        results = {}
        
        try:
            # Step 1: Detect language
            detected_lang = self.detect_article_language(article.raw_text)
            article.language = detected_lang
            article.processing_status = 'translating'
            article.save()
            
            ProcessingLog.objects.create(
                article=article,
                operation='translation',
                status='started',
                message=f"Detected language: {detected_lang}"
            )
            
            # Step 2: Translation (if not English)
            text_for_ner = article.raw_text
            
            if detected_lang != 'en':
                logger.info(f"Translating article {article.id} from {detected_lang} to English")
                
                translation_result = await self.call_translation_service(
                    article.raw_text, 
                    detected_lang
                )
                
                if translation_result:
                    results['translation'] = translation_result
                    text_for_ner = translation_result.get('translated_text', article.raw_text)
                    
                    ProcessingLog.objects.create(
                        article=article,
                        operation='translation',
                        status='completed',
                        message="Translation successful",
                        processing_time=translation_result.get('processing_time', 0)
                    )
                else:
                    ProcessingLog.objects.create(
                        article=article,
                        operation='translation',
                        status='failed',
                        message="Translation service unavailable"
                    )
            else:
                results['translation'] = {
                    'translated_text': text_for_ner,
                    'detected_language': 'en',
                    'processing_time': 0.0
                }
            
            # Step 3: Named Entity Recognition
            article.processing_status = 'extracting_entities'
            article.save()
            
            ProcessingLog.objects.create(
                article=article,
                operation='ner_extraction',
                status='started',
                message="Starting entity extraction"
            )
            
            logger.info(f"Extracting entities from article {article.id}")
            
            ner_result = await self.call_ner_service(text_for_ner)
            
            if ner_result:
                results['entities'] = ner_result
                article.entity_count = ner_result.get('entity_count', 0)
                
                ProcessingLog.objects.create(
                    article=article,
                    operation='ner_extraction',
                    status='completed',
                    message=f"Extracted {article.entity_count} entities",
                    processing_time=ner_result.get('processing_time', 0)
                )
                
                # Step 4: Geocoding (extract location from entities)
                location_entities = [
                    entity for entity in ner_result.get('entities', [])
                    if entity.get('entity_group') == 'LOCATION'
                ]
                
                if location_entities and not article.location:
                    # Try to geocode the first location entity
                    first_location = location_entities[0]['word']
                    coordinates = await self.geocode_location(first_location)
                    
                    if coordinates:
                        article.set_coordinates(
                            coordinates['latitude'], 
                            coordinates['longitude']
                        )
                        
                        ProcessingLog.objects.create(
                            article=article,
                            operation='geocoding',
                            status='completed',
                            message=f"Geocoded location: {first_location}"
                        )
            else:
                ProcessingLog.objects.create(
                    article=article,
                    operation='ner_extraction',
                    status='failed',
                    message="NER service unavailable"
                )
            
            # Update article with results
            article.processed_json = results
            article.processing_status = 'processed'
            article.save()
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing article {article.id}: {e}")
            article.mark_processing_failed(str(e))
            return {'error': str(e)}
    
    async def geocode_location(self, location_name: str) -> Optional[Dict[str, float]]:
        """
        Geocode a location name to coordinates.
        This is a simplified implementation - in production you'd use a proper geocoding service.
        """
        # Cameroon-specific locations (simplified mapping)
        cameroon_locations = {
            'yaoundé': {'latitude': 3.8480, 'longitude': 11.5021},
            'yaounde': {'latitude': 3.8480, 'longitude': 11.5021},
            'douala': {'latitude': 4.0511, 'longitude': 9.7679},
            'bamenda': {'latitude': 5.9631, 'longitude': 10.1591},
            'bafoussam': {'latitude': 5.4781, 'longitude': 10.4167},
            'garoua': {'latitude': 9.3265, 'longitude': 13.3971},
            'maroua': {'latitude': 10.5969, 'longitude': 14.3197},
            'ngaoundéré': {'latitude': 7.3167, 'longitude': 13.5833},
            'bertoua': {'latitude': 4.5777, 'longitude': 13.6836},
            'buea': {'latitude': 4.1559, 'longitude': 9.2928},
            'cameroon': {'latitude': 3.8480, 'longitude': 11.5021},  # Default to capital
        }
        
        location_lower = location_name.lower().strip()
        return cameroon_locations.get(location_lower)
    
    def post(self, request):
        """
        Process a new article through the NLP pipeline.
        
        Expected JSON payload:
        {
            "url": "https://example.com/article",
            "title": "Article title",
            "source": "News Source",
            "raw_text": "Article content...",
            "published_date": "2024-01-01T12:00:00Z"  # Optional
        }
        """
        try:
            # Validate and create article
            serializer = NewsArticleCreateSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(
                    {'error': 'Invalid data', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create article instance
            with transaction.atomic():
                article = serializer.save()
                article.processing_status = 'pending'
                article.save()
                
                logger.info(f"Created new article: {article.id}")
            
            # Process article asynchronously
            try:
                # Run async processing
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(
                    self.process_article_pipeline(article)
                )
                loop.close()
                
                # Return processed article data
                article.refresh_from_db()
                response_serializer = NewsArticleSerializer(article)
                
                return Response({
                    'success': True,
                    'message': 'Article processed successfully',
                    'article': response_serializer.data,
                    'processing_results': results
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                logger.error(f"Error processing article {article.id}: {e}")
                article.mark_processing_failed(str(e))
                
                return Response({
                    'success': False,
                    'message': 'Article saved but processing failed',
                    'error': str(e),
                    'article_id': str(article.id)
                }, status=status.HTTP_202_ACCEPTED)
        
        except Exception as e:
            logger.error(f"Error in process_article view: {e}")
            return Response(
                {'error': 'Internal server error', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetEventsView(APIView):
    """
    View to return all processed articles as GeoJSON for frontend map visualization.
    """
    
    permission_classes = [AllowAny]  # Adjust based on security requirements
    
    def get(self, request):
        """
        Return processed articles as GeoJSON FeatureCollection.
        
        Query parameters:
        - limit: Maximum number of articles to return (default: 100)
        - days: Number of days back to search (default: 30)
        - source: Filter by news source
        - priority: Filter by priority level (1-4)
        """
        try:
            # Parse query parameters
            limit = min(int(request.GET.get('limit', 100)), 1000)  # Max 1000
            days = int(request.GET.get('days', 30))
            source_filter = request.GET.get('source')
            priority_filter = request.GET.get('priority')
            
            # Build queryset
            queryset = NewsArticle.objects.filter(
                processing_status='processed',
                location__isnull=False  # Only articles with location data
            ).order_by('-published_date', '-created_at')
            
            # Apply date filter
            if days > 0:
                cutoff_date = timezone.now() - timezone.timedelta(days=days)
                queryset = queryset.filter(created_at__gte=cutoff_date)
            
            # Apply source filter
            if source_filter:
                queryset = queryset.filter(source__icontains=source_filter)
            
            # Apply priority filter
            if priority_filter:
                try:
                    priority_int = int(priority_filter)
                    if 1 <= priority_int <= 4:
                        queryset = queryset.filter(priority=priority_int)
                except ValueError:
                    pass
            
            # Limit results
            articles = queryset[:limit]
            
            # Build GeoJSON FeatureCollection
            features = []
            
            for article in articles:
                if article.location:
                    # Create feature properties
                    properties = {
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
                    }
                    
                    # Add entity data
                    entities = article.entities
                    if entities:
                        properties['entities'] = {
                            'persons': [e['word'] for e in entities if e.get('entity_group') == 'PERSON'],
                            'locations': [e['word'] for e in entities if e.get('entity_group') == 'LOCATION'],
                            'organizations': [e['word'] for e in entities if e.get('entity_group') == 'ORGANIZATION'],
                        }
                    
                    # Add translated text preview
                    translated_text = article.translated_text
                    if translated_text:
                        properties['text_preview'] = translated_text[:200] + '...' if len(translated_text) > 200 else translated_text
                    
                    # Create GeoJSON feature
                    feature = {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [article.location.x, article.location.y]  # [longitude, latitude]
                        },
                        'properties': properties
                    }
                    
                    features.append(feature)
            
            # Create GeoJSON FeatureCollection
            geojson = {
                'type': 'FeatureCollection',
                'features': features,
                'metadata': {
                    'total_features': len(features),
                    'generated_at': timezone.now().isoformat(),
                    'query_parameters': {
                        'limit': limit,
                        'days': days,
                        'source': source_filter,
                        'priority': priority_filter,
                    }
                }
            }
            
            return Response(geojson, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error in get_events view: {e}")
            return Response(
                {'error': 'Internal server error', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ArticleDetailView(generics.RetrieveAPIView):
    """
    View to retrieve detailed information about a specific article.
    """
    
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleSerializer
    permission_classes = [AllowAny]


class ArticleListView(generics.ListAPIView):
    """
    View to list articles with filtering and pagination.
    """
    
    queryset = NewsArticle.objects.all().order_by('-created_at')
    serializer_class = NewsArticleSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()
        
        # Filter by processing status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(processing_status=status_filter)
        
        # Filter by source
        source_filter = self.request.query_params.get('source')
        if source_filter:
            queryset = queryset.filter(source__icontains=source_filter)
        
        # Filter by date range
        days = self.request.query_params.get('days')
        if days:
            try:
                days_int = int(days)
                cutoff_date = timezone.now() - timezone.timedelta(days=days_int)
                queryset = queryset.filter(created_at__gte=cutoff_date)
            except ValueError:
                pass
        
        return queryset


@api_view(['GET'])
@permission_classes([AllowAny])
def statistics_view(request):
    """
    Return statistics about the articles in the system.
    """
    try:
        from django.db.models import Count, Q
        from datetime import timedelta
        
        # Basic counts
        total_articles = NewsArticle.objects.count()
        processed_articles = NewsArticle.objects.filter(processing_status='processed').count()
        pending_articles = NewsArticle.objects.filter(processing_status='pending').count()
        failed_articles = NewsArticle.objects.filter(processing_status='failed').count()
        
        # Articles with location data
        located_articles = NewsArticle.objects.filter(location__isnull=False).count()
        
        # Recent articles (last 24 hours)
        recent_cutoff = timezone.now() - timedelta(hours=24)
        recent_articles = NewsArticle.objects.filter(created_at__gte=recent_cutoff).count()
        
        # Articles by source
        source_stats = NewsArticle.objects.values('source').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Articles by priority
        priority_stats = NewsArticle.objects.values('priority').annotate(
            count=Count('id')
        ).order_by('priority')
        
        # Processing status breakdown
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
            },
            'by_source': list(source_stats),
            'by_priority': list(priority_stats),
            'by_status': list(status_stats),
            'generated_at': timezone.now().isoformat(),
        }
        
        return Response(stats, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error in statistics view: {e}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
