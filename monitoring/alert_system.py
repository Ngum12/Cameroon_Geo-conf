#!/usr/bin/env python3
"""
PROJECT SENTINEL - ALERT SYSTEM
Cameroon Defense Force OSINT Analysis System
Advanced alerting and notification system
"""

import smtplib
import json
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class NotificationChannel:
    """Notification channel configuration"""
    name: str
    type: str  # 'email', 'webhook', 'file'
    config: Dict[str, Any]
    enabled: bool = True

@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    metric: str
    condition: str  # 'greater_than', 'less_than', 'equals', 'not_equals'
    threshold: float
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    cooldown_minutes: int = 15  # Minimum time between same alerts
    enabled: bool = True
    
    def matches(self, metric_name: str, value: float) -> bool:
        """Check if metric value matches alert condition"""
        if not self.enabled or self.metric != metric_name:
            return False
        
        if self.condition == 'greater_than':
            return value > self.threshold
        elif self.condition == 'less_than':
            return value < self.threshold
        elif self.condition == 'equals':
            return abs(value - self.threshold) < 0.001
        elif self.condition == 'not_equals':
            return abs(value - self.threshold) >= 0.001
        
        return False

@dataclass 
class AlertEvent:
    """Alert event instance"""
    id: str
    rule_name: str
    metric_name: str
    current_value: float
    threshold_value: float
    severity: str
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    def to_dict(self):
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        if self.resolved_at:
            result['resolved_at'] = self.resolved_at.isoformat()
        return result

