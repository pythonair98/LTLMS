from .views import (
    profiles_list,
    create_user_profile,
    edit_user_profile,
    delete_user_profile,
)
from django.urls import path

urlpatterns = [
    path("profiles/", profiles_list, name="profiles-list"),
    path("create_user", create_user_profile),
    path("edit_user/<int:pk>", edit_user_profile),
    path("delete_user/<int:pk>", delete_user_profile),
]
