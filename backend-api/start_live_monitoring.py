#!/usr/bin/env python3
"""
🚀 START LIVE MONITORING - Activate continuous intelligence collection
"""
import os
import sys
import threading
import time
from datetime import datetime

def start_continuous_monitoring():
    """Start the continuous monitoring service"""
    print("🚀 ACTIVATING PROJECT SENTINEL LIVE MONITORING")
    print("=" * 60)
    print("🌍 COMPREHENSIVE GEOPOLITICAL INTELLIGENCE")
    print("📡 45+ Sophisticated Sources")
    print("🔄 Auto-Collection: Every 30 minutes")
    print("🎯 All 10 Cameroon Regions")
    print("🛡️ Defense-Grade Intelligence")
    print("=" * 60)
    
    try:
        # Import the monitoring service
        from continuous_news_monitor import ContinuousNewsMonitor
        
        # Create and start monitor
        monitor = ContinuousNewsMonitor()
        
        print(f"✅ Monitor initialized at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🔄 Starting continuous monitoring...")
        print("📊 Press Ctrl+C to stop monitoring")
        print("-" * 60)
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor.start_monitoring, daemon=True)
        monitor_thread.start()
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n🛑 Monitoring stopped at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            monitor.stop_monitoring()
            print("✅ Project Sentinel monitoring service stopped")
            
    except ImportError as e:
        print(f"❌ Error importing monitoring service: {e}")
        print("💡 Make sure you're in the backend-api directory")
    except Exception as e:
        print(f"❌ Error starting monitoring: {e}")

if __name__ == '__main__':
    start_continuous_monitoring()
