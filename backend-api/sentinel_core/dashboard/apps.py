# -*- coding: utf-8 -*-
"""
Project Sentinel Dashboard App Configuration
Cameroon Defense Force OSINT Analysis System
"""

from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """Configuration for the Dashboard app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sentinel_core.dashboard'
    verbose_name = 'Project Sentinel Dashboard'
    
    def ready(self):
        """Initialize app when Django starts."""
        # Import signals if you add them later
        # from . import signals
        pass
