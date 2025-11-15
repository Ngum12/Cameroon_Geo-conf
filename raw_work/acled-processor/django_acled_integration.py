"""
PROJECT SENTINEL - DJANGO ACLED INTEGRATION
Cameroon Defense Force OSINT Intelligence System

Integration module for importing processed ACLED historical data into Django backend.
Provides foundation for ML conflict prediction model training.
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
from acled_data_processor import ACLEDProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DjangoACLEDIntegrator:
    """
    Integrator for importing ACLED data into Django Project Sentinel backend.
    """
    
    def __init__(self, django_base_url: str = "http://127.0.0.1:8000"):
        self.base_url = django_base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Project-Sentinel-ACLED-Integrator/1.0'
        })
        
        # API endpoints
        self.endpoints = {
            'health': f"{self.base_url}/health/",
            'process_article': f"{self.base_url}/api/v1/process-article-real/",
            'get_events': f"{self.base_url}/api/v1/events/",
        }
        
        self.processed_count = 0
        self.failed_count = 0
    
    def check_django_backend(self) -> bool:
        """Check if Django backend is available."""
        try:
            response = self.session.get(self.endpoints['health'], timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Django Backend: {data.get('status', 'healthy')}")
                logger.info(f"📊 Current articles: {data.get('articles_count', 0)}")
                return True
            else:
                logger.error(f"❌ Django health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Cannot connect to Django backend: {e}")
            return False
    
    def convert_acled_to_article_format(self, acled_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert processed ACLED event to Django NewsArticle format.
        """
        # Create synthetic article data from ACLED event
        event_date = acled_event.get('date', datetime.now().isoformat())
        event_type = acled_event.get('event_type', 'Unknown')
        location = acled_event.get('location', 'Unknown')
        admin1 = acled_event.get('admin1', 'Unknown')
        actor1 = acled_event.get('actor1', 'Unknown Actor')
        actor2 = acled_event.get('actor2', '')
        description = acled_event.get('description', '')
        fatalities = acled_event.get('fatalities', 0)
        severity = acled_event.get('severity_score', 0)
        
        # Create article-like title
        if fatalities > 0:
            title = f"Incident sécuritaire à {location}: {event_type} - {fatalities} victimes"
        else:
            title = f"Incident sécuritaire à {location}: {event_type}"
        
        # Create article-like content in French (for translation testing)
        if actor2:
            content = f"Un incident de type '{event_type}' impliquant {actor1} et {actor2} s'est produit à {location} dans la région {admin1}. "
        else:
            content = f"Un incident de type '{event_type}' impliquant {actor1} s'est produit à {location} dans la région {admin1}. "
        
        if description:
            content += f"Détails: {description}. "
        
        if fatalities > 0:
            content += f"Nombre de victimes: {fatalities}. "
        
        content += f"Niveau de gravité évalué: {severity:.1f}/100."
        
        # Create synthetic URL based on ACLED event
        event_id = acled_event.get('event_id', 'UNKNOWN')
        synthetic_url = f"https://acled-historical-data.org/cameroon/event/{event_id}"
        
        article_data = {
            'url': synthetic_url,
            'title': title,
            'raw_text': content,
            'source': f"ACLED Historical Database ({acled_event.get('source', 'Unknown')})",
            'language': 'fr',
            'historical_event': True,
            'acled_event_id': event_id,
            'original_date': event_date,
            'severity_score': severity,
            'fatalities': fatalities,
            'coordinates': acled_event.get('coordinates', [0, 0]),
            'conflict_category': acled_event.get('conflict_category', 'Unknown')
        }
        
        return article_data
    
    def import_acled_events_batch(self, acled_events: List[Dict[str, Any]], batch_size: int = 10) -> Dict[str, int]:
        """
        Import ACLED events in batches to Django backend.
        """
        logger.info(f"🔄 Starting batch import of {len(acled_events)} ACLED events")
        
        total_events = len(acled_events)
        processed = 0
        failed = 0
        
        for i in range(0, total_events, batch_size):
            batch = acled_events[i:i + batch_size]
            logger.info(f"📊 Processing batch {i//batch_size + 1}: events {i+1}-{min(i+batch_size, total_events)}")
            
            for acled_event in batch:
                try:
                    # Convert ACLED event to article format
                    article_data = self.convert_acled_to_article_format(acled_event)
                    
                    # Send to Django processing pipeline
                    response = self.session.post(
                        self.endpoints['process_article'],
                        data=json.dumps(article_data),
                        timeout=30
                    )
                    
                    if response.status_code == 201:
                        result = response.json()
                        processed += 1
                        logger.info(f"✅ Event {acled_event.get('event_id', 'N/A')}: Processed successfully")
                    else:
                        failed += 1
                        logger.warning(f"❌ Event {acled_event.get('event_id', 'N/A')}: Failed ({response.status_code})")
                        
                except Exception as e:
                    failed += 1
                    logger.error(f"❌ Error processing event {acled_event.get('event_id', 'N/A')}: {e}")
            
            # Rate limiting between batches
            import time
            time.sleep(1)
        
        self.processed_count = processed
        self.failed_count = failed
        
        logger.info(f"✅ Batch import complete: {processed} processed, {failed} failed")
        return {'processed': processed, 'failed': failed, 'total': total_events}
    
    def import_high_severity_events(self, acled_events: List[Dict[str, Any]], min_severity: float = 80.0) -> Dict[str, int]:
        """
        Import only high-severity ACLED events for priority analysis.
        """
        high_severity_events = [event for event in acled_events 
                              if event.get('severity_score', 0) >= min_severity]
        
        logger.info(f"🎯 Importing {len(high_severity_events)} high-severity events (>={min_severity})")
        return self.import_acled_events_batch(high_severity_events)
    
    def import_recent_events(self, acled_events: List[Dict[str, Any]], years_back: int = 5) -> Dict[str, int]:
        """
        Import recent ACLED events for current threat assessment.
        """
        cutoff_year = 2016 - years_back  # ACLED data goes to 2016
        recent_events = []
        
        for event in acled_events:
            try:
                event_year = event.get('year', 0)
                if event_year >= cutoff_year:
                    recent_events.append(event)
            except:
                continue
        
        logger.info(f"📅 Importing {len(recent_events)} recent events ({cutoff_year}-2016)")
        return self.import_acled_events_batch(recent_events)
    
    def import_regional_events(self, acled_events: List[Dict[str, Any]], target_regions: List[str]) -> Dict[str, int]:
        """
        Import ACLED events from specific regions.
        """
        regional_events = [event for event in acled_events 
                          if event.get('admin1', '') in target_regions]
        
        logger.info(f"🗺️ Importing {len(regional_events)} events from regions: {target_regions}")
        return self.import_acled_events_batch(regional_events)
    
    def get_import_summary(self) -> Dict[str, Any]:
        """Get summary of import process."""
        try:
            # Check final article count
            response = self.session.get(self.endpoints['health'], timeout=10)
            if response.status_code == 200:
                data = response.json()
                current_articles = data.get('articles_count', 0)
            else:
                current_articles = 0
            
            return {
                'processed_events': self.processed_count,
                'failed_events': self.failed_count,
                'success_rate': (self.processed_count / (self.processed_count + self.failed_count)) * 100 if (self.processed_count + self.failed_count) > 0 else 0,
                'total_articles_in_db': current_articles,
                'import_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Error getting import summary: {e}")
            return {}

def run_acled_integration():
    """Main function to run ACLED integration."""
    logger.info("🚀 STARTING ACLED HISTORICAL DATA INTEGRATION")
    logger.info("=" * 60)
    
    # Initialize components
    csv_path = "../data/acled-version-7-cameroon-1997-2016-actordyad-xlsx-6.xlsx - Sheet1.csv"
    processor = ACLEDProcessor(csv_path)
    integrator = DjangoACLEDIntegrator()
    
    # Check Django backend
    if not integrator.check_django_backend():
        logger.error("❌ Django backend not available. Aborting integration.")
        return False
    
    # Process ACLED data
    logger.info("📊 Processing ACLED data...")
    if processor.load_data() is None:
        logger.error("❌ Failed to load ACLED data")
        return False
    
    processed_events = processor.clean_and_process_events()
    if not processed_events:
        logger.error("❌ No events processed from ACLED data")
        return False
    
    # Analyze patterns
    patterns = processor.analyze_conflict_patterns()
    logger.info(f"✅ Processed {len(processed_events)} conflict events")
    
    # Convert to dictionaries for JSON handling
    events_data = []
    for event in processed_events:
        event_dict = {
            'event_id': event.event_id,
            'date': event.date.isoformat() if hasattr(event.date, 'isoformat') else str(event.date),
            'year': event.year,
            'event_type': event.event_type,
            'conflict_category': event.conflict_category,
            'actor1': event.actor1,
            'actor2': event.actor2,
            'location': event.location,
            'admin1': event.admin1,
            'admin2': event.admin2,
            'coordinates': [event.latitude, event.longitude],
            'description': event.description,
            'fatalities': event.fatalities,
            'severity_score': event.severity_score,
            'geographic_scope': event.geographic_scope,
            'source': event.source
        }
        events_data.append(event_dict)
    
    # Strategy 1: Import high-severity events first (>= 85)
    logger.info("🎯 PHASE 1: Importing high-severity events...")
    high_severity_results = integrator.import_high_severity_events(events_data, min_severity=85.0)
    
    # Strategy 2: Import recent events (2012-2016)
    logger.info("📅 PHASE 2: Importing recent events...")
    recent_results = integrator.import_recent_events(events_data, years_back=4)
    
    # Strategy 3: Import critical regional events
    critical_regions = ['Extrême-Nord', 'Sud-Ouest', 'Nord-Ouest', 'Centre', 'Littoral']
    logger.info(f"🗺️ PHASE 3: Importing events from critical regions...")
    regional_results = integrator.import_regional_events(events_data, critical_regions)
    
    # Get final summary
    summary = integrator.get_import_summary()
    
    # Display results
    logger.info("🏆 ACLED INTEGRATION COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"📊 HIGH-SEVERITY EVENTS: {high_severity_results.get('processed', 0)} processed")
    logger.info(f"📅 RECENT EVENTS: {recent_results.get('processed', 0)} processed") 
    logger.info(f"🗺️ REGIONAL EVENTS: {regional_results.get('processed', 0)} processed")
    logger.info(f"✅ TOTAL SUCCESS RATE: {summary.get('success_rate', 0):.1f}%")
    logger.info(f"💾 TOTAL ARTICLES IN DATABASE: {summary.get('total_articles_in_db', 0)}")
    logger.info("")
    logger.info("🎯 HISTORICAL DATA READY FOR ML TRAINING:")
    logger.info("   • Conflict pattern recognition")
    logger.info("   • Temporal trend analysis") 
    logger.info("   • Geographic hotspot modeling")
    logger.info("   • Actor behavior prediction")
    logger.info("   • Escalation pathway identification")
    logger.info("")
    logger.info("🚀 READY FOR PHASE 4: ENHANCED AI/ML MODELS!")
    
    return True

if __name__ == "__main__":
    run_acled_integration()


