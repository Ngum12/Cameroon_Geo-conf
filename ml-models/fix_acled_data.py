"""
Fix the corrupted ACLED JSON file and extract events for ML training.
"""

import json
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_events_from_corrupted_json():
    """Extract events from the corrupted JSON file."""
    logger.info("🔧 Fixing corrupted ACLED JSON file...")
    
    input_path = "../acled-processor/cameroon_conflict_data_processed.json"
    output_path = "cameroon_events_fixed.json"
    
    events = []
    current_event = {}
    in_events_section = False
    brace_count = 0
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Look for the events section start
                if '"events": [' in line:
                    in_events_section = True
                    logger.info(f"📍 Found events section at line {line_num}")
                    continue
                
                if not in_events_section:
                    continue
                
                # Parse individual events
                if line == '{':
                    current_event = {}
                    brace_count = 1
                elif line.startswith('}'):
                    if brace_count == 1:
                        # End of current event
                        if current_event:
                            events.append(current_event.copy())
                            if len(events) % 100 == 0:
                                logger.info(f"   Processed {len(events)} events...")
                        current_event = {}
                        brace_count = 0
                elif current_event is not None and ':' in line:
                    # Parse key-value pairs
                    try:
                        # Clean the line and try to parse as JSON
                        clean_line = line.rstrip(',')
                        if clean_line.startswith('"') and '":' in clean_line:
                            # Split key and value
                            key_part, value_part = clean_line.split('": ', 1)
                            key = key_part.strip('"')
                            
                            # Parse value
                            if value_part.endswith(','):
                                value_part = value_part[:-1]
                            
                            try:
                                value = json.loads(value_part)
                            except:
                                # Handle string values
                                if value_part.startswith('"') and value_part.endswith('"'):
                                    value = value_part[1:-1]  # Remove quotes
                                else:
                                    value = value_part
                            
                            current_event[key] = value
                    except Exception as e:
                        # Skip problematic lines
                        continue
                
                # Stop if we encounter the end of events array or other sections
                if line.startswith(']') and in_events_section:
                    break
        
        logger.info(f"✅ Extracted {len(events)} events from corrupted file")
        
        # Create clean JSON output
        output_data = {
            "metadata": {
                "total_events": len(events),
                "source": "ACLED Cameroon 1997-2016",
                "processing_note": "Fixed from corrupted JSON file",
                "processing_timestamp": "2025-09-01T09:10:00"
            },
            "events": events
        }
        
        # Write fixed data
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"💾 Saved fixed data to: {output_path}")
        
        # Validate the fixed file
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
            logger.info(f"✅ Validation successful: {test_data['metadata']['total_events']} events")
            return True
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error fixing JSON file: {e}")
        return False

if __name__ == "__main__":
    success = extract_events_from_corrupted_json()
    if success:
        print("🎯 ACLED data fix completed successfully!")
    else:
        print("❌ Failed to fix ACLED data")
        sys.exit(1)

