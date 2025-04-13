from django.urls import path
from .views import (
    # User profile views
    profiles_list,
    create_new_user,
    user_edit,
    user_delete,
    user_deactivate, 
    user_activate,
    
    # Authentication views
    login_view,
    logout_view,
    
    # Team management views
    view_teams,
    team_create,
    team_edit,
    team_delete,
    get_team_members,
    
    # Email confirmation views
    send_confirmation_email,
    confirm_email
)

urlpatterns = [
    # User profile URLs
    path('profiles/', profiles_list, name='profiles-list'),
    path('profiles/new/', create_new_user, name='register'),
    path('profiles/<int:id>/edit/', user_edit, name='user_edit'),
    path('profiles/<int:id>/delete/', user_delete, name='user_delete'),
    path('profiles/<int:id>/deactivate/', user_deactivate, name='user_deactivate'),
    path('profiles/<int:id>/activate/', user_activate, name='user_activate'),

    # Authentication URLs  
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Team management URLs
    path('teams/', view_teams, name='teams'),
    path('teams/new/', team_create, name='team-create'),
    path('teams/<int:id>/edit/', team_edit, name='team-edit'),
    path('teams/<int:id>/delete/', team_delete, name='team-delete'),
    path('teams/<int:id>/members/', get_team_members, name='get_team_members'),

    # Email confirmation URLs
    path('email/send-confirmation/', send_confirmation_email, name='send_confirmation_email'),
    path('email/confirm/<str:uidb64>/<str:token>/', confirm_email, name='confirm_email'),
]
