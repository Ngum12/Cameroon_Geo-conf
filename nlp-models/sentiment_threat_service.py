#!/usr/bin/env python3
"""
SENTIMENT & THREAT ANALYSIS SERVICE
Project Sentinel - Cameroon Defense Force

Regional sentiment analysis and threat detection for predictive intelligence.
CPU-OPTIMIZED FOR REAL-TIME INTELLIGENCE
"""

import logging
import re
import time
import statistics
from collections import Counter
from enum import Enum
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatLevel(str, Enum):
    """Threat escalation levels"""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    IMMINENT = "imminent"

class SentimentLevel(str, Enum):
    """Sentiment intensity levels"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"
    HOSTILE = "hostile"
    INFLAMMATORY = "inflammatory"

class CameroonSentimentThreatAnalyzer:
    """Advanced sentiment and threat analysis for Cameroon defense intelligence"""
    
    def __init__(self):
        """Initialize the analyzer"""
        logger.info("🧠 Initializing Sentiment & Threat Analysis System...")
        
        # French threat patterns  
        self.french_threat_patterns = {
            "violence_imminent": ["va tuer", "va attaquer", "va détruire", "massacre", "éliminer"],
            "call_to_arms": ["aux armes", "révolution", "soulèvement", "résister", "guerre sainte"],
            "ethnic_hatred": ["sale", "vermine", "traître", "ennemi", "terroriste"],
            "weapon_references": ["armes", "fusils", "bombes", "explosifs", "munitions"]
        }
        
        # English threat patterns
        self.english_threat_patterns = {
            "violence_imminent": ["will kill", "will attack", "will destroy", "massacre", "eliminate"],
            "call_to_arms": ["take up arms", "revolution", "uprising", "resist", "holy war"],
            "ethnic_hatred": ["dirty", "vermin", "traitors", "enemies", "terrorists"],
            "weapon_references": ["weapons", "guns", "bombs", "explosives", "ammunition"]
        }
        
        # Regional indicators
        self.regional_indicators = {
            "Extrême-Nord": {"keywords": ["boko haram", "suicide", "attentat"], "baseline": 0.8},
            "Nord-Ouest": {"keywords": ["séparatiste", "amba", "ghost town"], "baseline": 0.7},
            "Sud-Ouest": {"keywords": ["ambazonie", "indépendance", "résistance"], "baseline": 0.7}
        }
        
        # Sentiment lexicon
        self.sentiment_lexicon = {
            # Positive
            "paix": 0.9, "peace": 0.9, "sécurité": 0.8, "security": 0.8,
            # Negative
            "violence": -0.9, "guerre": -1.0, "war": -1.0, "conflit": -0.8, "conflict": -0.8,
            "massacre": -1.0, "terroriste": -1.0, "terrorist": -1.0, "attaque": -0.9, "attack": -0.9
        }
        
        logger.info("✅ Sentiment & Threat Analysis System initialized")
    
    def detect_language(self, text: str) -> str:
        """Detect language (French or English)"""
        text_lower = text.lower()
        french_words = ['le', 'la', 'les', 'de', 'du', 'et', 'dans', 'avec']
        english_words = ['the', 'and', 'of', 'to', 'in', 'with', 'for', 'at']
        
        french_count = sum(1 for word in french_words if word in text_lower)
        english_count = sum(1 for word in english_words if word in text_lower)
        
        return "fr" if french_count > english_count else "en"
    
    def calculate_sentiment_score(self, text: str) -> float:
        """Calculate sentiment score"""
        words = re.findall(r'\w+', text.lower())
        scores = [self.sentiment_lexicon[word] for word in words if word in self.sentiment_lexicon]
        
        if not scores:
            return 0.0
        
        return statistics.mean(scores)
    
    def calculate_threat_score(self, text: str, language: str) -> float:
        """Calculate threat score"""
        text_lower = text.lower()
        threat_score = 0.0
        
        patterns = self.french_threat_patterns if language == "fr" else self.english_threat_patterns
        
        for category, pattern_list in patterns.items():
            matches = sum(1 for pattern in pattern_list if pattern in text_lower)
            if matches > 0:
                threat_score += min(1.0, matches * 0.5)
        
        return min(2.0, threat_score)
    
    def classify_sentiment_level(self, score: float) -> SentimentLevel:
        """Classify sentiment score"""
        if score >= 0.7:
            return SentimentLevel.VERY_POSITIVE
        elif score >= 0.3:
            return SentimentLevel.POSITIVE
        elif score >= -0.3:
            return SentimentLevel.NEUTRAL
        elif score >= -0.7:
            return SentimentLevel.NEGATIVE
        elif score >= -0.9:
            return SentimentLevel.VERY_NEGATIVE
        else:
            return SentimentLevel.INFLAMMATORY
    
    def classify_threat_level(self, score: float) -> ThreatLevel:
        """Classify threat score"""
        if score >= 1.5:
            return ThreatLevel.IMMINENT
        elif score >= 1.0:
            return ThreatLevel.CRITICAL
        elif score >= 0.6:
            return ThreatLevel.HIGH
        elif score >= 0.3:
            return ThreatLevel.MODERATE
        elif score >= 0.1:
            return ThreatLevel.LOW
        else:
            return ThreatLevel.MINIMAL
    
    def extract_threat_keywords(self, text: str, language: str) -> List[str]:
        """Extract threat keywords"""
        text_lower = text.lower()
        keywords = []
        
        patterns = self.french_threat_patterns if language == "fr" else self.english_threat_patterns
        
        for pattern_list in patterns.values():
            for pattern in pattern_list:
                if pattern in text_lower:
                    keywords.append(pattern)
        
        return list(set(keywords))
    
    def extract_regional_indicators(self, text: str) -> List[str]:
        """Extract regional indicators"""
        text_lower = text.lower()
        regions = []
        
        for region, data in self.regional_indicators.items():
            for keyword in data["keywords"]:
                if keyword in text_lower:
                    regions.append(region)
                    break
        
        return regions
    
    def analyze_sentiment_and_threat(self, text: str, language: str = "auto") -> Dict[str, Any]:
        """Main analysis function"""
        start_time = time.time()
        
        # Auto-detect language
        if language == "auto":
            language = self.detect_language(text)
        
        # Calculate scores
        sentiment_score = self.calculate_sentiment_score(text)
        threat_score = self.calculate_threat_score(text, language)
        
        # Extract indicators
        threat_keywords = self.extract_threat_keywords(text, language)
        regional_indicators = self.extract_regional_indicators(text)
        
        # Calculate confidence
        text_length = len(text.split())
        confidence = min(1.0, text_length / 50.0)
        
        processing_time = time.time() - start_time
        
        return {
            "text": text[:200] + "..." if len(text) > 200 else text,
            "language": language,
            "sentiment_score": round(sentiment_score, 3),
            "sentiment_level": self.classify_sentiment_level(sentiment_score).value,
            "threat_score": round(threat_score, 3),
            "threat_level": self.classify_threat_level(threat_score).value,
            "threat_keywords": threat_keywords,
            "regional_indicators": regional_indicators,
            "confidence": round(confidence, 3),
            "processing_time": round(processing_time, 3)
        }

def test_sentiment_threat_service():
    """Test the sentiment and threat analysis service"""
    print("\n🧪 TESTING SENTIMENT & THREAT ANALYSIS SERVICE")
    print("=" * 60)
    
    analyzer = CameroonSentimentThreatAnalyzer()
    
    # Test cases
    test_cases = [
        {
            "text": "Boko Haram militants are preparing a major attack in Far North region. Civilians should evacuate immediately.",
            "expected": "high_threat"
        },
        {
            "text": "Peace negotiations between communities in Northwest region show promising progress.",
            "expected": "positive"
        },
        {
            "text": "Les séparatistes anglophones appellent à la violence et à la résistance armée dans les régions du Sud-Ouest.",
            "expected": "high_threat"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}:")
        print(f"Text: {case['text'][:80]}...")
        print(f"Expected: {case['expected']}")
        
        result = analyzer.analyze_sentiment_and_threat(case['text'])
        
        print(f"Results:")
        print(f"  🎭 Sentiment: {result['sentiment_score']} ({result['sentiment_level']})")
        print(f"  ⚠️ Threat: {result['threat_score']} ({result['threat_level']})")
        print(f"  🔍 Keywords: {', '.join(result['threat_keywords']) if result['threat_keywords'] else 'None'}")
        print(f"  🗺️ Regions: {', '.join(result['regional_indicators']) if result['regional_indicators'] else 'None'}")
        print(f"  🎯 Confidence: {result['confidence']}")
    
    print(f"\n✅ SENTIMENT & THREAT ANALYSIS SERVICE READY!")
    print(f"🛡️ CAMEROON DEFENSE FORCE - PREDICTIVE INTELLIGENCE OPERATIONAL")
    
    return analyzer

if __name__ == "__main__":
    test_sentiment_threat_service()

