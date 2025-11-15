#!/usr/bin/env python3
"""
PROJECT SENTINEL - SYSTEM PERFORMANCE MONITOR
Cameroon Defense Force OSINT Analysis System
Real-time monitoring of all system components
"""

import os
import sys
import time
import json
import psutil
import requests
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path
import threading
import queue
import subprocess
from alert_system import alert_system

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ServiceStatus:
    """Service health status"""
    name: str
    url: str
    status: str  # 'healthy', 'unhealthy', 'unknown'
    response_time: float
    last_check: datetime
    error_message: Optional[str] = None
    
    def to_dict(self):
        result = asdict(self)
        result['last_check'] = self.last_check.isoformat()
        return result

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    memory_available: int
    disk_usage: float
    disk_free: int
    network_sent: int
    network_received: int
    process_count: int
    load_average: Optional[List[float]] = None
    
    def to_dict(self):
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result

@dataclass
class AlertThreshold:
    """Alert threshold configuration"""
    metric_name: str
    threshold_value: float
    comparison: str  # 'greater_than', 'less_than'
    severity: str  # 'low', 'medium', 'high', 'critical'
    message_template: str

@dataclass
class Alert:
    """System alert"""
    id: str
    metric_name: str
    current_value: float
    threshold_value: float
    severity: str
    message: str
    timestamp: datetime
    resolved: bool = False
    
    def to_dict(self):
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result

