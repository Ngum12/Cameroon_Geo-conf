# Project Sentinel - Authentication URLs
# URL patterns for authentication API endpoints

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import auth_views

urlpatterns = [
    # 🔐 Authentication Endpoints
    path('login/', auth_views.SentinelTokenObtainPairView.as_view(), name='auth_login'),
    path('register/', auth_views.UserRegistrationView.as_view(), name='auth_register'),
    path('logout/', auth_views.LogoutView.as_view(), name='auth_logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='auth_token_refresh'),
    
    # 👤 User Profile Management
    path('profile/', auth_views.UserProfileView.as_view(), name='user_profile'),
    path('change-password/', auth_views.PasswordChangeView.as_view(), name='change_password'),
    
    # 🔄 Session Management
    path('sessions/', auth_views.user_sessions, name='user_sessions'),
    path('sessions/<int:session_id>/terminate/', auth_views.terminate_session, name='terminate_session'),
    
    # 📊 Activity & Stats
    path('activity/', auth_views.user_activity_log, name='user_activity'),
    path('statistics/', auth_views.user_statistics, name='user_statistics'),
    
    # 🏥 System Health
    path('health/', auth_views.system_health, name='system_health'),
]

