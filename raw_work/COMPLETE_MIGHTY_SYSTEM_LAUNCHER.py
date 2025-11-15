#!/usr/bin/env python3
"""
🛡️ COMPLETE MIGHTY SYSTEM LAUNCHER - ALL 7 SERVICES
Project Sentinel - Harmony Flow Platform

COMPLETE RESTORATION OF YOUR ORIGINAL MIGHTY SYSTEM
✅ Django Backend API (Port 8000)
✅ ML Prediction API (Port 8001)
✅ RL Intervention API (Port 8002)
✅ Human Interface API (Port 8003)
✅ NLP Translation Service (Port 8004)
✅ NLP NER Service (Port 8005)
✅ React Frontend Dashboard (Port 5173)

USAGE: python COMPLETE_MIGHTY_SYSTEM_LAUNCHER.py
"""

import os
import sys
import subprocess
import time
import threading
import signal
from datetime import datetime
import requests
import json

class CompleteMightySystemLauncher:
    """Complete restoration of your original mighty system"""
    
    def __init__(self):
        self.processes = {}
        self.running = False
        self.start_time = None
        
        # All 7 services from your original system
        self.services = [
            {
                'name': 'Django Backend',
                'dir': 'backend-api',
                'command': ['python', 'manage.py', 'runserver', '8000', '--settings=sentinel_core.minimal_settings'],
                'port': 8000,
                'health_url': 'http://localhost:8000/api/v1/statistics/',
                'priority': 1
            },
            {
                'name': 'ML Prediction API',
                'dir': 'ml-models',
                'command': ['python', '-m', 'uvicorn', 'prediction_api:app', '--host', '0.0.0.0', '--port', '8001', '--reload'],
                'port': 8001,
                'health_url': 'http://localhost:8001/docs',
                'priority': 2
            },
            {
                'name': 'RL Intervention API',
                'dir': 'rl-system',
                'command': ['python', '-m', 'uvicorn', 'rl_system_api:app', '--host', '0.0.0.0', '--port', '8002', '--reload'],
                'port': 8002,
                'health_url': 'http://localhost:8002/docs',
                'priority': 3
            },
            {
                'name': 'Human Interface API',
                'dir': 'human-in-loop',
                'command': ['python', '-m', 'uvicorn', 'human_interface_api:app', '--host', '0.0.0.0', '--port', '8003', '--reload'],
                'port': 8003,
                'health_url': 'http://localhost:8003/docs',
                'priority': 4
            },
            {
                'name': 'NLP Translation Service',
                'dir': 'nlp-models',
                'command': ['python', '-m', 'uvicorn', 'translation_service_cpu:app', '--host', '0.0.0.0', '--port', '8004', '--reload'],
                'port': 8004,
                'health_url': 'http://localhost:8004/docs',
                'priority': 5
            },
            {
                'name': 'NLP NER Service',
                'dir': 'nlp-models',
                'command': ['python', '-m', 'uvicorn', 'ner_service:app', '--host', '0.0.0.0', '--port', '8005', '--reload'],
                'port': 8005,
                'health_url': 'http://localhost:8005/docs',
                'priority': 6
            },
            {
                'name': 'Frontend Dashboard',
                'dir': 'frontend-dashboard',
                'command': ['npm', 'run', 'dev'],
                'port': 5173,
                'health_url': 'http://localhost:5173',
                'priority': 7
            }
        ]
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n📡 Received signal {signum}, shutting down all services...")
        self.shutdown_system()
        sys.exit(0)
    
    def print_banner(self):
        """Print complete system banner"""
        print("\n" + "="*90)
        print("🛡️ PROJECT SENTINEL - COMPLETE MIGHTY SYSTEM LAUNCHER")
        print("="*90)
        print("🎯 CAMEROON DEFENSE FORCE - HARMONY FLOW PLATFORM")
        print("📡 ALL 7 ORIGINAL SERVICES RESTORED")
        print("🚀 COMPLETE MICROSERVICES ARCHITECTURE")
        print("🤖 ML + RL + NLP + HUMAN-IN-LOOP + FRONTEND")
        print("="*90)
        print("🔧 SERVICES TO START:")
        for service in self.services:
            print(f"   {service['priority']}. {service['name']} (Port {service['port']})")
        print("="*90)
        print("🚀 STARTING ALL SERVICES...")
        print("="*90)
    
    def start_service(self, service):
        """Start a single service"""
        print(f"🔧 Starting {service['name']} on port {service['port']}...")
        
        try:
            # Check if directory exists
            if not os.path.exists(service['dir']):
                print(f"❌ Directory not found: {service['dir']}")
                return False
            
            # Start the service
            process = subprocess.Popen(
                service['command'],
                cwd=service['dir'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[service['name']] = {
                'process': process,
                'service': service,
                'start_time': datetime.now()
            }
            
            print(f"✅ {service['name']} started (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start {service['name']}: {e}")
            return False
    
    def check_service_health(self, service):
        """Check if service is healthy"""
        try:
            response = requests.get(service['health_url'], timeout=3)
            return response.status_code in [200, 404]  # 404 is OK for some endpoints
        except:
            return False
    
    def wait_for_service(self, service, timeout=30):
        """Wait for service to become healthy"""
        print(f"⏳ Waiting for {service['name']} to become ready...")
        
        for i in range(timeout):
            if self.check_service_health(service):
                print(f"✅ {service['name']} is ready!")
                return True
            time.sleep(1)
            if i % 5 == 0 and i > 0:
                print(f"   Still waiting for {service['name']}... ({i}/{timeout}s)")
        
        print(f"⚠️ {service['name']} may not be fully ready")
        return False
    
    def start_all_services(self):
        """Start all services in order"""
        successful_starts = 0
        
        for service in self.services:
            if self.start_service(service):
                successful_starts += 1
                
                # Wait between services
                time.sleep(3)
                
                # Wait for critical services to be ready
                if service['priority'] <= 3:  # Django, ML, RL
                    self.wait_for_service(service, timeout=20)
        
        return successful_starts
    
    def show_system_status(self):
        """Show comprehensive system status"""
        uptime = (datetime.now() - self.start_time).total_seconds() / 60 if self.start_time else 0
        
        print("\n" + "="*85)
        print("🎯 PROJECT SENTINEL - COMPLETE SYSTEM STATUS")
        print("="*85)
        print(f"⏱️ System Uptime: {uptime:.1f} minutes")
        print(f"🔧 Total Services: {len(self.services)}")
        
        running_count = 0
        healthy_count = 0
        
        print(f"\n📊 SERVICE STATUS:")
        for service in self.services:
            service_name = service['name']
            
            if service_name in self.processes:
                process_info = self.processes[service_name]
                process = process_info['process']
                
                # Check if process is running
                is_running = process.poll() is None
                is_healthy = self.check_service_health(service) if is_running else False
                
                if is_running:
                    running_count += 1
                if is_healthy:
                    healthy_count += 1
                
                status_icon = "🟢" if is_healthy else ("🟡" if is_running else "🔴")
                status_text = "HEALTHY" if is_healthy else ("RUNNING" if is_running else "STOPPED")
                
                print(f"   {status_icon} {service_name}: {status_text} (Port {service['port']}, PID: {process.pid})")
            else:
                print(f"   🔴 {service_name}: NOT STARTED (Port {service['port']})")
        
        print(f"\n📈 SYSTEM METRICS:")
        print(f"   🔧 Running Services: {running_count}/{len(self.services)}")
        print(f"   💚 Healthy Services: {healthy_count}/{len(self.services)}")
        print(f"   📊 Success Rate: {(healthy_count/len(self.services)*100):.1f}%")
        
        if healthy_count >= len(self.services) * 0.8:  # 80% healthy
            print(f"\n🚀 SYSTEM STATUS: FULLY OPERATIONAL")
        elif running_count >= len(self.services) * 0.6:  # 60% running
            print(f"\n⚠️ SYSTEM STATUS: PARTIALLY OPERATIONAL")
        else:
            print(f"\n🔴 SYSTEM STATUS: DEGRADED")
        
        print(f"\n🌐 SERVICE ENDPOINTS:")
        print(f"   🎯 Main Dashboard:      http://localhost:5173")
        print(f"   🔧 Django Backend:      http://localhost:8000")
        print(f"   🤖 ML Prediction API:   http://localhost:8001/docs")
        print(f"   🧠 RL Intervention API: http://localhost:8002/docs")
        print(f"   👤 Human Interface API: http://localhost:8003/docs")
        print(f"   🌍 NLP Translation:     http://localhost:8004/docs")
        print(f"   🏷️ NLP NER Service:     http://localhost:8005/docs")
        
        print("="*85)
        print("🛡️ CAMEROON DEFENSE FORCE - PROJECT SENTINEL OPERATIONAL!")
        print("="*85)
    
    def monitor_services(self):
        """Monitor all services continuously"""
        while self.running:
            time.sleep(60)  # Check every minute
            
            # Check for crashed services
            crashed_services = []
            for service_name, process_info in self.processes.items():
                if process_info['process'].poll() is not None:
                    crashed_services.append(service_name)
            
            if crashed_services:
                print(f"⚠️ Detected crashed services: {', '.join(crashed_services)}")
            
            # Show status every 5 minutes
            if int(time.time()) % 300 == 0:  # Every 5 minutes
                self.show_system_status()
    
    def launch_complete_system(self):
        """Launch the complete mighty system"""
        self.print_banner()
        
        self.running = True
        self.start_time = datetime.now()
        
        # Start all services
        successful_starts = self.start_all_services()
        
        print(f"\n🎯 SERVICE STARTUP COMPLETE!")
        print(f"✅ Successfully started: {successful_starts}/{len(self.services)} services")
        
        # Wait for services to stabilize
        print(f"\n⏳ Allowing services to stabilize...")
        time.sleep(10)
        
        # Show initial status
        self.show_system_status()
        
        # Start monitoring
        monitor_thread = threading.Thread(target=self.monitor_services, daemon=True)
        monitor_thread.start()
        
        print(f"\n🎯 COMPLETE MIGHTY SYSTEM LAUNCH FINISHED!")
        print(f"📊 System monitoring active")
        print(f"🔄 Press Ctrl+C to shutdown all services gracefully")
        
        # Main loop
        try:
            while self.running:
                time.sleep(300)  # Show status every 5 minutes
                
        except KeyboardInterrupt:
            print(f"\n🛑 Graceful shutdown initiated...")
            self.shutdown_system()
        
        return True
    
    def shutdown_system(self):
        """Gracefully shutdown all services"""
        print(f"\n🛑 SHUTTING DOWN ALL PROJECT SENTINEL SERVICES...")
        
        self.running = False
        
        # Stop all services
        for service_name, process_info in self.processes.items():
            process = process_info['process']
            
            if process.poll() is None:
                print(f"🛑 Stopping {service_name}...")
                try:
                    process.terminate()
                    process.wait(timeout=10)
                    print(f"✅ {service_name} stopped")
                except subprocess.TimeoutExpired:
                    print(f"⚠️ Force killing {service_name}...")
                    process.kill()
                except Exception as e:
                    print(f"❌ Error stopping {service_name}: {e}")
        
        # Final status
        uptime = (datetime.now() - self.start_time).total_seconds() / 60 if self.start_time else 0
        
        print(f"\n📊 FINAL SYSTEM STATISTICS:")
        print(f"Total uptime: {uptime:.1f} minutes")
        print(f"Services managed: {len(self.services)}")
        print(f"🛡️ PROJECT SENTINEL - COMPLETE SHUTDOWN")
        print(f"🎯 CAMEROON DEFENSE FORCE - SYSTEM OFFLINE")

def main():
    """Main launcher function"""
    launcher = CompleteMightySystemLauncher()
    
    try:
        success = launcher.launch_complete_system()
        if success:
            print("✅ Complete mighty system launched successfully")
        else:
            print("❌ System launch encountered issues")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Critical error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
