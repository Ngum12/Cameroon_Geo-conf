#!/usr/bin/env python3
"""
Project Sentinel - Load Demo Data into Django Database
Cameroon Defense Force OSINT Analysis System
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentinel_core.step1_settings')
django.setup()

from django.utils import timezone
from sentinel_core.dashboard.models import NewsArticle

def load_demo_data():
    print("🇨🇲 PROJECT SENTINEL - Loading Demo Data")
    print("Cameroon Defense Force OSINT Analysis System")
    print("=" * 50)
    
    # Clear existing data
    NewsArticle.objects.all().delete()
    print("✓ Cleared existing articles")
    
    # Demo intelligence data
    demo_articles = [
        {
            'title': 'Security Operation in Northwest Region - Bamenda Sector',
            'source': 'Cameroon Tribune',
            'url': 'https://cameroon-tribune.cm/security-operation-bamenda-2024',
            'raw_text': 'Security forces from the Rapid Intervention Battalion conducted a successful operation in Bamenda, Northwest region. The operation aimed at improving security conditions following recent incidents. Colonel Jean Mbarga confirmed the mission was completed without casualties.',
            'latitude': 5.9631,
            'longitude': 10.1591,
            'priority': 2,
            'classification': 'RESTRICTED',
            'language': 'en',
            'processing_status': 'processed',
            'published_date': timezone.now() - timezone.timedelta(hours=8),
            'processed_json': {
                'translation': {
                    'detected_language': 'en',
                    'translated_text': 'Security forces from the Rapid Intervention Battalion conducted a successful operation in Bamenda, Northwest region. The operation aimed at improving security conditions following recent incidents. Colonel Jean Mbarga confirmed the mission was completed without casualties.'
                },
                'entities': {
                    'entities': [
                        {'word': 'Rapid Intervention Battalion', 'entity_group': 'ORGANIZATION', 'confidence': 0.98},
                        {'word': 'Bamenda', 'entity_group': 'LOCATION', 'confidence': 0.99},
                        {'word': 'Northwest region', 'entity_group': 'LOCATION', 'confidence': 0.97},
                        {'word': 'Colonel Jean Mbarga', 'entity_group': 'PERSON', 'confidence': 0.96}
                    ],
                    'entity_count': 4,
                    'processing_time': 0.8
                }
            }
        },
        {
            'title': 'Sommet Économique à Douala - Nouveaux Investissements',
            'source': 'Journal du Cameroun',
            'url': 'https://journalducameroun.com/sommet-economique-douala-2024',
            'raw_text': 'Le président Paul Biya a participé au sommet économique à Douala. Les ministres ont présenté les nouveaux projets d\'investissement pour la région du Littoral. Plus de 200 participants ont assisté à l\'événement.',
            'latitude': 4.0511,
            'longitude': 9.7679,
            'priority': 3,
            'classification': 'UNCLASSIFIED',
            'language': 'fr',
            'processing_status': 'processed',
            'published_date': timezone.now() - timezone.timedelta(hours=12),
            'processed_json': {
                'translation': {
                    'detected_language': 'fr',
                    'translated_text': 'President Paul Biya participated in the economic summit in Douala. The ministers presented new investment projects for the Littoral region. More than 200 participants attended the event.'
                },
                'entities': {
                    'entities': [
                        {'word': 'Paul Biya', 'entity_group': 'PERSON', 'confidence': 0.99},
                        {'word': 'Douala', 'entity_group': 'LOCATION', 'confidence': 0.98},
                        {'word': 'Littoral region', 'entity_group': 'LOCATION', 'confidence': 0.96}
                    ],
                    'entity_count': 3,
                    'processing_time': 0.6
                }
            }
        },
        {
            'title': 'Peacekeeping Mission Update - Far North Region',
            'source': 'Cameroon Intelligence Report',
            'url': 'https://cir.cm/peacekeeping-far-north-update-2024',
            'raw_text': 'The multinational joint task force operations in the Far North region continue near Maroua. General Valère Nka reported successful missions against insurgent activities. Local communities have reported improved security conditions.',
            'latitude': 10.5969,
            'longitude': 14.3197,
            'priority': 1,  # Critical
            'classification': 'RESTRICTED',
            'language': 'en',
            'processing_status': 'processed',
            'published_date': timezone.now() - timezone.timedelta(hours=18),
            'processed_json': {
                'translation': {
                    'detected_language': 'en',
                    'translated_text': 'The multinational joint task force operations in the Far North region continue near Maroua. General Valère Nka reported successful missions against insurgent activities. Local communities have reported improved security conditions.'
                },
                'entities': {
                    'entities': [
                        {'word': 'General Valère Nka', 'entity_group': 'PERSON', 'confidence': 0.98},
                        {'word': 'Maroua', 'entity_group': 'LOCATION', 'confidence': 0.99},
                        {'word': 'Far North region', 'entity_group': 'LOCATION', 'confidence': 0.97},
                        {'word': 'multinational joint task force', 'entity_group': 'ORGANIZATION', 'confidence': 0.95}
                    ],
                    'entity_count': 4,
                    'processing_time': 0.9
                }
            }
        }
    ]
    
    # Create articles in database
    created_count = 0
    for article_data in demo_articles:
        article = NewsArticle.objects.create(**article_data)
        article.entity_count = len(article.processed_json['entities']['entities'])
        article.save()
        created_count += 1
        print(f"✓ Created: {article.title[:50]}...")
    
    print("=" * 50)
    print(f"🎯 SUCCESS: {created_count} demo articles loaded")
    print("📊 Database now contains realistic Cameroon intelligence data")
    print("")
    print("📍 Geographic Coverage:")
    print("  - Northwest Region (Bamenda) - Security Operation")
    print("  - Littoral Region (Douala) - Economic Summit") 
    print("  - Far North Region (Maroua) - Peacekeeping Mission")
    print("")
    print("🔒 Classification Levels:")
    print("  - RESTRICTED: 2 articles")
    print("  - UNCLASSIFIED: 1 article")
    print("")
    print("⚡ Priority Levels:")
    print("  - Critical (1): 1 article")
    print("  - High (2): 1 article") 
    print("  - Medium (3): 1 article")
    print("")
    print("🇨🇲 CLASSIFICATION: RESTRICTED")
    print("Cameroon Defense Force - PROJECT SENTINEL")

if __name__ == '__main__':
    load_demo_data()









