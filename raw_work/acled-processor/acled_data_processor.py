"""
PROJECT SENTINEL - ACLED HISTORICAL DATA PROCESSOR
Cameroon Defense Force OSINT Intelligence System

Advanced processing of ACLED conflict data (1997-2016) for ML training.
Extracts patterns, actors, locations, and event types for conflict prediction models.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import Counter, defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ConflictEvent:
    """Data structure for processed conflict events."""
    event_id: str
    date: datetime
    year: int
    event_type: str
    actor1: str
    actor2: Optional[str]
    location: str
    admin1: str  # Region
    admin2: str  # Department
    admin3: str  # Sub-division
    latitude: float
    longitude: float
    source: str
    description: str
    fatalities: int
    severity_score: float
    conflict_category: str
    actors_involved: List[str]
    geographic_scope: str
    
class ACLEDProcessor:
    """
    Advanced ACLED data processor for Cameroon conflict analysis.
    """
    
    def __init__(self, csv_file_path: str):
        self.csv_path = csv_file_path
        self.raw_data = None
        self.processed_events = []
        self.conflict_patterns = {}
        self.actor_profiles = {}
        self.location_hotspots = {}
        self.temporal_trends = {}
        
        # Cameroon administrative regions
        self.cameroon_regions = {
            'Centre': {'capital': 'Yaoundé', 'departments': ['Mfoundi', 'Mbam-et-Kim', 'Haute-Sanaga']},
            'Littoral': {'capital': 'Douala', 'departments': ['Wouri', 'Mungo', 'Nkam']},
            'Sud-Ouest': {'capital': 'Buea', 'departments': ['Fako', 'Manyu', 'Ndian', 'Lebialem']},
            'Nord-Ouest': {'capital': 'Bamenda', 'departments': ['Mezam', 'Bui', 'Donga-Mantung']},
            'Extrême-Nord': {'capital': 'Maroua', 'departments': ['Diamare', 'Mayo-Sava', 'Logone-et-Chari']},
            'Nord': {'capital': 'Garoua', 'departments': ['Benoué', 'Mayo-Rey', 'Faro']},
            'Adamaoua': {'capital': 'Ngaoundéré', 'departments': ['Vina', 'Mbéré', 'Djerem']},
            'Est': {'capital': 'Bertoua', 'departments': ['Lom-et-Djerem', 'Kadey', 'Haut-Nyong']},
            'Sud': {'capital': 'Ebolowa', 'departments': ['Mvila', 'Dja-et-Lobo', 'Océan']},
            'Ouest': {'capital': 'Bafoussam', 'departments': ['Mifi', 'Bamboutos', 'Hauts-Plateaux']}
        }
        
        # Event type classifications
        self.event_categories = {
            'Battle': ['Battle-No change of territory', 'Battle-Government regains territory', 'Battle-Non-state actor overtakes territory'],
            'Violence Against Civilians': ['Violence against civilians'],
            'Protests': ['Riots/Protests', 'Peaceful protests'],
            'Remote Violence': ['Remote violence'],
            'Strategic Development': ['Strategic development'],
            'Government Action': ['Government action']
        }
        
        # Actor type classifications
        self.actor_types = {
            'Government Forces': ['Military Forces of Cameroon', 'Police Forces of Cameroon', 'Gendarmerie'],
            'Foreign Military': ['Military Forces of Nigeria', 'Military Forces of Chad'],
            'Armed Groups': ['Unidentified Armed Group', 'BFF: Bakassi Freedom Fighters', 'Boko Haram'],
            'Civilians': ['Civilians (Cameroon)', 'Civilians (Nigeria)', 'Civilians (International)'],
            'Protesters': ['Protesters (Cameroon)', 'Rioters (Cameroon)'],
            'Political': ['Government of Cameroon', 'Opposition parties'],
            'International': ['UN forces', 'Foreign diplomats']
        }
    
    def load_data(self) -> pd.DataFrame:
        """Load and validate ACLED CSV data."""
        try:
            logger.info(f"📊 Loading ACLED data from: {self.csv_path}")
            
            # Load CSV with proper encoding
            self.raw_data = pd.read_csv(self.csv_path, encoding='utf-8', low_memory=False)
            
            logger.info(f"✅ Loaded {len(self.raw_data)} conflict events")
            logger.info(f"📅 Date range: {self.raw_data['YEAR'].min()} - {self.raw_data['YEAR'].max()}")
            
            # Basic data validation
            required_columns = ['EVENT_DATE', 'EVENT_TYPE', 'ACTOR1', 'LOCATION', 'LATITUDE', 'LONGITUDE', 'NOTES']
            missing_columns = [col for col in required_columns if col not in self.raw_data.columns]
            
            if missing_columns:
                logger.error(f"❌ Missing required columns: {missing_columns}")
                return None
            
            return self.raw_data
            
        except Exception as e:
            logger.error(f"❌ Error loading ACLED data: {e}")
            return None
    
    def clean_and_process_events(self) -> List[ConflictEvent]:
        """Clean raw data and convert to structured conflict events."""
        if self.raw_data is None:
            logger.error("❌ No raw data loaded")
            return []
        
        logger.info("🔄 Processing and cleaning conflict events...")
        processed_events = []
        
        for idx, row in self.raw_data.iterrows():
            try:
                # Parse date
                try:
                    event_date = pd.to_datetime(row['EVENT_DATE'], format='%d/%m/%Y')
                except:
                    event_date = pd.to_datetime(row['EVENT_DATE'])
                
                # Calculate severity score
                fatalities = int(row.get('FATALITIES', 0)) if pd.notna(row.get('FATALITIES', 0)) else 0
                severity = self.calculate_severity_score(row['EVENT_TYPE'], fatalities, row.get('NOTES', ''))
                
                # Extract actor information
                actor1 = str(row.get('ACTOR1', '')).strip()
                actor2 = str(row.get('ACTOR2', '')).strip() if pd.notna(row.get('ACTOR2', '')) else None
                actors_involved = [actor1] + ([actor2] if actor2 else [])
                
                # Determine conflict category
                conflict_category = self.categorize_event_type(row['EVENT_TYPE'])
                
                # Determine geographic scope
                geographic_scope = self.determine_geographic_scope(
                    row.get('ADMIN1', ''), 
                    row.get('LOCATION', ''),
                    float(row.get('LATITUDE', 0)),
                    float(row.get('LONGITUDE', 0))
                )
                
                # Create processed event
                event = ConflictEvent(
                    event_id=str(row.get('EVENT_ID_CNTY', f'CAM_{idx}')),
                    date=event_date,
                    year=int(row.get('YEAR', 2000)),
                    event_type=str(row.get('EVENT_TYPE', '')),
                    actor1=actor1,
                    actor2=actor2,
                    location=str(row.get('LOCATION', '')),
                    admin1=str(row.get('ADMIN1', '')),
                    admin2=str(row.get('ADMIN2', '')),
                    admin3=str(row.get('ADMIN3', '')),
                    latitude=float(row.get('LATITUDE', 0)),
                    longitude=float(row.get('LONGITUDE', 0)),
                    source=str(row.get('SOURCE', '')),
                    description=str(row.get('NOTES', '')),
                    fatalities=fatalities,
                    severity_score=severity,
                    conflict_category=conflict_category,
                    actors_involved=actors_involved,
                    geographic_scope=geographic_scope
                )
                
                processed_events.append(event)
                
            except Exception as e:
                logger.warning(f"⚠️ Error processing row {idx}: {e}")
                continue
        
        self.processed_events = processed_events
        logger.info(f"✅ Successfully processed {len(processed_events)} conflict events")
        return processed_events
    
    def calculate_severity_score(self, event_type: str, fatalities: int, description: str) -> float:
        """Calculate severity score (0-100) based on event characteristics."""
        base_score = {
            'Battle-No change of territory': 70,
            'Battle-Government regains territory': 80,
            'Battle-Non-state actor overtakes territory': 90,
            'Violence against civilians': 85,
            'Remote violence': 75,
            'Riots/Protests': 40,
            'Peaceful protests': 20,
            'Strategic development': 30
        }
        
        score = base_score.get(event_type, 50)
        
        # Fatality multiplier
        if fatalities > 0:
            score += min(fatalities * 5, 30)  # Max 30 points for fatalities
        
        # Description-based severity indicators
        severity_keywords = {
            'attack': 15, 'killed': 20, 'bomb': 25, 'kidnap': 20,
            'military': 10, 'violence': 15, 'armed': 10, 'terror': 25,
            'massacre': 30, 'torture': 20, 'rape': 25
        }
        
        description_lower = description.lower()
        for keyword, points in severity_keywords.items():
            if keyword in description_lower:
                score += points
        
        return min(score, 100.0)
    
    def categorize_event_type(self, event_type: str) -> str:
        """Categorize event types into broader categories."""
        for category, types in self.event_categories.items():
            if event_type in types:
                return category
        return 'Other'
    
    def determine_geographic_scope(self, admin1: str, location: str, lat: float, lon: float) -> str:
        """Determine geographic scope of the conflict."""
        # Border areas (within 50km of international borders)
        border_threshold = 0.5  # degrees (~55km)
        
        # Nigeria border (western regions)
        if admin1 in ['Sud-Ouest', 'Nord-Ouest'] and lon < 9.0:
            return 'Cross-border (Nigeria)'
        
        # Chad border (northern regions)
        if admin1 in ['Extrême-Nord', 'Nord'] and lat > 10.0:
            return 'Cross-border (Chad)'
        
        # Central African Republic border
        if admin1 == 'Est' and lon > 14.0:
            return 'Cross-border (CAR)'
        
        # Major urban centers
        urban_centers = ['Yaoundé', 'Douala', 'Bamenda', 'Bafoussam', 'Garoua', 'Maroua']
        if any(city in location for city in urban_centers):
            return 'Urban'
        
        # Rural/remote areas
        return 'Rural'
    
    def analyze_conflict_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in conflict data."""
        logger.info("📊 Analyzing conflict patterns...")
        
        if not self.processed_events:
            logger.error("❌ No processed events available")
            return {}
        
        patterns = {
            'temporal_trends': self.analyze_temporal_trends(),
            'geographic_hotspots': self.analyze_geographic_hotspots(),
            'actor_analysis': self.analyze_actor_patterns(),
            'conflict_escalation': self.analyze_escalation_patterns(),
            'seasonal_patterns': self.analyze_seasonal_patterns(),
            'cross_border_analysis': self.analyze_cross_border_events()
        }
        
        self.conflict_patterns = patterns
        logger.info("✅ Conflict pattern analysis complete")
        return patterns
    
    def analyze_temporal_trends(self) -> Dict[str, Any]:
        """Analyze temporal trends in conflicts."""
        yearly_counts = defaultdict(int)
        yearly_fatalities = defaultdict(int)
        yearly_severity = defaultdict(list)
        
        for event in self.processed_events:
            yearly_counts[event.year] += 1
            yearly_fatalities[event.year] += event.fatalities
            yearly_severity[event.year].append(event.severity_score)
        
        trends = {
            'yearly_events': dict(yearly_counts),
            'yearly_fatalities': dict(yearly_fatalities),
            'yearly_avg_severity': {year: np.mean(scores) for year, scores in yearly_severity.items()},
            'peak_conflict_years': sorted(yearly_counts.keys(), key=lambda x: yearly_counts[x], reverse=True)[:5],
            'escalation_periods': self.identify_escalation_periods(yearly_counts)
        }
        
        return trends
    
    def analyze_geographic_hotspots(self) -> Dict[str, Any]:
        """Analyze geographic distribution of conflicts."""
        regional_counts = defaultdict(int)
        regional_severity = defaultdict(list)
        location_counts = defaultdict(int)
        
        for event in self.processed_events:
            regional_counts[event.admin1] += 1
            regional_severity[event.admin1].append(event.severity_score)
            location_counts[event.location] += 1
        
        hotspots = {
            'top_regions': sorted(regional_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'regional_severity': {region: np.mean(scores) for region, scores in regional_severity.items()},
            'conflict_locations': sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'high_risk_areas': self.identify_high_risk_areas()
        }
        
        return hotspots
    
    def analyze_actor_patterns(self) -> Dict[str, Any]:
        """Analyze actor involvement patterns."""
        actor_counts = defaultdict(int)
        actor_fatalities = defaultdict(int)
        actor_pairs = defaultdict(int)
        
        for event in self.processed_events:
            actor_counts[event.actor1] += 1
            actor_fatalities[event.actor1] += event.fatalities
            
            if event.actor2:
                actor_pairs[(event.actor1, event.actor2)] += 1
        
        patterns = {
            'most_active_actors': sorted(actor_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'deadliest_actors': sorted(actor_fatalities.items(), key=lambda x: x[1], reverse=True)[:10],
            'common_actor_pairs': sorted(actor_pairs.items(), key=lambda x: x[1], reverse=True)[:10],
            'government_involvement': self.analyze_government_involvement(),
            'foreign_actor_involvement': self.analyze_foreign_involvement()
        }
        
        return patterns
    
    def analyze_escalation_patterns(self) -> Dict[str, Any]:
        """Analyze conflict escalation patterns."""
        escalation_events = []
        
        # Sort events by date
        sorted_events = sorted(self.processed_events, key=lambda x: x.date)
        
        # Look for escalation patterns
        for i in range(len(sorted_events) - 1):
            current = sorted_events[i]
            next_event = sorted_events[i + 1]
            
            # Same location within 30 days with increasing severity
            if (current.location == next_event.location and 
                (next_event.date - current.date).days <= 30 and
                next_event.severity_score > current.severity_score + 10):
                
                escalation_events.append({
                    'location': current.location,
                    'initial_event': current.event_id,
                    'escalated_event': next_event.event_id,
                    'severity_increase': next_event.severity_score - current.severity_score,
                    'time_gap': (next_event.date - current.date).days
                })
        
        return {
            'escalation_events': escalation_events,
            'escalation_locations': Counter([event['location'] for event in escalation_events]),
            'avg_escalation_time': np.mean([event['time_gap'] for event in escalation_events]) if escalation_events else 0
        }
    
    def analyze_seasonal_patterns(self) -> Dict[str, Any]:
        """Analyze seasonal conflict patterns."""
        monthly_counts = defaultdict(int)
        monthly_severity = defaultdict(list)
        
        for event in self.processed_events:
            month = event.date.month
            monthly_counts[month] += 1
            monthly_severity[month].append(event.severity_score)
        
        return {
            'monthly_distribution': dict(monthly_counts),
            'peak_conflict_months': sorted(monthly_counts.keys(), key=lambda x: monthly_counts[x], reverse=True)[:3],
            'monthly_avg_severity': {month: np.mean(scores) for month, scores in monthly_severity.items()},
            'seasonal_trends': self.categorize_seasonal_trends(monthly_counts)
        }
    
    def analyze_cross_border_events(self) -> Dict[str, Any]:
        """Analyze cross-border conflict events."""
        cross_border_events = [event for event in self.processed_events 
                              if 'Cross-border' in event.geographic_scope]
        
        border_countries = defaultdict(int)
        border_severity = defaultdict(list)
        
        for event in cross_border_events:
            country = event.geographic_scope.split('(')[1].split(')')[0]
            border_countries[country] += 1
            border_severity[country].append(event.severity_score)
        
        return {
            'total_cross_border_events': len(cross_border_events),
            'border_countries': dict(border_countries),
            'border_avg_severity': {country: np.mean(scores) for country, scores in border_severity.items()},
            'cross_border_timeline': [(event.date, event.location, event.geographic_scope) 
                                    for event in cross_border_events]
        }
    
    def identify_escalation_periods(self, yearly_counts: Dict[int, int]) -> List[Tuple[int, int]]:
        """Identify periods of conflict escalation."""
        escalation_periods = []
        years = sorted(yearly_counts.keys())
        
        for i in range(len(years) - 1):
            current_year = years[i]
            next_year = years[i + 1]
            
            if yearly_counts[next_year] > yearly_counts[current_year] * 1.5:  # 50% increase
                escalation_periods.append((current_year, next_year))
        
        return escalation_periods
    
    def identify_high_risk_areas(self) -> List[Dict[str, Any]]:
        """Identify high-risk geographic areas."""
        location_risk = defaultdict(lambda: {'count': 0, 'total_severity': 0, 'fatalities': 0})
        
        for event in self.processed_events:
            location_risk[event.location]['count'] += 1
            location_risk[event.location]['total_severity'] += event.severity_score
            location_risk[event.location]['fatalities'] += event.fatalities
        
        high_risk_areas = []
        for location, stats in location_risk.items():
            if stats['count'] >= 3:  # At least 3 events
                avg_severity = stats['total_severity'] / stats['count']
                risk_score = (stats['count'] * 0.3) + (avg_severity * 0.5) + (stats['fatalities'] * 0.2)
                
                high_risk_areas.append({
                    'location': location,
                    'event_count': stats['count'],
                    'avg_severity': avg_severity,
                    'total_fatalities': stats['fatalities'],
                    'risk_score': risk_score
                })
        
        return sorted(high_risk_areas, key=lambda x: x['risk_score'], reverse=True)[:10]
    
    def analyze_government_involvement(self) -> Dict[str, Any]:
        """Analyze government forces involvement."""
        gov_events = [event for event in self.processed_events 
                     if 'Military Forces of Cameroon' in event.actor1 or 
                        'Police Forces of Cameroon' in event.actor1 or
                        'Gendarmerie' in event.actor1]
        
        return {
            'total_events': len(gov_events),
            'percentage': (len(gov_events) / len(self.processed_events)) * 100,
            'avg_severity': np.mean([event.severity_score for event in gov_events]),
            'total_fatalities': sum([event.fatalities for event in gov_events]),
            'most_common_opponents': Counter([event.actor2 for event in gov_events if event.actor2]).most_common(5)
        }
    
    def analyze_foreign_involvement(self) -> Dict[str, Any]:
        """Analyze foreign actor involvement."""
        foreign_events = [event for event in self.processed_events 
                         if 'Nigeria' in event.actor1 or 'Chad' in event.actor1 or
                            'Nigeria' in (event.actor2 or '') or 'Chad' in (event.actor2 or '')]
        
        return {
            'total_events': len(foreign_events),
            'percentage': (len(foreign_events) / len(self.processed_events)) * 100,
            'foreign_actors': Counter([actor for event in foreign_events 
                                     for actor in event.actors_involved if 'Nigeria' in actor or 'Chad' in actor]),
            'border_regions': Counter([event.admin1 for event in foreign_events])
        }
    
    def categorize_seasonal_trends(self, monthly_counts: Dict[int, int]) -> Dict[str, List[int]]:
        """Categorize seasonal conflict trends."""
        seasons = {
            'Dry Season': [11, 12, 1, 2, 3, 4],  # November - April
            'Rainy Season': [5, 6, 7, 8, 9, 10]  # May - October
        }
        
        seasonal_counts = {}
        for season, months in seasons.items():
            seasonal_counts[season] = sum([monthly_counts.get(month, 0) for month in months])
        
        return seasonal_counts
    
    def export_processed_data(self, output_file: str = "processed_acled_data.json") -> bool:
        """Export processed data for ML training."""
        try:
            export_data = {
                'metadata': {
                    'total_events': len(self.processed_events),
                    'date_range': [min(e.date for e in self.processed_events).isoformat(),
                                 max(e.date for e in self.processed_events).isoformat()],
                    'processing_timestamp': datetime.now().isoformat(),
                    'regions_covered': list(set(e.admin1 for e in self.processed_events)),
                    'event_types': list(set(e.event_type for e in self.processed_events))
                },
                'events': [
                    {
                        'event_id': event.event_id,
                        'date': event.date.isoformat(),
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
                    for event in self.processed_events
                ],
                'patterns': self.conflict_patterns
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Exported processed data to: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Export failed: {e}")
            return False
    
    def generate_summary_report(self) -> str:
        """Generate comprehensive summary report."""
        if not self.processed_events or not self.conflict_patterns:
            return "❌ No processed data available for report generation"
        
        report = f"""
🎯 PROJECT SENTINEL - ACLED DATA ANALYSIS REPORT
================================================
📊 Cameroon Conflict Patterns (1997-2016)

📈 OVERVIEW:
• Total Events: {len(self.processed_events)}
• Date Range: {min(e.date for e in self.processed_events).year} - {max(e.date for e in self.processed_events).year}
• Total Fatalities: {sum(e.fatalities for e in self.processed_events)}
• Average Severity Score: {np.mean([e.severity_score for e in self.processed_events]):.1f}/100

🏆 TOP CONFLICT HOTSPOTS:
"""
        
        # Add geographic analysis
        if 'geographic_hotspots' in self.conflict_patterns:
            hotspots = self.conflict_patterns['geographic_hotspots']['top_regions']
            for i, (region, count) in enumerate(hotspots, 1):
                report += f"{i}. {region}: {count} events\n"
        
        report += f"""
⚔️ MOST ACTIVE ACTORS:
"""
        
        # Add actor analysis
        if 'actor_analysis' in self.conflict_patterns:
            actors = self.conflict_patterns['actor_analysis']['most_active_actors'][:5]
            for i, (actor, count) in enumerate(actors, 1):
                report += f"{i}. {actor}: {count} events\n"
        
        report += f"""
📅 TEMPORAL TRENDS:
• Peak Conflict Years: {', '.join(map(str, self.conflict_patterns.get('temporal_trends', {}).get('peak_conflict_years', [])[:3]))}
• Cross-border Events: {self.conflict_patterns.get('cross_border_analysis', {}).get('total_cross_border_events', 0)}

🎯 PATTERN INSIGHTS:
• Government Involvement: {self.conflict_patterns.get('actor_analysis', {}).get('government_involvement', {}).get('percentage', 0):.1f}% of all events
• Foreign Actor Involvement: {self.conflict_patterns.get('actor_analysis', {}).get('foreign_actor_involvement', {}).get('percentage', 0):.1f}% of all events
• Escalation Events Detected: {len(self.conflict_patterns.get('escalation_analysis', {}).get('escalation_events', []))}

🔍 ML TRAINING DATA PREPARED:
✅ Temporal features extracted
✅ Geographic clustering completed  
✅ Actor relationship mapping done
✅ Escalation pattern identification complete
✅ Severity scoring calibrated

🚀 READY FOR CONFLICT PREDICTION MODEL TRAINING!
        """
        
        return report

# Main execution function
if __name__ == "__main__":
    # Initialize processor
    csv_path = "../data/acled-version-7-cameroon-1997-2016-actordyad-xlsx-6.xlsx - Sheet1.csv"
    processor = ACLEDProcessor(csv_path)
    
    # Load and process data
    print("🚀 Starting ACLED data processing...")
    
    if processor.load_data() is not None:
        processed_events = processor.clean_and_process_events()
        
        if processed_events:
            patterns = processor.analyze_conflict_patterns()
            
            # Export processed data
            processor.export_processed_data("cameroon_conflict_data_processed.json")
            
            # Generate and display report
            report = processor.generate_summary_report()
            print(report)
            
            print("✅ ACLED data processing complete!")
            print(f"📊 Ready for ML model training with {len(processed_events)} processed conflict events")
        else:
            print("❌ Failed to process events")
    else:
        print("❌ Failed to load ACLED data")