class SentinelSystemMonitor:
    """Main system monitoring class"""
    
    def __init__(self):
        self.services = {
            'Django Backend': 'http://localhost:8000/health/',
            'ML Prediction API': 'http://localhost:8001/health',
            'Translation Service': 'http://localhost:8004/health',
            'NER Service': 'http://localhost:8005/health',
            'RL Decision System': 'http://localhost:8003/health',
            'Frontend Dashboard': 'http://localhost:3000'
        }
        
        self.alert_thresholds = [
            AlertThreshold('cpu_usage', 80.0, 'greater_than', 'high', 
                         'High CPU usage detected: {current_value}%'),
            AlertThreshold('memory_usage', 85.0, 'greater_than', 'high',
                         'High memory usage detected: {current_value}%'),
            AlertThreshold('disk_usage', 90.0, 'greater_than', 'critical',
                         'Critical disk usage: {current_value}%'),
            AlertThreshold('disk_free', 1000, 'less_than', 'medium',
                         'Low disk space: {current_value}MB remaining'),
        ]
        
        self.metrics_history: List[SystemMetrics] = []
        self.service_status_history: Dict[str, List[ServiceStatus]] = {}
        self.active_alerts: List[Alert] = []
        self.alert_queue = queue.Queue()
        
        # Create monitoring directories
        self.monitoring_dir = Path('monitoring')
        self.logs_dir = self.monitoring_dir / 'logs'
        self.reports_dir = self.monitoring_dir / 'reports'
        
        for directory in [self.monitoring_dir, self.logs_dir, self.reports_dir]:
            directory.mkdir(exist_ok=True)
            
        logger.info("PROJECT SENTINEL System Monitor initialized")
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system performance metrics"""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            memory_available = memory.available // (1024 * 1024)  # MB
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            disk_free = disk.free // (1024 * 1024)  # MB
            
            # Network usage
            network = psutil.net_io_counters()
            network_sent = network.bytes_sent
            network_received = network.bytes_recv
            
            # Process count
            process_count = len(psutil.pids())
            
            # Load average (Unix-like systems only)
            load_average = None
            try:
                load_average = list(os.getloadavg())
            except (OSError, AttributeError):
                # Windows doesn't have load average
                pass
            
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                memory_available=memory_available,
                disk_usage=disk_usage,
                disk_free=disk_free,
                network_sent=network_sent,
                network_received=network_received,
                process_count=process_count,
                load_average=load_average
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            raise
    
    def check_service_health(self, name: str, url: str) -> ServiceStatus:
        """Check health of a specific service"""
        start_time = time.time()
        
        try:
            response = requests.get(url, timeout=10)
            response_time = (time.time() - start_time) * 1000  # ms
            
            if response.status_code == 200:
                status = 'healthy'
                error_message = None
            else:
                status = 'unhealthy'
                error_message = f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            response_time = 10000  # 10 seconds
            status = 'unhealthy'
            error_message = "Request timeout"
            
        except requests.exceptions.ConnectionError:
            response_time = (time.time() - start_time) * 1000
            status = 'unhealthy'
            error_message = "Connection refused"
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            status = 'unknown'
            error_message = str(e)
        
        return ServiceStatus(
            name=name,
            url=url,
            status=status,
            response_time=response_time,
            last_check=datetime.now(),
            error_message=error_message
        )
    
    def check_all_services(self) -> Dict[str, ServiceStatus]:
        """Check health of all services"""
        service_statuses = {}
        
        for service_name, service_url in self.services.items():
            service_status = self.check_service_health(service_name, service_url)
            service_statuses[service_name] = service_status
            
            # Update history
            if service_name not in self.service_status_history:
                self.service_status_history[service_name] = []
            
            self.service_status_history[service_name].append(service_status)
            
            # Keep only last 100 entries per service
            if len(self.service_status_history[service_name]) > 100:
                self.service_status_history[service_name].pop(0)
        
        return service_statuses
    
    def evaluate_alerts(self, metrics: SystemMetrics):
        """Evaluate metrics against alert thresholds"""
        current_alerts = []
        
        for threshold in self.alert_thresholds:
            metric_value = getattr(metrics, threshold.metric_name, None)
            
            if metric_value is None:
                continue
            
            should_alert = False
            
            if threshold.comparison == 'greater_than':
                should_alert = metric_value > threshold.threshold_value
            elif threshold.comparison == 'less_than':
                should_alert = metric_value < threshold.threshold_value
            
            if should_alert:
                alert_id = f"{threshold.metric_name}_{int(time.time())}"
                message = threshold.message_template.format(
                    current_value=metric_value,
                    threshold_value=threshold.threshold_value
                )
                
                alert = Alert(
                    id=alert_id,
                    metric_name=threshold.metric_name,
                    current_value=metric_value,
                    threshold_value=threshold.threshold_value,
                    severity=threshold.severity,
                    message=message,
                    timestamp=datetime.now()
                )
                
                current_alerts.append(alert)
                self.alert_queue.put(alert)
                logger.warning(f"ALERT: {message}")
        
        # Update active alerts
        self.active_alerts = current_alerts
    
    def generate_monitoring_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        if not self.metrics_history:
            return {"error": "No metrics data available"}
        
        latest_metrics = self.metrics_history[-1]
        
        # Calculate averages over last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp > one_hour_ago
        ]
        
        if recent_metrics:
            avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
            avg_response_times = {}
            
            # Calculate average response times
            for service_name, status_history in self.service_status_history.items():
                recent_statuses = [
                    s for s in status_history 
                    if s.last_check > one_hour_ago and s.status == 'healthy'
                ]
                
                if recent_statuses:
                    avg_response_times[service_name] = sum(
                        s.response_time for s in recent_statuses
                    ) / len(recent_statuses)
        else:
            avg_cpu = latest_metrics.cpu_usage
            avg_memory = latest_metrics.memory_usage
            avg_response_times = {}
        
        # Get current service status
        current_services = {}
        for service_name in self.services.keys():
            if (service_name in self.service_status_history and 
                self.service_status_history[service_name]):
                latest_status = self.service_status_history[service_name][-1]
                current_services[service_name] = latest_status.to_dict()
        
        # Get alert summary from the advanced alert system
        alert_summary = alert_system.get_alert_summary()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_overview': {
                'status': 'healthy' if alert_summary['active_alerts'] == 0 else 'warning',
                'active_alerts': alert_summary['active_alerts'],
                'services_healthy': sum(
                    1 for statuses in self.service_status_history.values()
                    if statuses and statuses[-1].status == 'healthy'
                ),
                'total_services': len(self.services)
            },
            'current_metrics': latest_metrics.to_dict(),
            'hourly_averages': {
                'cpu_usage': round(avg_cpu, 2),
                'memory_usage': round(avg_memory, 2),
                'response_times': {
                    service: round(time, 2) 
                    for service, time in avg_response_times.items()
                }
            },
            'service_status': current_services,
            'active_alerts': [alert.to_dict() for alert in alert_system.active_alerts.values()],
            'alert_summary': alert_summary,
            'metrics_count': len(self.metrics_history)
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any]):
        """Save monitoring report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.reports_dir / f'system_report_{timestamp}.json'
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Monitoring report saved: {report_file}")
    
    def cleanup_old_data(self, max_age_hours: int = 24):
        """Clean up old monitoring data"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        # Clean metrics history
        self.metrics_history = [
            m for m in self.metrics_history 
            if m.timestamp > cutoff_time
        ]
        
        # Clean service status history
        for service_name in self.service_status_history:
            self.service_status_history[service_name] = [
                s for s in self.service_status_history[service_name]
                if s.last_check > cutoff_time
            ]
        
        # Clean old report files
        cutoff_timestamp = cutoff_time.strftime('%Y%m%d_%H%M%S')
        for report_file in self.reports_dir.glob('system_report_*.json'):
            if report_file.stem.split('_')[-2:] < [cutoff_timestamp.split('_')[0], cutoff_timestamp.split('_')[1]]:
                report_file.unlink()
                logger.info(f"Cleaned up old report: {report_file}")
    
    def run_monitoring_cycle(self):
        """Run single monitoring cycle"""
        logger.info("Starting monitoring cycle...")
        
        # Collect system metrics
        try:
            metrics = self.collect_system_metrics()
            self.metrics_history.append(metrics)
            
            logger.info(f"System Metrics - CPU: {metrics.cpu_usage}%, "
                       f"Memory: {metrics.memory_usage}%, "
                       f"Disk: {metrics.disk_usage}%")
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return
        
        # Check service health
        try:
            service_statuses = self.check_all_services()
            
            healthy_services = sum(
                1 for status in service_statuses.values() 
                if status.status == 'healthy'
            )
            
            logger.info(f"Service Health - {healthy_services}/{len(service_statuses)} services healthy")
            
            for name, status in service_statuses.items():
                if status.status != 'healthy':
                    logger.warning(f"{name}: {status.status} - {status.error_message}")
            
        except Exception as e:
            logger.error(f"Failed to check service health: {e}")
        
        # Evaluate alerts using the advanced alert system
        try:
            alert_metrics = {
                'cpu_usage': metrics.cpu_usage,
                'memory_usage': metrics.memory_usage,
                'disk_usage': metrics.disk_usage,
                'disk_free': metrics.disk_free,
                'services_healthy': healthy_services
            }
            
            alert_result = alert_system.process_metrics(alert_metrics)
            logger.info(f"Alert processing: {alert_result}")
            
        except Exception as e:
            logger.error(f"Failed to evaluate alerts: {e}")
        
        # Generate and save report
        try:
            report = self.generate_monitoring_report()
            self.save_report(report)
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
        
        # Cleanup old data
        try:
            self.cleanup_old_data()
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
        
        logger.info("Monitoring cycle completed")
    
    def run_continuous_monitoring(self, interval_seconds: int = 60):
        """Run continuous monitoring loop"""
        logger.info(f"Starting continuous monitoring (interval: {interval_seconds}s)")
        
        while True:
            try:
                self.run_monitoring_cycle()
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring cycle failed: {e}")
                time.sleep(interval_seconds)

def main():
    """Main monitoring function"""
    monitor = SentinelSystemMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Run single monitoring cycle
        monitor.run_monitoring_cycle()
    else:
        # Run continuous monitoring
        try:
            monitor.run_continuous_monitoring()
        except KeyboardInterrupt:
            logger.info("Monitoring stopped")
            sys.exit(0)

if __name__ == '__main__':
    main()
