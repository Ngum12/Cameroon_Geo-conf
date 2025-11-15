#!/usr/bin/env python3
"""
🚀 LAUNCH ULTIMATE SYSTEM - ONE-CLICK DEPLOYMENT
Project Sentinel - Harmony Flow Platform

DEFENSE-READY COMPLETE SYSTEM LAUNCHER
✅ Launches entire data pipeline with one command
✅ Starts all components in correct order
✅ Monitors system health
✅ Provides real-time status dashboard
✅ Handles graceful shutdown
✅ Perfect for academic defense demonstration

USAGE: python LAUNCH_ULTIMATE_SYSTEM.py

CLASSIFICATION: DEFENSE-READY DEPLOYMENT SYSTEM
"""

import os
import sys
import subprocess
import threading
import time
import signal
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import requests
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ultimate_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UltimateSystemLauncher:
    """Ultimate system launcher for complete Harmony Flow Platform"""
    
    def __init__(self):
        self.processes = {}
        self.running = False
        self.start_time = None
        self.system_status = {
            'backend_running': False,
            'frontend_running': False,
            'pipeline_running': False,
            'database_connected': False
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # System configuration
        self.config = {
            'backend_port': 8000,
            'frontend_port': 3000,
            'backend_dir': 'backend-api',
            'frontend_dir': 'frontend-dashboard',
            'wait_time_between_starts': 5,
            'health_check_interval': 30,
            'max_startup_wait': 120
        }
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n📡 Received signal {signum}, shutting down system...")
        self.shutdown_system()
        sys.exit(0)
    
    def print_banner(self):
        """Print impressive system banner"""
        print("\n" + "="*80)
        print("🎯 HARMONY FLOW PLATFORM - ULTIMATE SYSTEM LAUNCHER")
        print("="*80)
        print("🛡️ CAMEROON DEFENSE INTELLIGENCE SYSTEM")
        print("📡 Real-time Data Collection & Analysis")
        print("🤖 Advanced ML Threat Assessment")
        print("🚨 Automated Alert System")
        print("🖥️ Interactive Dashboard")
        print("📋 Comprehensive Evidence Logging")
        print("="*80)
        print("🚀 LAUNCHING COMPLETE SYSTEM...")
        print("="*80)
    
    def check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        print("🔍 CHECKING SYSTEM PREREQUISITES...")
        
        prerequisites_ok = True
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("❌ Python 3.8+ required")
            prerequisites_ok = False
        else:
            print(f"✅ Python {python_version.major}.{python_version.minor}")
        
        # Check required directories
        required_dirs = [self.config['backend_dir'], self.config['frontend_dir']]
        for dir_name in required_dirs:
            if os.path.exists(dir_name):
                print(f"✅ Directory: {dir_name}")
            else:
                print(f"❌ Missing directory: {dir_name}")
                prerequisites_ok = False
        
        # Check key files
        key_files = [
            f"{self.config['backend_dir']}/manage.py",
            f"{self.config['frontend_dir']}/package.json",
            "MASTER_PIPELINE_CONTROLLER.py"
        ]
        
        for file_path in key_files:
            if os.path.exists(file_path):
                print(f"✅ File: {file_path}")
            else:
                print(f"❌ Missing file: {file_path}")
                prerequisites_ok = False
        
        # Check ports availability
        for port in [self.config['backend_port'], self.config['frontend_port']]:
            if self.is_port_available(port):
                print(f"✅ Port {port} available")
            else:
                print(f"⚠️ Port {port} in use (will attempt to use anyway)")
        
        return prerequisites_ok
    
    def is_port_available(self, port: int) -> bool:
        """Check if port is available"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def start_backend(self) -> bool:
        """Start Django backend server"""
        print("🔧 STARTING BACKEND SERVER...")
        
        try:
            backend_dir = self.config['backend_dir']
            
            # Change to backend directory
            original_dir = os.getcwd()
            os.chdir(backend_dir)
            
            # Start Django server
            cmd = [
                sys.executable, 'manage.py', 'runserver',
                f"{self.config['backend_port']}",
                '--settings=sentinel_core.minimal_settings',
                '--noreload'
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes['backend'] = process
            
            # Return to original directory
            os.chdir(original_dir)
            
            # Wait for backend to start
            if self.wait_for_backend():
                print("✅ Backend server started successfully")
                self.system_status['backend_running'] = True
                return True
            else:
                print("❌ Backend server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Backend startup error: {e}")
            return False
    
    def wait_for_backend(self) -> bool:
        """Wait for backend to be ready"""
        backend_url = f"http://localhost:{self.config['backend_port']}/api/v1/statistics/"
        
        for attempt in range(self.config['max_startup_wait'] // 2):
            try:
                response = requests.get(backend_url, timeout=2)
                if response.status_code == 200:
                    self.system_status['database_connected'] = True
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
            print(f"⏳ Waiting for backend... ({attempt + 1}/{self.config['max_startup_wait'] // 2})")
        
        return False
    
    def start_frontend(self) -> bool:
        """Start React frontend development server"""
        print("🖥️ STARTING FRONTEND SERVER...")
        
        try:
            frontend_dir = self.config['frontend_dir']
            
            # Check if node_modules exists
            node_modules_path = os.path.join(frontend_dir, 'node_modules')
            if not os.path.exists(node_modules_path):
                print("📦 Installing frontend dependencies...")
                self.install_frontend_dependencies()
            
            # Change to frontend directory
            original_dir = os.getcwd()
            os.chdir(frontend_dir)
            
            # Start development server
            cmd = ['npm', 'start']
            
            # Set environment variables
            env = os.environ.copy()
            env['PORT'] = str(self.config['frontend_port'])
            env['BROWSER'] = 'none'  # Don't auto-open browser
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            self.processes['frontend'] = process
            
            # Return to original directory
            os.chdir(original_dir)
            
            # Wait for frontend to start
            if self.wait_for_frontend():
                print("✅ Frontend server started successfully")
                self.system_status['frontend_running'] = True
                return True
            else:
                print("❌ Frontend server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Frontend startup error: {e}")
            return False
    
    def install_frontend_dependencies(self) -> bool:
        """Install frontend dependencies"""
        try:
            result = subprocess.run(['npm', 'install'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ Frontend dependencies installed")
                return True
            else:
                print(f"❌ Dependency installation failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Dependency installation error: {e}")
            return False
    
    def wait_for_frontend(self) -> bool:
        """Wait for frontend to be ready"""
        frontend_url = f"http://localhost:{self.config['frontend_port']}"
        
        for attempt in range(self.config['max_startup_wait'] // 3):
            try:
                response = requests.get(frontend_url, timeout=2)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(3)
            print(f"⏳ Waiting for frontend... ({attempt + 1}/{self.config['max_startup_wait'] // 3})")
        
        return False
    
    def start_pipeline(self) -> bool:
        """Start the master data pipeline"""
        print("📡 STARTING MASTER DATA PIPELINE...")
        
        try:
            # Start pipeline in separate process
            cmd = [sys.executable, 'MASTER_PIPELINE_CONTROLLER.py']
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes['pipeline'] = process
            
            # Give pipeline time to initialize
            time.sleep(10)
            
            # Check if pipeline is still running
            if process.poll() is None:
                print("✅ Master pipeline started successfully")
                self.system_status['pipeline_running'] = True
                return True
            else:
                print("❌ Master pipeline failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Pipeline startup error: {e}")
            return False
    
    def monitor_system_health(self):
        """Monitor system health in background thread"""
        while self.running:
            try:
                # Check process health
                for name, process in self.processes.items():
                    if process and process.poll() is not None:
                        print(f"⚠️ {name.title()} process has stopped")
                        self.system_status[f'{name}_running'] = False
                
                # Check service endpoints
                self.check_service_health()
                
                time.sleep(self.config['health_check_interval'])
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                time.sleep(30)
    
    def check_service_health(self):
        """Check health of all services"""
        # Check backend
        try:
            response = requests.get(f"http://localhost:{self.config['backend_port']}/api/v1/statistics/", timeout=5)
            self.system_status['backend_running'] = response.status_code == 200
        except:
            self.system_status['backend_running'] = False
        
        # Check frontend
        try:
            response = requests.get(f"http://localhost:{self.config['frontend_port']}", timeout=5)
            self.system_status['frontend_running'] = response.status_code == 200
        except:
            self.system_status['frontend_running'] = False
    
    def print_system_status(self):
        """Print current system status"""
        uptime = (datetime.now() - self.start_time).total_seconds() / 60 if self.start_time else 0
        
        print("\n" + "="*60)
        print("🎯 HARMONY FLOW PLATFORM - SYSTEM STATUS")
        print("="*60)
        print(f"⏱️ Uptime: {uptime:.1f} minutes")
        print(f"🔧 Backend: {'🟢 RUNNING' if self.system_status['backend_running'] else '🔴 STOPPED'}")
        print(f"🖥️ Frontend: {'🟢 RUNNING' if self.system_status['frontend_running'] else '🔴 STOPPED'}")
        print(f"📡 Pipeline: {'🟢 RUNNING' if self.system_status['pipeline_running'] else '🔴 STOPPED'}")
        print(f"🗄️ Database: {'🟢 CONNECTED' if self.system_status['database_connected'] else '🔴 DISCONNECTED'}")
        print("="*60)
        
        if all(self.system_status.values()):
            print("🚀 SYSTEM STATUS: FULLY OPERATIONAL")
            print(f"🌐 Frontend: http://localhost:{self.config['frontend_port']}")
            print(f"🔧 Backend API: http://localhost:{self.config['backend_port']}/api/v1/")
        else:
            print("⚠️ SYSTEM STATUS: PARTIAL OPERATION")
        
        print("="*60)
    
    def launch_system(self):
        """Launch the complete system"""
        self.print_banner()
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites check failed. Please fix issues and try again.")
            return False
        
        print("✅ Prerequisites check passed")
        
        self.running = True
        self.start_time = datetime.now()
        
        # Start components in order
        print("\n🚀 STARTING SYSTEM COMPONENTS...")
        
        # 1. Start backend
        if not self.start_backend():
            print("❌ Failed to start backend. Aborting.")
            return False
        
        time.sleep(self.config['wait_time_between_starts'])
        
        # 2. Start frontend
        if not self.start_frontend():
            print("❌ Failed to start frontend. Continuing with backend only.")
        
        time.sleep(self.config['wait_time_between_starts'])
        
        # 3. Start pipeline
        if not self.start_pipeline():
            print("❌ Failed to start pipeline. Continuing with web services only.")
        
        # Start health monitoring
        health_thread = threading.Thread(target=self.monitor_system_health, daemon=True)
        health_thread.start()
        
        # Print initial status
        time.sleep(5)
        self.print_system_status()
        
        print("\n🎯 SYSTEM LAUNCH COMPLETE!")
        print("📊 Real-time dashboard available")
        print("🔄 Press Ctrl+C to shutdown gracefully")
        
        # Main monitoring loop
        try:
            while self.running:
                time.sleep(60)  # Print status every minute
                self.print_system_status()
                
        except KeyboardInterrupt:
            print("\n🛑 Graceful shutdown initiated...")
            self.shutdown_system()
        
        return True
    
    def shutdown_system(self):
        """Gracefully shutdown all system components"""
        print("\n🛑 SHUTTING DOWN HARMONY FLOW PLATFORM...")
        
        self.running = False
        
        # Stop all processes
        for name, process in self.processes.items():
            if process and process.poll() is None:
                print(f"🛑 Stopping {name}...")
                try:
                    process.terminate()
                    process.wait(timeout=10)
                    print(f"✅ {name.title()} stopped")
                except subprocess.TimeoutExpired:
                    print(f"⚠️ Force killing {name}...")
                    process.kill()
                except Exception as e:
                    print(f"❌ Error stopping {name}: {e}")
        
        # Final status
        uptime = (datetime.now() - self.start_time).total_seconds() / 60 if self.start_time else 0
        
        print("\n📊 FINAL SYSTEM STATISTICS:")
        print(f"Total uptime: {uptime:.1f} minutes")
        print("🛡️ HARMONY FLOW PLATFORM - SHUTDOWN COMPLETE")
        print("📋 All logs preserved for analysis")

def main():
    """Main launcher function"""
    launcher = UltimateSystemLauncher()
    
    try:
        success = launcher.launch_system()
        if success:
            print("✅ System launched successfully")
        else:
            print("❌ System launch failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Critical error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
