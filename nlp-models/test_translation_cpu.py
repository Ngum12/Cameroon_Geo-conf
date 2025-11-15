#!/usr/bin/env python3
"""
Test script for the CPU-optimized translation service
"""

import asyncio
from translation_service_cpu import load_translation_model, translate_french_to_english

async def test_translation():
    try:
        print('🔄 Loading lightweight Helsinki-NLP model...')
        await load_translation_model()
        
        print('✅ Model loaded! Testing French→English translation...')
        
        test_texts = [
            'Le président Paul Biya a rencontré les forces de défense du Cameroun à Douala hier.',
            'Les soldats camerounais ont sécurisé la zone frontalière.',
            'Le ministre de la défense a annoncé de nouvelles mesures de sécurité.'
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f'\n--- Test {i} ---')
            result = await translate_french_to_english(text)
            
            print('🇫🇷 French :', result['original_text'])
            print('🇺🇸 English:', result['translated_text'])
            print('🔍 Language:', result['detected_language'])
            print('⏱️  Time    :', f"{result['processing_time']:.2f}s")
            print('📊 Confidence:', f"{result['confidence_score']:.2f}")
        
        print('\n🎯 All translations SUCCESSFUL!')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_translation())




