# Project Sentinel - Step 1 URLs
# Django URL routing for Step 1

from django.urls import path, include
from .dashboard.step1_views import health_check, get_events, get_statistics, process_article
from .dashboard.real_nlp_views import process_article_real_nlp
from .dashboard.simple_real_nlp import test_real_nlp_simple
from .dashboard.ml_predictions_view import (
    predict_conflict,
    regional_assessment, 
    intelligence_report,
    ml_system_status
)

urlpatterns = [
    # 🔐 Authentication Routes (temporarily disabled)
    # path('api/v1/auth/', include('sentinel_core.dashboard.auth_urls')),
    
    # 🏥 System Health
    path('health/', health_check, name='health_check'),
    
    # 📊 Intelligence Data API
    path('api/v1/events/', get_events, name='get_events'),
    path('api/v1/statistics/', get_statistics, name='get_statistics'),
    path('api/v1/process-article/', process_article, name='process_article'),
    path('api/v1/process-article-real/', process_article_real_nlp, name='process_article_real_nlp'),
    path('api/v1/test-nlp/', test_real_nlp_simple, name='test_real_nlp_simple'),
    
    # 🤖 ML Prediction endpoints
    path('api/v1/ml/predict/', predict_conflict, name='ml_predict_conflict'),
    path('api/v1/ml/regional-assessment/', regional_assessment, name='ml_regional_assessment'),
    path('api/v1/ml/intelligence-report/', intelligence_report, name='ml_intelligence_report'),
    path('api/v1/ml/status/', ml_system_status, name='ml_system_status'),
]



