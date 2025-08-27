# -*- coding: utf-8 -*-
"""
Project Sentinel Dashboard Utilities
Cameroon Defense Force OSINT Analysis System

Utility functions for text processing, geocoding, and data analysis.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from django.contrib.gis.geos import Point

logger = logging.getLogger(__name__)


def detect_language(text: str) -> str:
    """
    Detect the language of input text using pattern matching.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Language code ('en', 'fr', or 'auto')
    """
    if not text or len(text.strip()) < 10:
        return 'auto'
    
    text_lower = text.lower().strip()
    words = text_lower.split()
    
    if len(words) < 5:
        return 'auto'
    
    # French language indicators
    french_indicators = {
        'articles': ['le', 'la', 'les', 'un', 'une', 'des', 'du', 'de'],
        'prepositions': ['dans', 'pour', 'avec', 'sur', 'sous', 'par', 'sans'],
        'conjunctions': ['et', 'ou', 'mais', 'donc', 'car', 'ni'],
        'common_words': ['est', 'sont', 'avoir', 'être', 'faire', 'aller', 'voir'],
        'pronouns': ['je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles']
    }
    
    # English language indicators
    english_indicators = {
        'articles': ['the', 'a', 'an'],
        'prepositions': ['in', 'on', 'at', 'for', 'with', 'by', 'from', 'to', 'of'],
        'conjunctions': ['and', 'or', 'but', 'so', 'yet', 'nor'],
        'common_words': ['is', 'are', 'have', 'has', 'will', 'would', 'could', 'should'],
        'pronouns': ['i', 'you', 'he', 'she', 'we', 'they', 'it', 'this', 'that']
    }
    
    # Count French indicators
    french_score = 0
    for category, indicators in french_indicators.items():
        french_score += sum(1 for word in words if word in indicators)
    
    # Count English indicators
    english_score = 0
    for category, indicators in english_indicators.items():
        english_score += sum(1 for word in words if word in indicators)
    
    # Determine language based on scores
    if french_score > english_score * 1.5:  # French bias for Cameroon
        return 'fr'
    elif english_score > french_score:
        return 'en'
    else:
        return 'auto'


def extract_locations(text: str) -> List[str]:
    """
    Extract potential location names from text using pattern matching.
    
    Args:
        text: Input text to analyze
        
    Returns:
        List of potential location names
    """
    locations = []
    
    # Known Cameroon locations
    cameroon_locations = {
        'cities': [
            'yaoundé', 'yaounde', 'douala', 'bamenda', 'bafoussam', 'garoua',
            'maroua', 'ngaoundéré', 'ngaoundere', 'bertoua', 'buea', 'limbe',
            'kumba', 'edea', 'loum', 'nkongsamba', 'foumban', 'tiko',
            'kribi', 'sangmelima', 'ebolowa', 'mbalmayo', 'akonolinga'
        ],
        'regions': [
            'adamawa', 'centre', 'east', 'far north', 'littoral', 'north',
            'northwest', 'north-west', 'south', 'southwest', 'south-west', 'west',
            'extrême-nord', 'nord-ouest', 'sud-ouest'
        ],
        'countries': [
            'cameroon', 'cameroun', 'nigeria', 'chad', 'tchad',
            'central african republic', 'equatorial guinea', 'gabon'
        ]
    }
    
    text_lower = text.lower()
    
    # Check for known locations
    for category, location_list in cameroon_locations.items():
        for location in location_list:
            if location in text_lower:
                # Try to find the original case version
                pattern = re.compile(re.escape(location), re.IGNORECASE)
                matches = pattern.finditer(text)
                for match in matches:
                    original_text = text[match.start():match.end()]
                    if original_text not in locations:
                        locations.append(original_text)
    
    # Look for capitalized words that might be locations
    # Pattern: Capital letter followed by lowercase letters
    location_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'
    potential_locations = re.findall(location_pattern, text)
    
    # Filter potential locations
    common_words = {
        'The', 'This', 'That', 'These', 'Those', 'President', 'Minister',
        'Government', 'Minister', 'General', 'Colonel', 'Major', 'Captain',
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    }
    
    for location in potential_locations:
        if (location not in common_words and 
            len(location) > 3 and 
            location not in locations):
            locations.append(location)
    
    return locations[:10]  # Limit to top 10 locations


def geocode_location(location_name: str) -> Optional[Dict[str, float]]:
    """
    Geocode a location name to coordinates.
    
    This is a simplified implementation with known Cameroon locations.
    In production, you would integrate with a proper geocoding service.
    
    Args:
        location_name: Name of the location to geocode
        
    Returns:
        Dictionary with latitude and longitude, or None if not found
    """
    # Comprehensive Cameroon location database
    location_database = {
        # Major cities
        'yaoundé': {'latitude': 3.8480, 'longitude': 11.5021},
        'yaounde': {'latitude': 3.8480, 'longitude': 11.5021},
        'douala': {'latitude': 4.0511, 'longitude': 9.7679},
        'bamenda': {'latitude': 5.9631, 'longitude': 10.1591},
        'bafoussam': {'latitude': 5.4781, 'longitude': 10.4167},
        'garoua': {'latitude': 9.3265, 'longitude': 13.3971},
        'maroua': {'latitude': 10.5969, 'longitude': 14.3197},
        'ngaoundéré': {'latitude': 7.3167, 'longitude': 13.5833},
        'ngaoundere': {'latitude': 7.3167, 'longitude': 13.5833},
        'bertoua': {'latitude': 4.5777, 'longitude': 13.6836},
        'buea': {'latitude': 4.1559, 'longitude': 9.2928},
        'limbe': {'latitude': 4.0186, 'longitude': 9.2105},
        'kumba': {'latitude': 4.6371, 'longitude': 9.4469},
        'edea': {'latitude': 3.7969, 'longitude': 10.1350},
        'loum': {'latitude': 4.7181, 'longitude': 9.7336},
        'nkongsamba': {'latitude': 4.9547, 'longitude': 9.9386},
        'foumban': {'latitude': 5.7269, 'longitude': 10.9004},
        'tiko': {'latitude': 4.0719, 'longitude': 9.3606},
        'kribi': {'latitude': 2.9394, 'longitude': 9.9078},
        'sangmelima': {'latitude': 2.9294, 'longitude': 11.9981},
        'ebolowa': {'latitude': 2.9156, 'longitude': 11.1544},
        'mbalmayo': {'latitude': 3.5186, 'longitude': 11.5036},
        'akonolinga': {'latitude': 3.7731, 'longitude': 12.2506},
        
        # Regions (using regional capitals)
        'adamawa': {'latitude': 7.3167, 'longitude': 13.5833},  # Ngaoundéré
        'centre': {'latitude': 3.8480, 'longitude': 11.5021},   # Yaoundé
        'east': {'latitude': 4.5777, 'longitude': 13.6836},     # Bertoua
        'far north': {'latitude': 10.5969, 'longitude': 14.3197}, # Maroua
        'littoral': {'latitude': 4.0511, 'longitude': 9.7679},  # Douala
        'north': {'latitude': 9.3265, 'longitude': 13.3971},    # Garoua
        'northwest': {'latitude': 5.9631, 'longitude': 10.1591}, # Bamenda
        'north-west': {'latitude': 5.9631, 'longitude': 10.1591}, # Bamenda
        'south': {'latitude': 2.9156, 'longitude': 11.1544},    # Ebolowa
        'southwest': {'latitude': 4.1559, 'longitude': 9.2928}, # Buea
        'south-west': {'latitude': 4.1559, 'longitude': 9.2928}, # Buea
        'west': {'latitude': 5.4781, 'longitude': 10.4167},     # Bafoussam
        
        # French region names
        'extrême-nord': {'latitude': 10.5969, 'longitude': 14.3197},
        'nord-ouest': {'latitude': 5.9631, 'longitude': 10.1591},
        'sud-ouest': {'latitude': 4.1559, 'longitude': 9.2928},
        
        # Country
        'cameroon': {'latitude': 3.8480, 'longitude': 11.5021},
        'cameroun': {'latitude': 3.8480, 'longitude': 11.5021},
        
        # Neighboring countries
        'nigeria': {'latitude': 9.0820, 'longitude': 8.6753},
        'chad': {'latitude': 15.4542, 'longitude': 18.7322},
        'tchad': {'latitude': 15.4542, 'longitude': 18.7322},
        'central african republic': {'latitude': 6.6111, 'longitude': 20.9394},
        'equatorial guinea': {'latitude': 1.6508, 'longitude': 10.2679},
        'gabon': {'latitude': -0.8037, 'longitude': 11.6094},
    }
    
    # Normalize location name for lookup
    location_key = location_name.lower().strip()
    
    # Direct lookup
    if location_key in location_database:
        return location_database[location_key]
    
    # Try partial matching for compound names
    for key, coords in location_database.items():
        if key in location_key or location_key in key:
            return coords
    
    # Log unknown location for potential future addition
    logger.info(f"Unknown location for geocoding: {location_name}")
    
    return None


def create_point_from_coordinates(latitude: float, longitude: float) -> Point:
    """
    Create a Django GIS Point object from latitude and longitude.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        Point object in WGS84 (SRID 4326)
    """
    try:
        return Point(longitude, latitude, srid=4326)
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid coordinates: lat={latitude}, lon={longitude}, error={e}")
        return None


def calculate_distance_km(point1: Point, point2: Point) -> float:
    """
    Calculate distance between two points in kilometers.
    
    Args:
        point1: First point
        point2: Second point
        
    Returns:
        Distance in kilometers
    """
    try:
        # Transform to a projected coordinate system for accurate distance calculation
        # Using UTM Zone 33N which covers most of Cameroon
        point1_utm = point1.transform(32633, clone=True)
        point2_utm = point2.transform(32633, clone=True)
        
        # Distance in meters, convert to kilometers
        distance_m = point1_utm.distance(point2_utm)
        return distance_m / 1000.0
    
    except Exception as e:
        logger.error(f"Error calculating distance: {e}")
        return 0.0


def extract_keywords(text: str, max_keywords: int = 20) -> List[str]:
    """
    Extract keywords from text for search and analysis.
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    # Common stop words in English and French
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'must', 'shall', 'can', 'this', 'that', 'these', 'those',
        # French stop words
        'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'ou', 'mais',
        'dans', 'pour', 'avec', 'sur', 'sous', 'par', 'sans', 'est', 'sont',
        'était', 'étaient', 'être', 'avoir', 'je', 'tu', 'il', 'elle', 'nous',
        'vous', 'ils', 'elles', 'ce', 'cette', 'ces'
    }
    
    # Extract words (alphanumeric, 3+ characters)
    words = re.findall(r'\b[A-Za-z]{3,}\b', text.lower())
    
    # Filter stop words and count frequency
    word_freq = {}
    for word in words:
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return [keyword for keyword, freq in sorted_keywords[:max_keywords]]


