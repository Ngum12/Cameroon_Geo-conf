"""
PROJECT SENTINEL - POSTGRESQL PRODUCTION SETTINGS
Cameroon Defense Force OSINT Analysis System
Production-grade PostgreSQL configuration
"""

from .settings import *
import os

# Database - PostgreSQL Production Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sentinel_defense',
        'USER': 'sentinel_admin',
        'PASSWORD': 'CameroonDefense2025!',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'connect_timeout': 20,
            'options': '-c default_transaction_isolation=read_committed'
        },
    }
}

# Enable connection pooling
DATABASES['default']['CONN_HEALTH_CHECKS'] = True

# Cache Configuration for PostgreSQL
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'sentinel_cache_table',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 10000,
            'CULL_FREQUENCY': 3,
        }
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'

# Logging Configuration for Production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',  # Reduce DB query logging
            'propagate': False,
        },
        'sentinel_core': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
import os
os.makedirs('logs', exist_ok=True)

# Security Settings for Production
SECURE_SSL_REDIRECT = False  # Set to True in production with SSL
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Performance Optimizations
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database Query Optimization
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Enable PostgreSQL-specific features
DATABASE_ROUTERS = []

print("PostgreSQL Production Settings Loaded")
print("Database: sentinel_defense")
print("User: sentinel_admin")
print("Host: localhost:5432")