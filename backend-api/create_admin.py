#!/usr/bin/env python
"""
Create Admin User for Project Sentinel
"""
import os
import sys
import django
from django.conf import settings

# Add current directory to path
sys.path.append('.')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentinel_core.minimal_settings')

try:
    django.setup()
    
    from django.contrib.auth.models import User
    
    # Create admin user
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@cdf.cm',
            password='sentinel2024'
        )
        print("✅ Admin user created successfully!")
        print("📧 Username: admin")
        print("🔐 Password: sentinel2024")
        print("🌐 Access: http://localhost:8000/admin/")
    else:
        print("⚠️ Admin user already exists")
        
except Exception as e:
    print(f"❌ Error creating admin user: {e}")

