#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LTLMS.settings_docker_simple')
django.setup()

from django.contrib.auth.models import User

# Create superuser
if not User.objects.filter(username='manager').exists():
    User.objects.create_superuser('manager', '', 'manger@2025#')
    print("Superuser 'manager' created successfully!")
else:
    print("Superuser 'manager' already exists!") 