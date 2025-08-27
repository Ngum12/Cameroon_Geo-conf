#!/usr/bin/env python3
"""
Test script for Project Sentinel Translation Service
Demonstrates usage of the FastAPI translation endpoint
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

# Test data - typical Cameroonian news content
TEST_CASES = [
    {
        "text": "Le président de la République du Cameroun a annoncé de nouvelles mesures de sécurité.",
        "source_lang": "auto",
        "expected_lang": "fr"
    },
    {
        "text": "The security situation in the North-West region requires immediate attention.",
        "source_lang": "auto", 
        "expected_lang": "en"
    },
    {
        "text": "Les forces armées camerounaises ont renforcé leur présence dans la région de l'Extrême-Nord.",
        "source_lang": "fr",
        "expected_lang": "fr"
    },
    {
        "text": "Yaoundé accueillera le sommet sur la sécurité régionale la semaine prochaine.",
        "source_lang": "auto",
        "expected_lang": "fr"
    },
    {
        "text": "Intelligence reports indicate increased activity along the border.",
        "source_lang": "en",
        "expected_lang": "en"
    }
]

BASE_URL = "http://localhost:8001"

async def test_translation_endpoint(client: httpx.AsyncClient, test_case: Dict[str, Any]):
    """Test a single translation request."""
    print(f"\n📝 Testing: {test_case['text'][:50]}...")
    print(f"   Source Language: {test_case['source_lang']}")
    
    start_time = time.time()
    
    try:
        response = await client.post(
            f"{BASE_URL}/translate",
            json={
                "text": test_case["text"],
                "source_lang": test_case["source_lang"]
            },
            timeout=30.0
        )
        
        request_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success ({request_time:.2f}s)")
            print(f"   Translated: {data['translated_text']}")
            print(f"   Detected Language: {data.get('detected_language', 'N/A')}")
            print(f"   Processing Time: {data.get('processing_time', 'N/A'):.3f}s")
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
    print("\n🔍 Testing health endpoint...")
    
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
                print(f"   Languages: {len(model_info.get('supported_languages', []))}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check exception: {str(e)}")
        return False

async def test_languages_endpoint(client: httpx.AsyncClient):
    """Test the languages endpoint."""
    print("\n🌍 Testing languages endpoint...")
    
    try:
        response = await client.get(f"{BASE_URL}/languages", timeout=10.0)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Languages endpoint working")
            print(f"   Total Languages: {data.get('total_count', 0)}")
            print(f"   Primary Languages: {data.get('primary_languages', [])}")
            return True
        else:
            print(f"❌ Languages endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Languages endpoint exception: {str(e)}")
        return False

async def wait_for_service(max_wait: int = 60):
    """Wait for the translation service to be ready."""
    print(f"⏳ Waiting for translation service to start (max {max_wait}s)...")
    
    async with httpx.AsyncClient() as client:
        for i in range(max_wait):
            try:
                response = await client.get(f"{BASE_URL}/health", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('model_loaded'):
                        print("✅ Translation service is ready!")
                        return True
            except:
                pass
            
            await asyncio.sleep(1)
            if i % 10 == 0:
                print(f"   Still waiting... ({i}s)")
    
    print("❌ Service did not start in time")
    return False

async def run_tests():
    """Run all tests for the translation service."""
    print("🚀 Starting Project Sentinel Translation Service Tests")
    print("=" * 60)
    
    # Wait for service to be ready
    if not await wait_for_service():
        return
    
    async with httpx.AsyncClient() as client:
        # Test health endpoint
        health_ok = await test_health_endpoint(client)
        if not health_ok:
            print("❌ Health check failed, aborting tests")
            return
        
        # Test languages endpoint
        await test_languages_endpoint(client)
        
        # Test translation endpoint with various inputs
        print("\n📚 Testing Translation Endpoint")
        print("-" * 40)
        
        success_count = 0
        total_tests = len(TEST_CASES)
        
        for i, test_case in enumerate(TEST_CASES, 1):
            print(f"\nTest {i}/{total_tests}:")
            success = await test_translation_endpoint(client, test_case)
            if success:
                success_count += 1
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {success_count}/{total_tests} tests passed")
        
        if success_count == total_tests:
            print("🎉 All tests passed! Translation service is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the service logs for details.")

def main():
    """Main entry point."""
    print("Project Sentinel Translation Service - Test Suite")
    print("Cameroon Defense Force OSINT Analysis System")
    print()
    
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")

if __name__ == "__main__":
    main()
