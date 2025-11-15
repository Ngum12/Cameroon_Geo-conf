"""
Project Sentinel - Real NLP Service Integration
Connects Django backend to actual Translation and NER services
"""
import requests
import json
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import NewsArticle

# Service endpoints
TRANSLATION_SERVICE_URL = "http://127.0.0.1:8004/translate"
NER_SERVICE_URL = "http://127.0.0.1:8005/analyze-entities"

@api_view(['POST'])
def process_article_real_nlp(request):
    """
    Process article with REAL NLP services - Translation + NER
    """
    start_time = time.time()
    
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['title', 'raw_text', 'source', 'url']
        for field in required_fields:
            if not data.get(field):
                return Response({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create article in database
        article = NewsArticle.objects.create(
            url=data['url'],
            title=data['title'],
            source=data['source'],
            raw_text=data['raw_text'],
            published_date=timezone.now() if not data.get('published_date') else None,
            classification=data.get('classification', 'RESTRICTED'),
            priority=data.get('priority', 2),
            processing_status='translating'
        )
        
        # STEP 1: Call Translation Service
        translation_start = time.time()
        try:
            translation_response = requests.post(
                TRANSLATION_SERVICE_URL,
                json={'text': article.raw_text},
                headers={'Content-Type': 'application/json'},
                timeout=300  # 5 minutes for complex French intelligence processing
            )
            translation_response.raise_for_status()
            translation_data = translation_response.json()
            translation_time = time.time() - translation_start
            
        except Exception as e:
            article.processing_status = 'failed'
            article.save()
            return Response({
                'success': False,
                'error': f'Translation service error: {str(e)}',
                'article_id': str(article.id)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Update article with translation
        article.language = translation_data.get('detected_language', 'unknown')
        translated_text = translation_data.get('translated_text', article.raw_text)
        
        # STEP 2: Call NER Service on translated text
        article.processing_status = 'extracting_entities'
        article.save()
        
        ner_start = time.time()
        try:
            ner_response = requests.post(
                NER_SERVICE_URL,
                json={'text': translated_text},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            ner_response.raise_for_status()
            ner_data = ner_response.json()
            ner_time = time.time() - ner_start
            
        except Exception as e:
            article.processing_status = 'failed'
            article.save()
            return Response({
                'success': False,
                'error': f'NER service error: {str(e)}',
                'article_id': str(article.id)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # STEP 3: Process entities and extract locations
        entities = ner_data.get('entities', [])
        locations = []
        persons = []
        organizations = []
        
        for entity in entities:
            entity_text = entity.get('text', '')
            entity_label = entity.get('label', '')
            
            if entity_label == 'LOCATION':
                locations.append(entity_text)
            elif entity_label == 'PERSON':
                persons.append(entity_text)
            elif entity_label == 'ORGANIZATION':
                organizations.append(entity_text)
        
        # Set coordinates based on known Cameroon locations
        cameroon_locations = {
            'yaoundé': {'latitude': 3.8480, 'longitude': 11.5021},
            'yaounde': {'latitude': 3.8480, 'longitude': 11.5021},
            'douala': {'latitude': 4.0511, 'longitude': 9.7679},
            'bamenda': {'latitude': 5.9631, 'longitude': 10.1591},
            'maroua': {'latitude': 10.5969, 'longitude': 14.3197},
            'garoua': {'latitude': 9.3265, 'longitude': 13.3971},
            'buea': {'latitude': 4.1560, 'longitude': 9.2349},
        }
        
        for location in locations:
            location_lower = location.lower().strip()
            if location_lower in cameroon_locations:
                coords = cameroon_locations[location_lower]
                article.latitude = coords['latitude']
                article.longitude = coords['longitude']
                break
        
        # STEP 4: Store all results
        processing_results = {
            'translation': {
                'detected_language': translation_data.get('detected_language'),
                'translated_text': translated_text,
                'processing_time': translation_time,
                'confidence_score': translation_data.get('confidence_score')
            },
            'entities': {
                'total_entities': len(entities),
                'locations': locations,
                'persons': persons,
                'organizations': organizations,
                'processing_time': ner_time,
                'raw_entities': entities[:10]  # Store first 10 for debugging
            }
        }
        
        # Update article with results
        article.processed_json = processing_results
        article.entity_count = len(entities)
        article.content_length = len(article.raw_text)
        article.word_count = len(article.raw_text.split())
        article.processing_status = 'processed'
        article.save()
        
        total_time = time.time() - start_time
        
        # Return success response
        return Response({
            'success': True,
            'message': 'Article processed successfully with REAL NLP services',
            'article_id': str(article.id),
            'processing_time': round(total_time, 2),
            'services_used': {
                'translation': 'Helsinki-NLP CPU-optimized',
                'ner': 'XLM-RoBERTa multilingual'
            },
            'results': {
                'language_detected': article.language,
                'entities_found': article.entity_count,
                'locations_found': len(locations),
                'persons_found': len(persons),
                'coordinates_set': bool(article.latitude and article.longitude),
                'translation_time': round(translation_time, 2),
                'ner_time': round(ner_time, 2)
            },
            'article_preview': {
                'title': article.title,
                'source': article.source,
                'status': article.processing_status,
                'priority': article.priority,
                'classification': article.classification
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'processing_time': round(time.time() - start_time, 2)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



