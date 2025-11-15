# Project Sentinel - Authentication Serializers
# Django REST Framework serializers for authentication

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import SentinelUser, UserSession, UserActivity
import re

class SentinelTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    🔐 CUSTOM JWT TOKEN SERIALIZER
    Enhanced JWT token with user role and clearance information
    """
    
    def validate(self, attrs):
        # Get the token pair
        data = super().validate(attrs)
        
        # Add custom claims
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'display_name': self.user.display_name,
            'role': self.user.role,
            'clearance_level': self.user.clearance_level,
            'rank': self.user.rank,
            'unit': self.user.unit,
            'is_commander': self.user.is_commander,
            'can_access_classified': self.user.can_access_classified,
            'profile_picture': self.user.profile_picture,
        }
        
        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    📝 USER REGISTRATION SERIALIZER
    Handle new user registration with validation
    """
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    employee_id = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = SentinelUser
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'employee_id', 'rank', 'unit',
            'clearance_level', 'role', 'phone_number', 'secure_email',
            'location'
        ]
    
    def validate_username(self, value):
        """Validate username format"""
        if not re.match(r'^[a-zA-Z0-9_.-]+$', value):
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, dots, underscores, and hyphens."
            )
        return value
    
    def validate_employee_id(self, value):
        """Validate employee ID format"""
        if value and not re.match(r'^[A-Z]{2,4}\d{4,6}$', value):
            raise serializers.ValidationError(
                "Employee ID must be in format: 2-4 letters followed by 4-6 numbers (e.g., CDF001234)"
            )
        return value
    
    def validate_email(self, value):
        """Validate email domain"""
        if value:
            # Allow government and military domains
            allowed_domains = ['.gov.cm', '.mil.cm', 'defense.gov.cm', 'admin.gov.cm']
            domain_valid = any(value.endswith(domain) for domain in allowed_domains)
            
            # For development, also allow common domains
            if not domain_valid and not (value.endswith('.com') or value.endswith('.org')):
                raise serializers.ValidationError(
                    "Please use an official government or military email address."
                )
        return value
    
    def validate(self, data):
        """Validate password confirmation"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        
        # Validate password strength
        try:
            validate_password(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError({'password': e.messages})
        
        return data
    
    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = SentinelUser.objects.create_user(
            password=password,
            **validated_data
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """
    👤 USER PROFILE SERIALIZER
    Handle user profile updates
    """
    
    class Meta:
        model = SentinelUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'employee_id', 'rank', 'unit', 'clearance_level', 'role',
            'phone_number', 'secure_email', 'profile_picture', 'bio',
            'location', 'date_joined', 'last_login', 'last_activity',
            'two_factor_enabled', 'is_commander', 'can_access_classified'
        ]
        read_only_fields = [
            'id', 'username', 'date_joined', 'last_login', 'clearance_level',
            'role', 'is_commander', 'can_access_classified'
        ]

class PasswordChangeSerializer(serializers.Serializer):
    """
    🔐 PASSWORD CHANGE SERIALIZER
    Handle secure password changes
    """
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match.")
        
        # Validate password strength
        try:
            validate_password(data['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({'new_password': e.messages})
        
        return data
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

class UserSessionSerializer(serializers.ModelSerializer):
    """
    🔄 USER SESSION SERIALIZER
    Handle user session information
    """
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'session_token', 'ip_address', 'location',
            'device_info', 'created_at', 'last_activity',
            'expires_at', 'is_active'
        ]
        read_only_fields = ['session_token', 'created_at']

class UserActivitySerializer(serializers.ModelSerializer):
    """
    📊 USER ACTIVITY SERIALIZER
    Handle user activity logs
    """
    
    user_display_name = serializers.CharField(source='user.display_name', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'user_display_name', 'action', 'description',
            'ip_address', 'endpoint', 'method', 'status_code',
            'risk_level', 'created_at', 'metadata'
        ]
        read_only_fields = ['created_at']

class LoginSerializer(serializers.Serializer):
    """
    🚪 LOGIN SERIALIZER
    Handle user login with enhanced security
    """
    
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    remember_me = serializers.BooleanField(default=False)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            # Check if user exists
            try:
                user = SentinelUser.objects.get(username=username)
            except SentinelUser.DoesNotExist:
                raise serializers.ValidationError("Invalid username or password.")
            
            # Check if account is locked
            if user.is_account_locked():
                raise serializers.ValidationError(
                    f"Account is locked due to multiple failed login attempts. "
                    f"Try again after {user.account_locked_until.strftime('%H:%M')}."
                )
            
            # Authenticate user
            user = authenticate(username=username, password=password)
            if not user:
                # Record failed login attempt
                try:
                    failed_user = SentinelUser.objects.get(username=username)
                    failed_user.record_failed_login()
                except SentinelUser.DoesNotExist:
                    pass
                raise serializers.ValidationError("Invalid username or password.")
            
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
            
            data['user'] = user
        else:
            raise serializers.ValidationError("Username and password are required.")
        
        return data

class UserStatsSerializer(serializers.Serializer):
    """
    📈 USER STATISTICS SERIALIZER
    Handle user statistics and metrics
    """
    
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    users_by_role = serializers.DictField()
    users_by_clearance = serializers.DictField()
    recent_registrations = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    failed_logins_today = serializers.IntegerField()
    
class SystemHealthSerializer(serializers.Serializer):
    """
    🏥 SYSTEM HEALTH SERIALIZER
    Handle system health status
    """
    
    status = serializers.CharField()
    uptime = serializers.CharField()
    active_users = serializers.IntegerField()
    database_status = serializers.CharField()
    api_status = serializers.CharField()
    last_backup = serializers.DateTimeField()
    security_alerts = serializers.IntegerField()