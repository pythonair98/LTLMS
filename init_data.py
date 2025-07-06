#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LTLMS.settings_docker_simple')
django.setup()

from django.contrib.auth.models import User
from user_auth.models import Occupation, Team
from ILAS.models import Activity

# --- Create Superuser ---
if not User.objects.filter(username='manager').exists():
    User.objects.create_superuser('manager', '', 'manger@2025#')
    print("Superuser 'manager' created successfully!")
else:
    print("Superuser 'manager' already exists!")

# --- Occupations Data ---
occupations_data = [
    {"id": 2, "ar_name": "مدير دائرة التراخيص", "en_name": "Licensing Department Director", "power": 1},
    {"id": 3, "ar_name": "نائب مدير دائرة التراخيص", "en_name": "Deputy Licensing Department Director", "power": 2},
    {"id": 4, "ar_name": "رئيس قسم التراخيص", "en_name": "Licensing Section Head", "power": 3},
    {"id": 5, "ar_name": "مسؤول إصدار التراخيص", "en_name": "Licensing Officer", "power": 4},
    {"id": 6, "ar_name": "مفتش تراخيص النقل", "en_name": "Transport Licensing Inspector", "power": 5},
    {"id": 7, "ar_name": "موظف إدخال بيانات التراخيص", "en_name": "Licensing Data Entry Clerk", "power": 6},
]

for occ in occupations_data:
    obj, created = Occupation.objects.get_or_create(
        id=occ["id"],
        defaults={
            "ar_name": occ["ar_name"],
            "en_name": occ["en_name"],
            "power": occ["power"],
        }
    )
    if not created:
        obj.ar_name = occ["ar_name"]
        obj.en_name = occ["en_name"]
        obj.power = occ["power"]
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

