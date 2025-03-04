from .views import (
    profiles_list,
    create_user_profile,
    edit_user_profile,
    delete_user_profile,
    register,
    login_view, logout_view,view_teams
)
from django.urls import path

urlpatterns = [
    path("profiles", profiles_list, name="profiles-list"),
    path("create_user", create_user_profile),
    path("new_user", register, name="register"),
    path("edit_user/<int:pk>", edit_user_profile),
    path("delete_user/<int:pk>", delete_user_profile),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("teams", view_teams, name="teams"),
    path("team-create", view_teams, name="team-create"),
    path("team-detail/<int:id>", view_teams, name="team-detail"),
    path("team-edit/<int:id>", view_teams, name="team-edit"),
    path("team-delete/<int:id>", view_teams, name="team-delete"),

]
