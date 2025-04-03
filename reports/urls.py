from django.urls import path

from .views import all_establishment_report, report_index, inspection_report,license_report

urlpatterns = [
    path("report", report_index, name="report_index"),
    path(
        "all-establishment-report/",
        all_establishment_report,
        name="all_establishment_report",
    ),
    path("inspection_report/<int:inspection_id>", inspection_report, name="inspection_report"),
    path("license_report/<int:licence_id>", license_report, name="license_report"),

]
