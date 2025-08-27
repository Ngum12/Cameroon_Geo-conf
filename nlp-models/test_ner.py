#!/usr/bin/env python3
"""
Test script for Project Sentinel NER Service
Demonstrates usage of the FastAPI Named Entity Recognition endpoint
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any, List

# Test data - typical Cameroonian OSINT content (in English)
NER_TEST_CASES = [
    {
        "description": "Presidential announcement",
        "text": "President Paul Biya of Cameroon announced new security measures for the North-West and South-West regions during a meeting in Yaoundé.",
        "expected_entities": ["Paul Biya", "Cameroon", "North-West", "South-West", "Yaoundé"]
    },
    {
        "description": "Military operations",
        "text": "The Cameroon Armed Forces conducted operations in Bamenda and Buea in collaboration with UN peacekeeping forces.",
        "expected_entities": ["Cameroon Armed Forces", "Bamenda", "Buea", "UN"]
    },
    {
        "description": "International relations",
        "text": "Ambassador John Smith from the United States Embassy met with Foreign Minister Lejeune Mbella Mbella in the capital.",
        "expected_entities": ["John Smith", "United States Embassy", "Lejeune Mbella Mbella"]
    },
    {
        "description": "Economic news",
        "text": "The Central Bank of Central African States reported increased investment from France and China in Douala's port infrastructure.",
        "expected_entities": ["Central Bank of Central African States", "France", "China", "Douala"]
    },
    {
        "description": "Security incident",
        "text": "Local reports indicate that Boko Haram militants attacked villages near Maroua, prompting response from the Rapid Intervention Battalion.",
        "expected_entities": ["Boko Haram", "Maroua", "Rapid Intervention Battalion"]
    },
    {
        "description": "Government officials",
        "text": "Minister Ferdinand Ngoh Ngoh and Prime Minister Joseph Dion Ngute attended the African Union summit in Addis Ababa, Ethiopia.",
        "expected_entities": ["Ferdinand Ngoh Ngoh", "Joseph Dion Ngute", "African Union", "Addis Ababa", "Ethiopia"]
    }
]

BASE_URL = "http://localhost:8002"

def print_entities_formatted(entities: List[Dict], title: str = "Detected Entities"):
    """Print entities in a formatted table."""
    print(f"\n📋 {title}:")
    print("-" * 80)
    print(f"{'Entity':<25} {'Type':<15} {'Confidence':<12} {'Position':<10}")
    print("-" * 80)
    
    for entity in entities:
        position = f"{entity['start']}-{entity['end']}"
        print(f"{entity['word']:<25} {entity['entity_group']:<15} {entity['confidence']:<12.4f} {position:<10}")
    
    if not entities:
        print("No entities detected.")
    
    print("-" * 80)

async def test_ner_endpoint(client: httpx.AsyncClient, test_case: Dict[str, Any]):
    """Test a single NER analysis request."""
    print(f"\n🔍 Testing: {test_case['description']}")
    print(f"📝 Text: {test_case['text']}")
    
    start_time = time.time()
    
    try:
        response = await client.post(
            f"{BASE_URL}/analyze-entities",
            json={"text": test_case["text"]},
            timeout=60.0  # Longer timeout for NER processing
        )
        
        request_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            entities = data['entities']
            
            print(f"✅ Success ({request_time:.2f}s)")
            print(f"   Processing Time: {data.get('processing_time', 'N/A'):.3f}s")
            print(f"   Entities Found: {data.get('entity_count', 0)}")
            
            # Display entities
            print_entities_formatted(entities, "Detected Entities")
            
            # Check if expected entities were found (basic validation)
            expected = test_case.get('expected_entities', [])
            found_words = [entity['word'] for entity in entities]
            
            if expected:
                found_expected = []
                missing_expected = []
                
                for exp in expected:
                    found = any(exp.lower() in word.lower() or word.lower() in exp.lower() 
                             for word in found_words)
                    if found:
                        found_expected.append(exp)
                    else:
                        missing_expected.append(exp)
                
                print(f"\n📊 Expected Entity Analysis:")
                print(f"   Found: {found_expected}")
                print(f"   Missing: {missing_expected}")
                print(f"   Coverage: {len(found_expected)}/{len(expected)} ({len(found_expected)/len(expected)*100:.1f}%)")
            
            # Group entities by type
            entity_groups = {}
            for entity in entities:
                group = entity['entity_group']
                if group not in entity_groups:
                    entity_groups[group] = []
                entity_groups[group].append(entity['word'])
            
            print(f"\n🏷️ Entities by Type:")
            for group, words in entity_groups.items():
                print(f"   {group}: {', '.join(words)}")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

async def test_health_endpoint(client: httpx.AsyncClient):
    """Test the health check endpoint."""
    print("\n🔍 Testing NER health endpoint...")
    
    try:
        response = await client.get(f"{BASE_URL}/health", timeout=10.0)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data['status']}")
            print(f"   Model Loaded: {data['model_loaded']}")
            if data.get('model_info'):
                model_info = data['model_info']
                print(f"   Model: {model_info.get('model_name', 'N/A')}")
                print(f"   Device: {model_info.get('device', 'N/A')}")
                print(f"   Supported Entities: {model_info.get('supported_entities', [])}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check exception: {str(e)}")
        return False

async def test_entity_types_endpoint(client: httpx.AsyncClient):
    """Test the entity types endpoint."""
    print("\n🏷️ Testing entity-types endpoint...")
    
    try:
        response = await client.get(f"{BASE_URL}/entity-types", timeout=10.0)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Entity types endpoint working")
            print(f"   Supported Entities: {data.get('supported_entities', [])}")
            
            descriptions = data.get('entity_descriptions', {})
            print(f"\n📖 Entity Descriptions:")
            for entity_type, description in descriptions.items():
                print(f"   {entity_type}: {description}")
            
            return True
        else:
            print(f"❌ Entity types endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Entity types endpoint exception: {str(e)}")
        return False

async def test_grouped_analysis(client: httpx.AsyncClient):
    """Test the grouped analysis endpoint."""
    print("\n📊 Testing grouped analysis endpoint...")
    
    test_text = "President Paul Biya of Cameroon met with UN Secretary-General António Guterres in New York to discuss peace initiatives in the Central African Republic."
    
    try:
        response = await client.post(
            f"{BASE_URL}/analyze-entities/grouped",
            json={"text": test_text},
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Grouped analysis working")
            
            grouped = data.get('grouped_entities', {})
            stats = data.get('entity_statistics', {})
            
            print(f"   Total Entities: {data.get('total_entities', 0)}")
            print(f"   Entity Statistics: {stats}")
            
            for entity_type, entities in grouped.items():
                print(f"\n   {entity_type} entities:")
                for entity in entities:
                    print(f"     - {entity['word']} (confidence: {entity['confidence']:.3f})")
            
            return True
        else:
            print(f"❌ Grouped analysis failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Grouped analysis exception: {str(e)}")
        return False

async def test_high_confidence_analysis(client: httpx.AsyncClient):
    """Test the high-confidence analysis endpoint."""
    print("\n🎯 Testing high-confidence analysis endpoint...")
    
    test_text = "The Cameroon Armed Forces and Boko Haram clashed near Maroua while UN forces monitored the situation."
    
    try:
        response = await client.post(
            f"{BASE_URL}/analyze-entities/high-confidence?min_confidence=0.9",
            json={"text": test_text},
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ High-confidence analysis working")
            print(f"   High-confidence entities: {data.get('entity_count', 0)}")
            print(f"   Total entities found: {data.get('total_entities_found', 0)}")
            print(f"   Confidence threshold: {data.get('confidence_threshold', 0)}")
            
            entities = data.get('entities', [])
            if entities:
                print_entities_formatted(entities, "High-Confidence Entities")
            
            return True
        else:
            print(f"❌ High-confidence analysis failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ High-confidence analysis exception: {str(e)}")
        return False

async def wait_for_ner_service(max_wait: int = 180):
    """Wait for the NER service to be ready (NER models take longer to load)."""
    print(f"⏳ Waiting for NER service to start (max {max_wait}s)...")
    print("   Note: XLM-RoBERTa model is large (~2GB) and may take 60-180s to load")
    
    async with httpx.AsyncClient() as client:
        for i in range(max_wait):
            try:
                response = await client.get(f"{BASE_URL}/health", timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('model_loaded'):
                        print("✅ NER service is ready!")
                        return True
            except:
                pass
            
            await asyncio.sleep(1)
            if i % 30 == 0 and i > 0:
                print(f"   Still waiting... ({i}s elapsed)")
    
    print("❌ NER service did not start in time")
    return False

async def run_ner_tests():
    """Run all tests for the NER service."""
    print("🚀 Starting Project Sentinel NER Service Tests")
    print("=" * 80)
    
    # Wait for service to be ready
    if not await wait_for_ner_service():
        return
    
    async with httpx.AsyncClient() as client:
        # Test health endpoint
        health_ok = await test_health_endpoint(client)
        if not health_ok:
            print("❌ Health check failed, aborting tests")
            return
        
        # Test entity types endpoint
        await test_entity_types_endpoint(client)
        
        # Test grouped analysis
        await test_grouped_analysis(client)
        
        # Test high-confidence analysis
        await test_high_confidence_analysis(client)
        
        # Test main NER endpoint with various inputs
        print("\n📚 Testing Main NER Endpoint")
        print("=" * 80)
        
        success_count = 0
        total_tests = len(NER_TEST_CASES)
        
        for i, test_case in enumerate(NER_TEST_CASES, 1):
            print(f"\n🧪 Test {i}/{total_tests}:")
            success = await test_ner_endpoint(client, test_case)
            if success:
                success_count += 1
        
        # Summary
        print("\n" + "=" * 80)
        print(f"📊 Test Summary: {success_count}/{total_tests} tests passed")
        
        if success_count == total_tests:
            print("🎉 All tests passed! NER service is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the service logs for details.")

def main():
    """Main entry point."""
    print("Project Sentinel NER Service - Test Suite")
    print("Cameroon Defense Force OSINT Analysis System")
    print()
    
    try:
        asyncio.run(run_ner_tests())
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")

if __name__ == "__main__":
    main()
