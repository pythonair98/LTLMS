import logging
from django.urls import path
from .views import (
    add_establishment,
    view_establishment,
    delete_establishment,
    edit_establishment,
    reader,
    query,
    register_list_create,
    register_delete,
    licence_list_create,
    licence_delete,
    view_inspection_assignments,
    delete_assignment,
    edit_assignment,
    update_assignment_status,
    assign_establishment,
    create_inspection,
    dashboard,
    view_inspections,
    archive_inspection,
    view_archive,
    add_establishment_register,
    add_establishment_licence,
    get_inspector_assignments,
    get_inspector_inspections,
    inspect_establishment,
    inspection_delete,
    view_inspection_data,
)

# URL patterns for routing different views in the Django application
urlpatterns = [
    # Dashboard view
    path("summary", dashboard, name="dashboard"),
    # Establishment-related URLs
    path("add_establishment", add_establishment, name="add_establishment"),
    path("view_establishment", view_establishment, name="view_establishment"),
    path(
        "delete_establishment/<int:register_number>",
        delete_establishment,
        name="delete_establishment",
    ),
    path(
        "edit_establishment/<str:rifd>", edit_establishment, name="edit_establishment"
    ),
    # RFID Reader-related URLs
    path("reader", reader, name="reader"),
    path("test", create_inspection, name="test"),
    # API Endpoints
    path("api/query", query, name="query"),
    # Establishment Register-related URLs
    path("registers/", register_list_create, name="register-list"),
    path("registers/delete/<int:pk>/", register_delete, name="register-delete"),
    # Establishment Licence-related URLs
    path("licences", licence_list_create, name="licence-list"),
    path("licences/delete/<int:pk>/", licence_delete, name="licence-delete"),
    # Inspection Assignment URLs
    path("assignments", view_inspection_assignments, name="view_assignments"),
    path("assignments/delete/<int:pk>", delete_assignment, name="delete_assignment"),
    path("assignments/edit/<int:pk>", edit_assignment, name="edit_assignment"),
    path(
        "assignments/update_status/<int:pk>",
        update_assignment_status,
        name="update_assignment_status",
    ),
    # Establishment Assignment
    path("assign-establishment/", assign_establishment, name="assign_establishment"),
    # Inspection-related URLs
    path("inspections", view_inspections, name="view_inspections"),
    path("archived_inspection", view_archive, name="archived_inspection"),
    path(
        "inspections/<int:pk>/archive/", archive_inspection, name="archive_inspection"
    ),
    path("inspections/<int:id>/delete/", inspection_delete, name="inspection_delete"),
    path(
        "inspections/<int:pk>/view/", view_inspection_data, name="view_inspection_data"
    ),
    path(
        "inspect_establishment/<int:id>",
        inspect_establishment,
        name="inspect_establishment",
    ),
    # Additional Establishment Management URLs
    path("register/add/", add_establishment_register, name="add_register"),
    path("add_establishment_licence", add_establishment_licence, name="add_licence"),
    # Inspector-specific URLs
    path(
        "get_inspector_assignments",
        get_inspector_assignments,
        name="get_inspector_assignments",
    ),
    path(
        "get_inspector_inspections",
        get_inspector_inspections,
        name="get_inspector_inspections",
    ),
]
