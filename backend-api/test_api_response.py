#!/usr/bin/env python3
"""Test if API returns live data"""
import requests
import json

try:
    print("🔍 TESTING LIVE API RESPONSE...")
    
    response = requests.get('http://localhost:8000/api/v1/statistics/', timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        
        print("✅ API Response Success!")
        print("\n📊 LIVE STATISTICS:")
        
        overview = data.get('overview', {})
        print(f"   Total Articles: {overview.get('total_articles', 'Unknown')}")
        print(f"   Processed: {overview.get('processed_articles', 'Unknown')}")
        print(f"   Pending: {overview.get('pending_articles', 'Unknown')}")
        print(f"   Recent (24h): {overview.get('recent_articles_24h', 'Unknown')}")
        
        # Show sources
        sources = data.get('by_source', [])[:5]
        if sources:
            print("\n📰 TOP SOURCES:")
            for source in sources:
                print(f"   - {source.get('source', 'Unknown')}: {source.get('count', 0)} articles")
        
        # Check if we have fresh data
        recent_count = overview.get('recent_articles_24h', 0)
        if recent_count > 0:
            print(f"\n🎉 SUCCESS: API shows {recent_count} fresh articles!")
            print("✅ Your frontend should now update with REAL data!")
        else:
            print(f"\n⚠️  API still shows 0 recent articles")
    else:
        print(f"❌ API Error: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error testing API: {e}")
    print("\nℹ️  Make sure Django server is running on port 8000")
