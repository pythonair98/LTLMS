#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LTLMS.settings_docker_simple')
django.setup()

from user_auth.models import Occupation, Team

# --- Occupations Data ---
occupations_data = [
    {
        "id": 2,
        "ar_name": "مدير دائرة التراخيص",
        "en_name": "Licensing Department Director",
        "power": 1,
        "users_count": 0,
    },
    {
        "id": 3,
        "ar_name": "نائب مدير دائرة التراخيص",
        "en_name": "Deputy Licensing Department Director",
        "power": 2,
        "users_count": 0,
    },
    {
        "id": 4,
        "ar_name": "رئيس قسم التراخيص",
        "en_name": "Licensing Section Head",
        "power": 3,
        "users_count": 0,
    },
    {
        "id": 5,
        "ar_name": "مسؤول إصدار التراخيص",
        "en_name": "Licensing Officer",
        "power": 4,
        "users_count": 0,
    },
    {
        "id": 6,
        "ar_name": "مفتش تراخيص النقل",
        "en_name": "Transport Licensing Inspector",
        "power": 5,
        "users_count": 0,
    },
    {
        "id": 7,
        "ar_name": "موظف إدخال بيانات التراخيص",
        "en_name": "Licensing Data Entry Clerk",
        "power": 6,
        "users_count": 0,
    },
]

for occ in occupations_data:
    obj, created = Occupation.objects.get_or_create(
        id=occ["id"],
        defaults={
            "ar_name": occ["ar_name"],
            "en_name": occ["en_name"],
            "power": occ["power"],
            "users_count": occ["users_count"],
        }
    )
    if not created:
        # Update fields if already exists
        obj.ar_name = occ["ar_name"]
        obj.en_name = occ["en_name"]
        obj.power = occ["power"]
        obj.users_count = occ["users_count"]
        obj.save()
    print(f"Occupation {obj.en_name} ({'created' if created else 'updated'})")

# --- Teams Data (example, add your own as needed) ---
teams_data = [
    {"ar_name": "الفريق الأول", "en_name": "Team One"},
    {"ar_name": "الفريق الثاني", "en_name": "Team Two"},
]

for team in teams_data:
    obj, created = Team.objects.get_or_create(
        ar_name=team["ar_name"],
        en_name=team["en_name"]
    )
    print(f"Team {obj.en_name} ({'created' if created else 'already exists'})") 