# --- Activities Data ---
activities_data = [
    {"id": 1, "ar_name": "نشاط 1", "en_name": "Activity 1", "code": "ACT1"},
    {"id": 2, "ar_name": "نشاط 2", "en_name": "Activity 2", "code": "ACT2"},
    {"id": 3, "ar_name": "نشاط 3", "en_name": "Activity 3", "code": "ACT3"},
    {"id": 4, "ar_name": "نشاط 4", "en_name": "Activity 4", "code": "ACT4"},
    {"id": 5, "ar_name": "نشاط 5", "en_name": "Activity 5", "code": "ACT5"},
    {"id": 6, "ar_name": "خدمة الليموزين", "en_name": "Limousine Service", "code": "4921211"},
    {"id": 7, "ar_name": "تأجير السيارات بسائق", "en_name": "Car Rental with Driver", "code": "4922400"},
    {"id": 8, "ar_name": "تأجير السيارات بدون سائق", "en_name": "Car Rental without Driver", "code": "4922901"},
    {"id": 9, "ar_name": "خدمات النقل البري عن طريق التطبيقات الإلكترونية", "en_name": "Land Transport Services via Electronic Applications", "code": "6201002"},
    {"id": 10, "ar_name": "تأجير الشاحنات مع السائق", "en_name": "Truck Rental with Driver", "code": "4923060"},
    {"id": 11, "ar_name": "تأجير الشاحنات بدون سائق", "en_name": "Truck Rental without Driver", "code": "4923091"},
    {"id": 12, "ar_name": "تأجير الآليات والمعدات", "en_name": "Machinery and Equipment Rental", "code": "7730002"},
    {"id": 13, "ar_name": "تأجير معدات وآليات التحميل", "en_name": "Loading Equipment and Machinery Rental", "code": "7730192"},
    {"id": 14, "ar_name": "تأجير معدات وآليات التشييد والبناء", "en_name": "Construction Equipment and Machinery Rental", "code": "4390501"},
    {"id": 15, "ar_name": "تأجير المعدات ذات المحركات", "en_name": "Motorized Equipment Rental", "code": "7730120"},
    {"id": 16, "ar_name": "تأجير الحافلات بالسائق", "en_name": "Bus Rental with Driver", "code": "4922001"},
    {"id": 17, "ar_name": "تأجير الحافلات بدون سائق", "en_name": "Bus Rental without Driver", "code": "4922002"},
    {"id": 18, "ar_name": "استشارات النقل", "en_name": "Transport Consultancy", "code": "7020001"},
    {"id": 19, "ar_name": "نقل الأثاث", "en_name": "Furniture Moving", "code": "4923030"},
    {"id": 20, "ar_name": "نقل السلع المبردة والمجمدة", "en_name": "Refrigerated and Frozen Goods Transport", "code": "4923010"},
    {"id": 21, "ar_name": "نقل المواد الاستهلاكية للعملاء", "en_name": "Consumer Goods Delivery to Clients", "code": "3830092"},
    {"id": 22, "ar_name": "نقل الخضروات والفواكه وتوصيلها وتفريقها وتوصيلها إلى العملاء", "en_name": "Vegetables and Fruits Transport and Distribution to Clients", "code": "4923094"},
    {"id": 23, "ar_name": "نقل المواد العامة بالشاحنات الخفيفة", "en_name": "General Goods Transport with Light Trucks", "code": "3830093"},
    {"id": 24, "ar_name": "النقل الثقيل للبضائع والمعدات", "en_name": "Heavy Goods and Equipment Transport", "code": "4923020"},
    {"id": 25, "ar_name": "نقل الحاويات", "en_name": "Container Transport", "code": "5210141"},
    {"id": 26, "ar_name": "نقل السيارات والمركبات", "en_name": "Car and Vehicle Transport", "code": "4923071"},
    {"id": 27, "ar_name": "خدمة نقل السيارات المعطلة", "en_name": "Disabled Vehicle Transport Service", "code": "4923003"},
    {"id": 28, "ar_name": "نقل المياه", "en_name": "Water Transport", "code": "3600091"},
    {"id": 29, "ar_name": "خدمة نقل مياه الشرب", "en_name": "Drinking Water Transport Service", "code": "3600092"},
    {"id": 30, "ar_name": "خدمة نقل مياه المجاري", "en_name": "Sewage Water Transport Service", "code": "3700091"},
    {"id": 31, "ar_name": "نقل الرمل والدفان والحجر", "en_name": "Sand, Backfill, and Stone Transport", "code": "4923093"},
    {"id": 32, "ar_name": "النقل البري للخامات الأولية", "en_name": "Land Transport of Raw Materials", "code": "3830091"},
    {"id": 33, "ar_name": "نقل النفايات غير الخطرة", "en_name": "Non-Hazardous Waste Transport", "code": "3811091"},
    {"id": 34, "ar_name": "النقل المدرسي الموسمي", "en_name": "Seasonal School Transport", "code": "4922201"},
    {"id": 35, "ar_name": "النقل البري للركاب بالحافلات داخل المدن", "en_name": "Urban Bus Passenger Transport", "code": "4921101"},
    {"id": 36, "ar_name": "نقل الركاب بالحافلات على الخطوط الدولية", "en_name": "International Bus Passenger Transport", "code": "4921121"},
    {"id": 37, "ar_name": "نقل المواشي", "en_name": "Livestock Transport", "code": "4923040"},
    {"id": 38, "ar_name": "النقل البري بين الدول", "en_name": "Intercountry Land Transport", "code": "4921120"},
    {"id": 39, "ar_name": "النقل البري بين المدن", "en_name": "Intercity Land Transport", "code": "4921110"},
    {"id": 40, "ar_name": "توصيل حقائب المسافرين", "en_name": "Passenger Luggage Delivery", "code": "4923095"},
    {"id": 41, "ar_name": "خدمات شحن وتفريق السلع عن طريق البر", "en_name": "Land Goods Loading and Unloading Services", "code": "4923001"},
    {"id": 42, "ar_name": "شحن وتفريغ أمتعة الركاب عن طريق البر", "en_name": "Land Passenger Luggage Loading and Unloading", "code": "4923002"},
    {"id": 43, "ar_name": "توصيل طلبات المنازل", "en_name": "Home Delivery Services", "code": "4923004"},
    {"id": 44, "ar_name": "توصيل الطلبات للمنازل من خلال التطبيقات الإلكترونية", "en_name": "Home Delivery via Electronic Applications", "code": "4923005"},
    {"id": 45, "ar_name": "خدمة الإسعاف التجاري", "en_name": "Commercial Ambulance Service", "code": "4922501"},
    {"id": 46, "ar_name": "تأجير السيارات بسائق لذوي الاحتياجات الخاصة", "en_name": "Car Rental with Driver for Special Needs", "code": "4922902"},
    {"id": 47, "ar_name": "نقل الركاب بخطوط السكك الحديدية بين المدن", "en_name": "Intercity Railway Passenger Transport", "code": "4911020"},
    {"id": 48, "ar_name": "أنشطة أخرى لنقل الركاب بالسكك الحديدية", "en_name": "Other Railway Passenger Transport Activities", "code": "4911091"},
    {"id": 49, "ar_name": "نقل الركاب بخطوط السكك الحديدية داخل المدن", "en_name": "Urban Railway Passenger Transport", "code": "4911010"},
    {"id": 50, "ar_name": "أنشطة أخرى لنقل البضائع بالسكك الحديدية", "en_name": "Other Railway Freight Transport Activities", "code": "4912090"},
    {"id": 51, "ar_name": "نقل البضائع بخطوط السكك الحديدية داخل المدن", "en_name": "Urban Railway Freight Transport", "code": "4912010"},
    {"id": 52, "ar_name": "نقل البضائع بخطوط السكك الحديدية بين المدن", "en_name": "Intercity Railway Freight Transport", "code": "4912020"},
    {"id": 53, "ar_name": "نقل السوائل والغازات السائلة", "en_name": "Liquid and Gas Transport", "code": "4923050"},
    {"id": 54, "ar_name": "نقل البترول ومنتجاته بواسطة ناقلات البترول", "en_name": "Petroleum and Products Transport via Tankers", "code": "4923096"},
    {"id": 55, "ar_name": "نقل المنتجات البترولية عن طريق البر", "en_name": "Land Transport of Petroleum Products", "code": "4923092"},
    {"id": 56, "ar_name": "نقل الركاب بسيارات الأجرة التاكسي", "en_name": "Taxi Passenger Transport", "code": "4922101"},
    {"id": 57, "ar_name": "النقل السياحي بالحافلات", "en_name": "Tourist Bus Transport", "code": "4921001"},
    {"id": 58, "ar_name": "نقل المواد الخطرة", "en_name": "Hazardous Materials Transport", "code": "3812005"},
]

for act in activities_data:
    obj, created = Activity.objects.get_or_create(
        id=act["id"],
        defaults={
            "ar_name": act["ar_name"],
            "en_name": act["en_name"],
            "code": act["code"],
        }
    )
    if not created:
        obj.ar_name = act["ar_name"]
        obj.en_name = act["en_name"]
        obj.code = act["code"]
        obj.save()
    print(f"Activity {obj.en_name} ({'created' if created else 'updated'})") 