# -*- coding: utf-8 -*-
"""
Project Sentinel Dashboard URLs
Cameroon Defense Force OSINT Analysis System

URL routing for dashboard API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    HealthCheckView,
    ProcessArticleView,
    GetEventsView,
    ArticleDetailView,
    ArticleListView,
    statistics_view,
)

app_name = 'dashboard'

# API endpoints
urlpatterns = [
    # Health check
    path('health/', HealthCheckView.as_view(), name='health-check'),
    
    # Article processing
    path('process-article/', ProcessArticleView.as_view(), name='process-article'),
    
    # Events and mapping
    path('events/', GetEventsView.as_view(), name='get-events'),
    
    # Article management
    path('articles/', ArticleListView.as_view(), name='article-list'),
    path('articles/<uuid:pk>/', ArticleDetailView.as_view(), name='article-detail'),
    
    # Statistics and analytics
    path('statistics/', statistics_view, name='statistics'),
]
