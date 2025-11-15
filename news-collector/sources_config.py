"""
PROJECT SENTINEL - CAMEROON NEWS SOURCES CONFIGURATION
Cameroon Defense Force OSINT Intelligence System

This file contains the comprehensive list of Cameroon news sources
for automated geopolitical intelligence collection.
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass

class SourceType(Enum):
    RSS = "rss"
    WEB_SCRAPING = "web_scraping"
    API = "api"

class Language(Enum):
    FRENCH = "fr"
    ENGLISH = "en"
    BILINGUAL = "both"

@dataclass
class NewsSource:
    name: str
    url: str
    source_type: SourceType
    language: Language
    credibility_score: float  # 1-10 scale
    update_frequency: str  # in minutes
    region_focus: Optional[str] = None
    css_selectors: Optional[Dict[str, str]] = None
    rss_feed: Optional[str] = None
    is_active: bool = True
    keywords_focus: Optional[List[str]] = None

# CAMEROON MAJOR NEWS SOURCES
CAMEROON_NEWS_SOURCES = [
    
    # === GOVERNMENT & OFFICIAL SOURCES ===
    NewsSource(
        name="Cameroon Tribune",
        url="https://www.cameroon-tribune.cm",
        source_type=SourceType.WEB_SCRAPING,
        language=Language.BILINGUAL,
        credibility_score=9.0,
        update_frequency="60",
        css_selectors={
            "title": ".post-title h1",
            "content": ".post-content",
            "date": ".post-date",
            "author": ".post-author"
        },
        keywords_focus=["gouvernement", "sécurité", "défense", "politique", "military", "security"]
    ),
    
    # === FRENCH LANGUAGE SOURCES ===
    NewsSource(
        name="Journal du Cameroun",
        url="https://www.journalducameroun.com",
        source_type=SourceType.WEB_SCRAPING,
        language=Language.FRENCH,
        credibility_score=8.5,
        update_frequency="30",
        rss_feed="https://www.journalducameroun.com/feed/",
        css_selectors={
            "title": "h1.entry-title",
            "content": ".entry-content",
            "date": ".entry-date"
        },
        keywords_focus=["sécurité", "crise anglophone", "Boko Haram", "politique", "défense"]
    ),
    
    NewsSource(
        name="Mutations",
        url="https://www.mutations.com",
        source_type=SourceType.WEB_SCRAPING,
        language=Language.FRENCH,
        credibility_score=8.0,
        update_frequency="45",
        css_selectors={
            "title": ".article-title",
            "content": ".article-content",
            "date": ".article-date"
        },
        keywords_focus=["actualité", "politique", "sécurité", "économie"]
    ),
    
    NewsSource(
        name="Le Messager",
        url="https://www.lemessager.net",
        source_type=SourceType.WEB_SCRAPING,
        language=Language.FRENCH,
        credibility_score=7.5,
        update_frequency="60",
        keywords_focus=["investigation", "politique", "société", "sécurité"]
    ),
    
    NewsSource(
        name="L'Anecdote",
        url="https://lanecdote.com",
        source_type=SourceType.WEB_SCRAPING,
        language=Language.FRENCH,
        credibility_score=7.0,
        update_frequency="120",
        keywords_focus=["actualité", "société", "politique"]
    ),
    
    # === ENGLISH LANGUAGE SOURCES ===
    NewsSource(
        name="The Post Newspaper",
        url="https://www.thepostcameroon.com",
        source_type=SourceType.WEB_SCRAPING,
        language=Language.ENGLISH,
        credibility_score=8.5,
        update_frequency="30",
        region_focus="Anglophone regions",
        css_selectors={
            "title": "h1.post-title",
            "content": ".post-content",
            "date": ".post-date"
        },
        keywords_focus=["anglophone", "crisis", "separatist", "government", "security"]
    ),
    
    NewsSource(
        name="Cameroon Today",
        url="https://cameroontoday.com",
        source_type=SourceType.WEB_SCRAPING,
        language=Language.ENGLISH,
        credibility_score=8.0,
        update_frequency="45",
        keywords_focus=["politics", "security", "economy", "society"]
    ),
    
    NewsSource(
        name="Business in Cameroon",
        url="https://www.businessincameroon.com",
        source_type=SourceType.WEB_SCRAPING,
        language=Language.ENGLISH,
        credibility_score=8.5,
        update_frequency="60",
        css_selectors={
            "title": ".article-title",
            "content": ".article-body",
            "date": ".article-date"
        },
        keywords_focus=["economy", "politics", "infrastructure", "investment"]
    ),
    
    NewsSource(
        name="The Guardian Post",
        url="https://www.theguardianpost.com",
        source_type=SourceType.WEB_SCRAPING,
        language=Language.ENGLISH,
        credibility_score=7.5,
        update_frequency="90",
        keywords_focus=["news", "politics", "society", "investigation"]
    ),
    
    # === REGIONAL SOURCES ===
    NewsSource(
        name="Bamenda Online",
        url="https://bamendaonline.net",
        source_type=SourceType.WEB_SCRAPING,
        language=Language.ENGLISH,
        credibility_score=7.0,
        update_frequency="60",
        region_focus="Nord-Ouest",
        keywords_focus=["bamenda", "northwest", "anglophone", "crisis", "separatist"]
    ),
    
    NewsSource(
        name="Eden Newspaper",
        url="https://edennewspaper.net",
        source_type=SourceType.WEB_SCRAPING,
        language=Language.ENGLISH,
        credibility_score=6.5,
        update_frequency="120",
        region_focus="Sud-Ouest",
        keywords_focus=["buea", "southwest", "anglophone", "university"]
    ),
    
    NewsSource(
        name="The Sun Newspaper",
        url="https://www.thesunnewspaper.com",
        source_type=SourceType.WEB_SCRAPING,
        language=Language.ENGLISH,
        credibility_score=7.0,
        update_frequency="90",
        keywords_focus=["politics", "society", "investigation"]
    ),
    
    NewsSource(
        name="Cameroon Concord News",
        url="https://www.cameroonconcordnews.com",
        source_type=SourceType.WEB_SCRAPING,
        language=Language.ENGLISH,
        credibility_score=6.5,
        update_frequency="45",
        region_focus="Diaspora perspective",
        keywords_focus=["anglophone", "crisis", "diaspora", "politics", "human rights"]
    ),
    
    # === INTERNATIONAL SOURCES (CAMEROON FOCUS) ===
    NewsSource(
        name="BBC Afrique Cameroun",
        url="https://www.bbc.com/afrique",
        source_type=SourceType.RSS,
        language=Language.FRENCH,
        credibility_score=9.5,
        update_frequency="60",
        rss_feed="https://feeds.bbci.co.uk/afrique/rss.xml",
        keywords_focus=["Cameroun", "sécurité", "politique", "crise"]
    ),
    
    NewsSource(
        name="RFI Afrique Cameroun",
        url="https://www.rfi.fr/fr/afrique/",
        source_type=SourceType.RSS,
        language=Language.FRENCH,
        credibility_score=9.0,
        update_frequency="60",
        rss_feed="https://www.rfi.fr/fr/afrique/rss",
        keywords_focus=["Cameroun", "politique", "sécurité", "actualité"]
    ),
    
    NewsSource(
        name="Africa News Cameroon",
        url="https://www.africanews.com/",
        source_type=SourceType.RSS,
        language=Language.ENGLISH,
        credibility_score=8.5,
        update_frequency="90",
        rss_feed="https://www.africanews.com/api/en/rss",
        keywords_focus=["cameroon", "politics", "security", "economy"]
    ),
    
    NewsSource(
        name="Voice of America - Cameroon",
        url="https://www.voanews.com/cameroon",
        source_type=SourceType.WEB_SCRAPING,
        language=Language.ENGLISH,
        credibility_score=9.0,
        update_frequency="120",
        keywords_focus=["cameroon", "democracy", "politics", "security", "human rights"]
    ),
    
    # === SPECIALTY SOURCES ===
    NewsSource(
        name="Cameroon Info.Net",
        url="https://www.camerooninfo.net",
        source_type=SourceType.WEB_SCRAPING,
        language=Language.BILINGUAL,
        credibility_score=7.5,
        update_frequency="60",
        keywords_focus=["actualité", "politics", "société", "economy"]
    ),
    
    NewsSource(
        name="237Online",
        url="https://237online.com",
        source_type=SourceType.WEB_SCRAPING,
        language=Language.FRENCH,
        credibility_score=7.0,
        update_frequency="45",
        keywords_focus=["actualité", "société", "politique", "sport"]
    ),
    
    NewsSource(
        name="Camer.be",
        url="https://www.camer.be",
        source_type=SourceType.WEB_SCRAPING,
        language=Language.FRENCH,
        credibility_score=6.5,
        update_frequency="90",
        keywords_focus=["actualité", "politique", "société"]
    )
]

# GEOPOLITICAL KEYWORDS FOR FILTERING
GEOPOLITICAL_KEYWORDS = {
    'french': [
        # Security & Military
        'sécurité', 'défense', 'militaire', 'armée', 'gendarmerie', 'police', 
        'BIR', 'opération militaire', 'déploiement', 'sécurisation',
        
        # Political
        'gouvernement', 'ministre', 'président', 'opposition', 'parti politique',
        'élection', 'campagne', 'politique', 'diplomatie', 'relations internationales',
        
        # Conflict & Crisis
        'crise', 'conflit', 'tension', 'manifestation', 'protestation', 'grève',
        'violence', 'attaque', 'terrorisme', 'séparatiste', 'anglophone',
        'Boko Haram', 'enlèvement', 'kidnapping',
        
        # Regions & Places
        'Nord-Ouest', 'Sud-Ouest', 'Extrême-Nord', 'Yaoundé', 'Douala', 
        'Bamenda', 'Buea', 'Maroua', 'Garoua', 'frontière', 'Nigeria', 'Tchad',
        
        # Officials
        'Joseph Beti Assomo', 'Paul Biya', 'Dion Ngute', 'ministre de la défense',
        'gouverneur', 'préfet', 'maire', 'chef traditionnel',
        
        # Economic Security
        'pétrole', 'port', 'infrastructure', 'transport', 'économie', 'investissement'
    ],
    
    'english': [
        # Security & Military  
        'security', 'defense', 'military', 'army', 'gendarmerie', 'police',
        'BIR', 'military operation', 'deployment', 'counter-terrorism',
        
        # Political
        'government', 'minister', 'president', 'opposition', 'political party',
        'election', 'campaign', 'politics', 'diplomacy', 'international relations',
        
        # Conflict & Crisis
        'crisis', 'conflict', 'tension', 'demonstration', 'protest', 'strike',
        'violence', 'attack', 'terrorism', 'separatist', 'anglophone',
        'Boko Haram', 'kidnapping', 'insurgency',
        
        # Regions & Places
        'Northwest', 'Southwest', 'Far North', 'Yaounde', 'Douala',
        'Bamenda', 'Buea', 'Maroua', 'Garoua', 'border', 'Nigeria', 'Chad',
        
        # Officials
        'Joseph Beti Assomo', 'Paul Biya', 'Dion Ngute', 'defense minister',
        'governor', 'prefect', 'mayor', 'traditional ruler',
        
        # Economic Security
        'oil', 'port', 'infrastructure', 'transport', 'economy', 'investment'
    ]
}

# SOURCE RELIABILITY WEIGHTS
CREDIBILITY_WEIGHTS = {
    9.0: 1.0,   # Highest credibility (BBC, Government sources)
    8.5: 0.9,   # Very high credibility
    8.0: 0.8,   # High credibility
    7.5: 0.7,   # Good credibility
    7.0: 0.6,   # Moderate credibility
    6.5: 0.5,   # Lower credibility
    6.0: 0.4    # Lowest acceptable credibility
}

def get_active_sources() -> List[NewsSource]:
    """Return only active news sources."""
    return [source for source in CAMEROON_NEWS_SOURCES if source.is_active]

def get_sources_by_language(language: Language) -> List[NewsSource]:
    """Return sources filtered by language."""
    if language == Language.BILINGUAL:
        return get_active_sources()
    return [source for source in get_active_sources() 
            if source.language == language or source.language == Language.BILINGUAL]

def get_high_priority_sources() -> List[NewsSource]:
    """Return sources with credibility score >= 8.0."""
    return [source for source in get_active_sources() 
            if source.credibility_score >= 8.0]

def get_sources_by_region(region: str) -> List[NewsSource]:
    """Return sources focused on a specific region."""
    return [source for source in get_active_sources()
            if source.region_focus and region.lower() in source.region_focus.lower()]

# CONFIGURATION SUMMARY
print(f"📊 Total News Sources: {len(CAMEROON_NEWS_SOURCES)}")
print(f"✅ Active Sources: {len(get_active_sources())}")
print(f"🇫🇷 French Sources: {len(get_sources_by_language(Language.FRENCH))}")
print(f"🇬🇧 English Sources: {len(get_sources_by_language(Language.ENGLISH))}")
print(f"⭐ High Priority Sources: {len(get_high_priority_sources())}")


