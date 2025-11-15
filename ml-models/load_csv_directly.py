"""
Load ACLED data directly from CSV file and create ML-ready dataset.
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_acled_from_csv():
    """Load ACLED data directly from CSV file."""
    logger.info("📊 Loading ACLED data directly from CSV...")
    
    csv_path = "../data/acled-version-7-cameroon-1997-2016-actordyad-xlsx-6.xlsx - Sheet1.csv"
    output_path = "cameroon_events_ml_ready.json"
    
    try:
        # Load CSV data
        df = pd.read_csv(csv_path)
        logger.info(f"✅ Loaded {len(df)} rows from CSV")
        
        # Display column names to understand structure
        logger.info(f"📋 CSV Columns: {list(df.columns)}")
        
        # Convert to ML-ready format
        events = []
        
        for idx, row in df.iterrows():
            # Create event record
            event = {
                "event_id": str(row.get('EVENT_ID_CNTY', f'event_{idx}')),
                "date": str(row.get('EVENT_DATE', '')),
                "year": int(row.get('YEAR', 0)) if pd.notna(row.get('YEAR')) else 0,
                "admin1": str(row.get('ADMIN1', '')),
                "location": str(row.get('LOCATION', '')),
                "latitude": float(row.get('LATITUDE', 0.0)) if pd.notna(row.get('LATITUDE')) else 0.0,
                "longitude": float(row.get('LONGITUDE', 0.0)) if pd.notna(row.get('LONGITUDE')) else 0.0,
                "coordinates": [
                    float(row.get('LATITUDE', 0.0)) if pd.notna(row.get('LATITUDE')) else 0.0,
                    float(row.get('LONGITUDE', 0.0)) if pd.notna(row.get('LONGITUDE')) else 0.0
                ],
                "event_type": str(row.get('EVENT_TYPE', '')),
                "sub_event_type": str(row.get('SUB_EVENT_TYPE', '')),
                "conflict_category": str(row.get('EVENT_TYPE', 'Unknown')),
                "actor1": str(row.get('ACTOR1', '')),
                "actor2": str(row.get('ACTOR2', '')),
                "fatalities": int(row.get('FATALITIES', 0)) if pd.notna(row.get('FATALITIES')) else 0,
                "notes": str(row.get('NOTES', '')),
                "source": str(row.get('SOURCE', ''))
            }
            
            # Add severity score based on fatalities and event type
            fatalities = event['fatalities']
            if fatalities >= 50:
                severity = 95
            elif fatalities >= 20:
                severity = 85
            elif fatalities >= 10:
                severity = 75
            elif fatalities >= 5:
                severity = 65
            elif fatalities >= 1:
                severity = 55
            else:
                # Base severity on event type
                event_type = event['event_type'].lower()
                if 'violence' in event_type or 'battle' in event_type:
                    severity = 60
                elif 'riot' in event_type or 'protest' in event_type:
                    severity = 40
                else:
                    severity = 30
            
            event['severity_score'] = severity
            events.append(event)
            
            if len(events) % 100 == 0:
                logger.info(f"   Processed {len(events)} events...")
        
        # Create final dataset
        dataset = {
            "metadata": {
                "total_events": len(events),
                "source": "ACLED Cameroon 1997-2016 (Direct CSV Load)",
                "date_range": [
                    min(e['date'] for e in events if e['date']),
                    max(e['date'] for e in events if e['date'])
                ],
                "processing_timestamp": datetime.now().isoformat()
            },
            "events": events
        }
        
        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved {len(events)} events to: {output_path}")
        
        # Display sample statistics
        df_events = pd.DataFrame(events)
        logger.info(f"📊 Statistics:")
        logger.info(f"   • Total Events: {len(events)}")
        logger.info(f"   • Date Range: {df_events['year'].min()} - {df_events['year'].max()}")
        logger.info(f"   • Regions: {df_events['admin1'].nunique()} unique regions")
        logger.info(f"   • Total Fatalities: {df_events['fatalities'].sum()}")
        logger.info(f"   • Average Severity: {df_events['severity_score'].mean():.1f}")
        
        # Top regions by events
        top_regions = df_events['admin1'].value_counts().head()
        logger.info(f"   • Top Regions: {dict(top_regions)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error loading CSV data: {e}")
        return False

if __name__ == "__main__":
    success = load_acled_from_csv()
    if success:
        print("🎯 ACLED data loaded successfully from CSV!")
    else:
        print("❌ Failed to load ACLED data from CSV")

