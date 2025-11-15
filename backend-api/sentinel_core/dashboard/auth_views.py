# Project Sentinel - Authentication Views
# Django REST API views for user authentication

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from django.contrib.gis.geoip2 import GeoIP2
from django.utils import timezone
from django.db.models import Count, Q
from django.http import JsonResponse
import jwt
from datetime import datetime, timedelta
import uuid

from .models import SentinelUser, UserSession, UserActivity
from .serializers import (
    SentinelTokenObtainPairSerializer, 
    UserRegistrationSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer,
    LoginSerializer,
    UserStatsSerializer,
    SystemHealthSerializer
)

class SentinelTokenObtainPairView(TokenObtainPairView):
    """
    🔐 CUSTOM JWT TOKEN VIEW
    Enhanced JWT token generation with user tracking
    """
    serializer_class = SentinelTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get user from token
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.user
            
            # Record successful login
            ip_address = self.get_client_ip(request)
            user.record_login(ip_address)
            
            # Create user session
            self.create_user_session(user, request)
            
            # Log activity
            UserActivity.objects.create(
                user=user,
                action='LOGIN',
                description=f'User logged in successfully',
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                endpoint='/auth/login/',
                method='POST',
                status_code=200,
                risk_level='LOW'
            )
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def create_user_session(self, user, request):
        """Create user session record"""
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Try to get location from IP (optional)
        location = ""
        try:
            g = GeoIP2()
            location_data = g.city(ip_address)
            location = f"{location_data['city']}, {location_data['country_name']}"
        except:
            location = "Unknown Location"
        
        # Create session
        UserSession.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            location=location,
            device_info={
                'user_agent': user_agent,
                'ip': ip_address,
                'login_time': timezone.now().isoformat()
            },
            expires_at=timezone.now() + timedelta(hours=24)
        )

