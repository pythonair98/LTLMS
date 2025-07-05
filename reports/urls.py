from django.urls import path
from .views import (
    all_establishment_report,
    report_index,
    inspection_report,
    license_report,
    view_exported_report,
    activity_overview,
    activity_codes_report,
    establishment_directory_report,
)

# Define URL patterns for the reports app
urlpatterns = [
    path("report", report_index, name="report_index"),
    path(
        "all-establishment-report/",
        all_establishment_report,
        name="all_establishment_report",
    ),
    path(
        "inspection_report/<int:inspection_id>/",
        inspection_report,
        name="inspection_report",
    ),
    path(
        "license_report/<int:licence_id>/",
        license_report,
        name="license_report",
    ),
    path(
        "exported_report/",
        view_exported_report,
        name="view_exported_report",
    ),
    path('activity-overview/', activity_overview, name='activity_overview'),
    path('activity-codes/', activity_codes_report, name='activity_codes_report'),
    path('establishment-directory/', establishment_directory_report, name='establishment_directory_report'),
]