class ProjectSentinelAlertSystem:
    """Advanced alert system for PROJECT SENTINEL"""
    
    def __init__(self, config_file: str = "monitoring/config/alert_config.json"):
        self.config_file = Path(config_file)
        self.alerts_dir = Path("monitoring/alerts")
        self.logs_dir = Path("monitoring/logs")
        
        # Create directories
        for directory in [self.alerts_dir, self.logs_dir, self.config_file.parent]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.load_config()
        
        # Alert tracking
        self.active_alerts: Dict[str, AlertEvent] = {}
        self.alert_history: List[AlertEvent] = []
        self.last_alert_times: Dict[str, datetime] = {}
        
        logger.info("PROJECT SENTINEL Alert System initialized")
    
    def load_config(self):
        """Load alert configuration from file"""
        default_config = {
            "notification_channels": [
                {
                    "name": "file_logger",
                    "type": "file",
                    "enabled": True,
                    "config": {
                        "file_path": "monitoring/logs/alerts.log",
                        "format": "detailed"
                    }
                },
                {
                    "name": "email_admin",
                    "type": "email",
                    "enabled": False,
                    "config": {
                        "smtp_server": "smtp.gmail.com",
                        "smtp_port": 587,
                        "sender_email": "sentinel@defense.cam",
                        "sender_password": "your_password_here",
                        "recipient_emails": ["admin@defense.cam"],
                        "use_tls": True
                    }
                }
            ],
            "alert_rules": [
                {
                    "name": "High CPU Usage",
                    "metric": "cpu_usage",
                    "condition": "greater_than",
                    "threshold": 80.0,
                    "severity": "high",
                    "description": "CPU usage exceeded 80%",
                    "cooldown_minutes": 10,
                    "enabled": True
                },
                {
                    "name": "Critical CPU Usage",
                    "metric": "cpu_usage",
                    "condition": "greater_than",
                    "threshold": 95.0,
                    "severity": "critical",
                    "description": "CPU usage critically high at 95%+",
                    "cooldown_minutes": 5,
                    "enabled": True
                },
                {
                    "name": "High Memory Usage",
                    "metric": "memory_usage",
                    "condition": "greater_than",
                    "threshold": 85.0,
                    "severity": "high",
                    "description": "Memory usage exceeded 85%",
                    "cooldown_minutes": 10,
                    "enabled": True
                },
                {
                    "name": "Critical Memory Usage",
                    "metric": "memory_usage",
                    "condition": "greater_than",
                    "threshold": 95.0,
                    "severity": "critical",
                    "description": "Memory usage critically high at 95%+",
                    "cooldown_minutes": 5,
                    "enabled": True
                },
                {
                    "name": "Low Disk Space",
                    "metric": "disk_free",
                    "condition": "less_than",
                    "threshold": 1000.0,  # MB
                    "severity": "medium",
                    "description": "Low disk space - less than 1GB remaining",
                    "cooldown_minutes": 30,
                    "enabled": True
                },
                {
                    "name": "Critical Disk Space",
                    "metric": "disk_free",
                    "condition": "less_than",
                    "threshold": 500.0,  # MB
                    "severity": "critical",
                    "description": "Critical disk space - less than 500MB remaining",
                    "cooldown_minutes": 15,
                    "enabled": True
                },
                {
                    "name": "Service Unavailable",
                    "metric": "services_healthy",
                    "condition": "less_than",
                    "threshold": 5.0,  # Less than 5 services healthy
                    "severity": "high",
                    "description": "Multiple services are unhealthy",
                    "cooldown_minutes": 5,
                    "enabled": True
                }
            ]
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}. Using defaults.")
                config = default_config
        else:
            config = default_config
            self.save_config(config)
        
        # Parse configuration
        self.notification_channels = [
            NotificationChannel(**channel) for channel in config.get("notification_channels", [])
        ]
        
        self.alert_rules = [
            AlertRule(**rule) for rule in config.get("alert_rules", [])
        ]
        
        logger.info(f"Loaded {len(self.alert_rules)} alert rules and {len(self.notification_channels)} notification channels")
    
    def save_config(self, config: Dict):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def generate_alert_id(self, rule_name: str, metric_name: str) -> str:
        """Generate unique alert ID"""
        data = f"{rule_name}_{metric_name}_{datetime.now().strftime('%Y%m%d')}"
        return hashlib.md5(data.encode()).hexdigest()[:8]
    
    def check_cooldown(self, rule_name: str, cooldown_minutes: int) -> bool:
        """Check if alert is in cooldown period"""
        if rule_name not in self.last_alert_times:
            return True
        
        last_alert_time = self.last_alert_times[rule_name]
        cooldown_period = timedelta(minutes=cooldown_minutes)
        
        return datetime.now() - last_alert_time > cooldown_period
    
    def evaluate_metrics(self, metrics: Dict[str, float]) -> List[AlertEvent]:
        """Evaluate metrics against alert rules"""
        new_alerts = []
        
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            if rule.metric not in metrics:
                continue
            
            metric_value = metrics[rule.metric]
            
            if rule.matches(rule.metric, metric_value):
                # Check cooldown
                if not self.check_cooldown(rule.name, rule.cooldown_minutes):
                    continue
                
                # Generate alert
                alert_id = self.generate_alert_id(rule.name, rule.metric)
                
                alert = AlertEvent(
                    id=alert_id,
                    rule_name=rule.name,
                    metric_name=rule.metric,
                    current_value=metric_value,
                    threshold_value=rule.threshold,
                    severity=rule.severity,
                    message=f"{rule.description} (Current: {metric_value}, Threshold: {rule.threshold})",
                    timestamp=datetime.now()
                )
                
                new_alerts.append(alert)
                self.active_alerts[alert_id] = alert
                self.alert_history.append(alert)
                self.last_alert_times[rule.name] = datetime.now()
                
                logger.warning(f"ALERT TRIGGERED: {alert.message}")
        
        return new_alerts
    
    def resolve_alerts(self, metrics: Dict[str, float]):
        """Check if any active alerts should be resolved"""
        resolved_alerts = []
        
        for alert_id, alert in list(self.active_alerts.items()):
            if alert.resolved:
                continue
            
            # Find the rule for this alert
            rule = next((r for r in self.alert_rules if r.name == alert.rule_name), None)
            if not rule:
                continue
            
            if alert.metric_name not in metrics:
                continue
            
            current_value = metrics[alert.metric_name]
            
            # Check if condition is no longer met (alert should be resolved)
            if not rule.matches(alert.metric_name, current_value):
                alert.resolved = True
                alert.resolved_at = datetime.now()
                resolved_alerts.append(alert)
                
                logger.info(f"ALERT RESOLVED: {alert.rule_name} - {alert.metric_name} now at {current_value}")
        
        # Clean up resolved alerts
        for alert in resolved_alerts:
            if alert.id in self.active_alerts:
                del self.active_alerts[alert.id]
        
        return resolved_alerts
    
    def send_notifications(self, alerts: List[AlertEvent]):
        """Send notifications for alerts"""
        if not alerts:
            return
        
        for channel in self.notification_channels:
            if not channel.enabled:
                continue
            
            try:
                if channel.type == "file":
                    self.send_file_notification(channel, alerts)
                elif channel.type == "email":
                    self.send_email_notification(channel, alerts)
                elif channel.type == "webhook":
                    self.send_webhook_notification(channel, alerts)
                else:
                    logger.warning(f"Unknown notification channel type: {channel.type}")
            
            except Exception as e:
                logger.error(f"Failed to send notification via {channel.name}: {e}")
    
    def send_file_notification(self, channel: NotificationChannel, alerts: List[AlertEvent]):
        """Send file-based notification"""
        log_file = Path(channel.config.get("file_path", "monitoring/logs/alerts.log"))
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            for alert in alerts:
                if channel.config.get("format") == "detailed":
                    log_entry = (
                        f"[{alert.severity.upper()}] {alert.timestamp.isoformat()} - "
                        f"{alert.rule_name}: {alert.message}\n"
                        f"  Metric: {alert.metric_name} = {alert.current_value}\n"
                        f"  Threshold: {alert.threshold_value}\n"
                        f"  Alert ID: {alert.id}\n\n"
                    )
                else:
                    log_entry = (
                        f"[{alert.severity.upper()}] {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - "
                        f"{alert.message}\n"
                    )
                
                f.write(log_entry)
        
        logger.info(f"File notification sent to {log_file}")
    
    def send_email_notification(self, channel: NotificationChannel, alerts: List[AlertEvent]):
        """Send email notification"""
        config = channel.config
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = config['sender_email']
        msg['To'] = ', '.join(config['recipient_emails'])
        msg['Subject'] = f"PROJECT SENTINEL Alert - {len(alerts)} alert(s) triggered"
        
        # Build email body
        body = "PROJECT SENTINEL - System Alert\n"
        body += "Cameroon Defense Force Intelligence Platform\n"
        body += "=" * 50 + "\n\n"
        
        for alert in alerts:
            body += f"ALERT: {alert.rule_name}\n"
            body += f"Severity: {alert.severity.upper()}\n"
            body += f"Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            body += f"Message: {alert.message}\n"
            body += f"Metric: {alert.metric_name} = {alert.current_value}\n"
            body += f"Threshold: {alert.threshold_value}\n"
            body += "-" * 30 + "\n\n"
        
        body += "Please check the system immediately.\n"
        body += "Access monitoring dashboard at: http://localhost:8006\n"
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        if config.get('use_tls'):
            server.starttls()
        server.login(config['sender_email'], config['sender_password'])
        
        text = msg.as_string()
        server.sendmail(config['sender_email'], config['recipient_emails'], text)
        server.quit()
        
        logger.info(f"Email notification sent to {config['recipient_emails']}")
    
    def send_webhook_notification(self, channel: NotificationChannel, alerts: List[AlertEvent]):
        """Send webhook notification"""
        import requests
        
        config = channel.config
        webhook_url = config['url']
        
        payload = {
            "source": "PROJECT SENTINEL",
            "timestamp": datetime.now().isoformat(),
            "alerts": [alert.to_dict() for alert in alerts]
        }
        
        headers = config.get('headers', {'Content-Type': 'application/json'})
        
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        logger.info(f"Webhook notification sent to {webhook_url}")
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of alert system status"""
        active_by_severity = {}
        for alert in self.active_alerts.values():
            severity = alert.severity
            active_by_severity[severity] = active_by_severity.get(severity, 0) + 1
        
        return {
            "active_alerts": len(self.active_alerts),
            "total_rules": len(self.alert_rules),
            "enabled_rules": sum(1 for rule in self.alert_rules if rule.enabled),
            "notification_channels": len(self.notification_channels),
            "active_by_severity": active_by_severity,
            "last_evaluation": datetime.now().isoformat()
        }
    
    def process_metrics(self, metrics: Dict[str, float]):
        """Process metrics and handle alerts"""
        # Evaluate new alerts
        new_alerts = self.evaluate_metrics(metrics)
        
        # Resolve existing alerts
        resolved_alerts = self.resolve_alerts(metrics)
        
        # Send notifications for new alerts
        if new_alerts:
            self.send_notifications(new_alerts)
        
        # Log resolved alerts
        for alert in resolved_alerts:
            logger.info(f"Alert resolved: {alert.rule_name}")
        
        return {
            "new_alerts": len(new_alerts),
            "resolved_alerts": len(resolved_alerts),
            "active_alerts": len(self.active_alerts)
        }

# Global alert system instance
alert_system = ProjectSentinelAlertSystem()

if __name__ == "__main__":
    # Test alert system
    test_metrics = {
        "cpu_usage": 85.0,
        "memory_usage": 90.0,
        "disk_free": 800.0,
        "services_healthy": 4.0
    }
    
    print("Testing PROJECT SENTINEL Alert System...")
    result = alert_system.process_metrics(test_metrics)
    print(f"Result: {result}")
    
    summary = alert_system.get_alert_summary()
    print(f"Alert Summary: {json.dumps(summary, indent=2)}")