class UserRegistrationView(APIView):
    """
    📝 USER REGISTRATION VIEW
    Handle new user registration
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user = serializer.save()
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                
                # Add custom claims
                access_token['role'] = user.role
                access_token['clearance_level'] = user.clearance_level
                access_token['display_name'] = user.display_name
                
                # Log registration activity
                ip_address = self.get_client_ip(request)
                UserActivity.objects.create(
                    user=user,
                    action='REGISTER',
                    description=f'New user registered: {user.display_name}',
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    endpoint='/auth/register/',
                    method='POST',
                    status_code=201,
                    risk_level='MEDIUM'
                )
                
                return Response({
                    'message': '🎉 Registration successful! Welcome to Project Sentinel!',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'display_name': user.display_name,
                        'role': user.role,
                        'clearance_level': user.clearance_level,
                    },
                    'tokens': {
                        'access': str(access_token),
                        'refresh': str(refresh),
                    }
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': 'Registration failed',
                    'details': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'error': 'Invalid registration data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class UserProfileView(APIView):
    """
    👤 USER PROFILE VIEW
    Handle user profile operations
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user profile"""
        serializer = UserProfileSerializer(request.user)
        return Response({
            'profile': serializer.data,
            'permissions': {
                'is_commander': request.user.is_commander,
                'can_access_classified': request.user.can_access_classified,
                'api_access_enabled': request.user.api_access_enabled,
            }
        })
    
    def put(self, request):
        """Update user profile"""
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            # Log profile update
            UserActivity.objects.create(
                user=request.user,
                action='PROFILE_UPDATE',
                description='User updated profile information',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                endpoint='/auth/profile/',
                method='PUT',
                status_code=200,
                risk_level='LOW'
            )
            
            return Response({
                'message': 'Profile updated successfully',
                'profile': serializer.data
            })
        
        return Response({
            'error': 'Invalid profile data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class PasswordChangeView(APIView):
    """
    🔐 PASSWORD CHANGE VIEW
    Handle secure password changes
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Log password change
            UserActivity.objects.create(
                user=user,
                action='PASSWORD_CHANGE',
                description='User changed password',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                endpoint='/auth/change-password/',
                method='POST',
                status_code=200,
                risk_level='MEDIUM'
            )
            
            return Response({
                'message': '🔐 Password changed successfully! Please login again.'
            })
        
        return Response({
            'error': 'Password change failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class LogoutView(APIView):
    """
    🚪 LOGOUT VIEW
    Handle user logout and token invalidation
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Deactivate user sessions
            UserSession.objects.filter(
                user=request.user,
                is_active=True
            ).update(is_active=False)
            
            # Log logout activity
            UserActivity.objects.create(
                user=request.user,
                action='LOGOUT',
                description='User logged out',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                endpoint='/auth/logout/',
                method='POST',
                status_code=200,
                risk_level='LOW'
            )
            
            return Response({
                'message': '👋 Logout successful. Stay safe!'
            })
            
        except Exception as e:
            return Response({
                'error': 'Logout failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_sessions(request):
    """
    🔄 GET USER SESSIONS
    Get active user sessions
    """
    sessions = UserSession.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-last_activity')[:10]  # Last 10 sessions
    
    session_data = []
    for session in sessions:
        session_data.append({
            'id': session.id,
            'ip_address': session.ip_address,
            'location': session.location,
            'created_at': session.created_at,
            'last_activity': session.last_activity,
            'is_current': str(session.session_token) in request.META.get('HTTP_AUTHORIZATION', ''),
        })
    
    return Response({
        'sessions': session_data,
        'total_active': sessions.count()
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def terminate_session(request, session_id):
    """
    ❌ TERMINATE SESSION
    Terminate a specific user session
    """
    try:
        session = UserSession.objects.get(
            id=session_id,
            user=request.user
        )
        session.is_active = False
        session.save()
        
        # Log session termination
        UserActivity.objects.create(
            user=request.user,
            action='SESSION_TERMINATE',
            description=f'User terminated session {session_id}',
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            endpoint=f'/auth/sessions/{session_id}/terminate/',
            method='POST',
            status_code=200,
            risk_level='MEDIUM'
        )
        
        return Response({
            'message': 'Session terminated successfully'
        })
        
    except UserSession.DoesNotExist:
        return Response({
            'error': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_activity_log(request):
    """
    📊 GET USER ACTIVITY LOG
    Get user's recent activities
    """
    activities = UserActivity.objects.filter(
        user=request.user
    ).order_by('-created_at')[:50]  # Last 50 activities
    
    activity_data = []
    for activity in activities:
        activity_data.append({
            'action': activity.action,
            'description': activity.description,
            'ip_address': activity.ip_address,
            'created_at': activity.created_at,
            'risk_level': activity.risk_level,
            'endpoint': activity.endpoint,
            'method': activity.method,
        })
    
    return Response({
        'activities': activity_data,
        'total': activities.count()
    })

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def user_statistics(request):
    """
    📈 GET USER STATISTICS
    Get system-wide user statistics (Admin only)
    """
    total_users = SentinelUser.objects.count()
    active_users = SentinelUser.objects.filter(is_active=True).count()
    
    # Users by role
    users_by_role = dict(
        SentinelUser.objects.values('role').annotate(count=Count('role')).values_list('role', 'count')
    )
    
    # Users by clearance
    users_by_clearance = dict(
        SentinelUser.objects.values('clearance_level').annotate(count=Count('clearance_level')).values_list('clearance_level', 'count')
    )
    
    # Recent registrations (last 30 days)
    recent_registrations = SentinelUser.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Active sessions
    active_sessions = UserSession.objects.filter(
        is_active=True,
        expires_at__gt=timezone.now()
    ).count()
    
    # Failed logins today
    failed_logins_today = UserActivity.objects.filter(
        action='LOGIN',
        created_at__date=timezone.now().date(),
        risk_level='HIGH'
    ).count()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'users_by_role': users_by_role,
        'users_by_clearance': users_by_clearance,
        'recent_registrations': recent_registrations,
        'active_sessions': active_sessions,
        'failed_logins_today': failed_logins_today,
    }
    
    return Response(stats)

@api_view(['GET'])
def system_health(request):
    """
    🏥 SYSTEM HEALTH CHECK
    Get system health status
    """
    try:
        # Basic health checks
        db_status = "HEALTHY"
        try:
            SentinelUser.objects.count()
        except:
            db_status = "ERROR"
        
        active_users = UserSession.objects.filter(
            is_active=True,
            expires_at__gt=timezone.now()
        ).count()
        
        # Security alerts (high-risk activities in last 24 hours)
        security_alerts = UserActivity.objects.filter(
            risk_level__in=['HIGH', 'CRITICAL'],
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        health_data = {
            'status': 'HEALTHY' if db_status == 'HEALTHY' else 'ERROR',
            'uptime': str(timezone.now() - datetime(2024, 1, 1, tzinfo=timezone.utc)),
            'active_users': active_users,
            'database_status': db_status,
            'api_status': 'HEALTHY',
            'last_backup': timezone.now() - timedelta(hours=2),  # Mock data
            'security_alerts': security_alerts,
            'timestamp': timezone.now()
        }
        
        return Response(health_data)
        
    except Exception as e:
        return Response({
            'status': 'ERROR',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

