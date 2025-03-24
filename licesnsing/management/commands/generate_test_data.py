from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

from licesnsing.models import (
    Activity, MainCategory, SubCategory, Establishment,
    EstablishmentRegister, EstablishmentLicence, Inspection
)


class Command(BaseCommand):
    help = 'Generates test data for charts'

    def handle(self, *args, **kwargs):
        # Create activities
        activities = []
        for i in range(5):
            activity = Activity.objects.create(
                ar_name=f"نشاط {i + 1}",
                en_name=f"Activity {i + 1}",
                code=f"ACT{i + 1}"
            )
            activities.append(activity)

        # Create categories
        main_category = MainCategory.objects.create(ar_name="فئة رئيسية", en_name="Main Category")
        sub_category = SubCategory.objects.create(ar_name="فئة فرعية", en_name="Sub Category")

        # Create municipalities
        municipalities = ["الرياض", "جدة", "الدمام", "مكة", "المدينة"]

        # Create establishments
        establishments = []
        for i in range(20):
            establishment = Establishment.objects.create(
                rifd=f"RFID{i + 1}",
                establishment_name=f"منشأة {i + 1}",
                main_category=main_category,
                sub_category=sub_category,
                owner_name=f"مالك {i + 1}",
                owner_number=f"05{random.randint(10000000, 99999999)}",
                director_name=f"مدير {i + 1}",
                director_number=f"05{random.randint(10000000, 99999999)}",
                representative_name=f"ممثل {i + 1}",
                representative_number=f"05{random.randint(10000000, 99999999)}",
                box_O_P=random.randint(1000, 9999),
                email=f"test{i + 1}@example.com",
                phone_number=f"05{random.randint(10000000, 99999999)}",
                municipality_name=random.choice(municipalities),
                region_number=str(random.randint(1, 13)),
                street_number=random.randint(1, 100),
                street_name=f"شارع {i + 1}",
                building_number=random.randint(1, 1000),
                block_number=random.randint(1, 50),
                block_name=f"حي {i + 1}",
                activity=random.choice(activities)
            )
            establishments.append(establishment)

        # Create registers and licenses
        today = timezone.now().date()
        for establishment in establishments:
            register = EstablishmentRegister.objects.create(
                establishment=establishment,
                issuance_date=today - timedelta(days=random.randint(1, 365)),
                expiration_date=today + timedelta(days=random.randint(-30, 365))
            )

            EstablishmentLicence.objects.create(
                register=register,
                creation_date=today - timedelta(days=random.randint(1, 365)),
                expiration_date=today + timedelta(days=random.randint(-30, 365)),
                main_category=main_category,
                activity=random.choice(activities),
                sub_category=sub_category
            )

        # Create some inspections
        if not User.objects.filter(username='inspector').exists():
            User.objects.create_user('inspector', 'inspector@example.com', 'password')
        inspector = User.objects.get(username='inspector')

        for register in EstablishmentRegister.objects.all():
            Inspection.objects.create(
                register_number=str(register.id),
                notes="Test inspection notes",
                latitude="24.7136",
                longitude="46.6753",
                status=random.choice([True, False]),
                inspector=inspector
            )

        self.stdout.write(self.style.SUCCESS('Successfully generated test data'))
