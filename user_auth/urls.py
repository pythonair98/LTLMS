from .views import (
    profiles_list,
    create_new_user,
    login_view,
    logout_view,
    view_teams,
    team_edit,
    team_delete,
    team_create,
    user_edit,
    user_delete,
    user_deactivate,
    user_activate,
    get_team_members,
)
from django.urls import path

urlpatterns = [
    path("profiles", profiles_list, name="profiles-list"),
    path("new_user", create_new_user, name="register"),
    path("user_edit/<int:id>", user_edit, name="user_edit"),
    path("user_delete/<int:id>", user_delete, name="user_delete"),
    path("user_deactivate/<int:id>", user_deactivate, name="user_deactivate"),
    path("user_activate/<int:id>", user_activate, name="user_activate"),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("teams", view_teams, name="teams"),
    path("team-create", team_create, name="team-create"),
    path("team-edit/<int:id>", team_edit, name="team-edit"),
    path("team-delete/<int:id>", team_delete, name="team-delete"),
    path("get_team_members/<int:id>", get_team_members, name="get_team_members"),
]
