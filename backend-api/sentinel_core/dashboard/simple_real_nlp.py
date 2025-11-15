"""
Simplified Real NLP Integration for debugging
"""
import requests
import time
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def test_real_nlp_simple(request):
    """
    Simple test of real NLP services without database operations
    """
    try:
        data = request.data
        text = data.get('raw_text', 'Hello world')
        
        # Test translation service
        translation_response = requests.post(
            "http://127.0.0.1:8001/translate",
            json={'text': text},
            timeout=10
        )
        translation_data = translation_response.json()
        
        # Test NER service  
        translated_text = translation_data.get('translated_text', text)
        ner_response = requests.post(
            "http://127.0.0.1:8002/analyze-entities", 
            json={'text': translated_text},
            timeout=10
        )
        ner_data = ner_response.json()
        
        return Response({
            'success': True,
            'original_text': text,
            'translation': translation_data,
            'ner_results': {
                'entity_count': len(ner_data.get('entities', [])),
                'entities': ner_data.get('entities', [])[:5]  # First 5 entities
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        })