def classify_article_priority(article_data: Dict) -> int:
    """
    Automatically classify article priority based on content analysis.
    
    Args:
        article_data: Dictionary containing article information
        
    Returns:
        Priority level (1=Critical, 2=High, 3=Medium, 4=Low)
    """
    # High priority keywords
    critical_keywords = [
        'attack', 'bomb', 'explosion', 'terrorist', 'boko haram',
        'ambush', 'kidnap', 'hostage', 'emergency', 'crisis'
    ]
    
    high_priority_keywords = [
        'military', 'army', 'security', 'police', 'operation',
        'conflict', 'violence', 'protest', 'strike', 'unrest'
    ]
    
    # Get text to analyze
    text_to_analyze = article_data.get('translated_text', '') or article_data.get('raw_text', '')
    text_lower = text_to_analyze.lower()
    
    # Count critical keywords
    critical_count = sum(1 for keyword in critical_keywords if keyword in text_lower)
    high_count = sum(1 for keyword in high_priority_keywords if keyword in text_lower)
    
    # Get entity information
    entities = article_data.get('entities', [])
    person_entities = [e for e in entities if e.get('entity_group') == 'PERSON']
    org_entities = [e for e in entities if e.get('entity_group') == 'ORGANIZATION']
    
    # Classification logic
    if critical_count >= 2 or any('boko haram' in text_lower, 'terrorist' in text_lower):
        return 1  # Critical
    elif critical_count >= 1 or high_count >= 3:
        return 2  # High
    elif high_count >= 1 or len(person_entities) >= 3 or len(org_entities) >= 2:
        return 3  # Medium
    else:
        return 4  # Low
